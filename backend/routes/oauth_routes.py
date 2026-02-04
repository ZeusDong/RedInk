"""
OAuth authorization routes for Feishu integration.

This module handles the OAuth 2.0 authorization flow for obtaining
user_access_token and refresh_token from Feishu.
"""
import logging
import secrets
import json
from flask import Blueprint, request, jsonify, redirect, render_template_string
from backend.config import Config

logger = logging.getLogger(__name__)

# Store state parameters for CSRF protection (in production, use Redis/database)
# Format: {state: {"workspace": workspace_name, "frontend_origin": origin}}
_oauth_states = {}


def create_oauth_blueprint():
    """Create OAuth routes blueprint"""
    oauth_bp = Blueprint('oauth', __name__)

    @oauth_bp.route('/oauth/authorize', methods=['GET'])
    def authorize():
        """
        Initiate OAuth authorization flow.

        Query parameters:
        - workspace: Workspace name to save tokens to
        - frontend_origin: Frontend origin (e.g., http://localhost:5173) for postMessage callback

        Redirects user to Feishu authorization page.
        """
        workspace = request.args.get('workspace', 'default')
        frontend_origin = request.args.get('frontend_origin', '')

        if not frontend_origin:
            return jsonify({"error": "frontend_origin is required"}), 400

        try:
            # Get workspace config
            workspace_config = Config.get_feishu_workspace_config(workspace)
            app_id = workspace_config.get('app_id')

            if not app_id:
                return jsonify({"error": "app_id not configured for workspace"}), 400

            # Build the callback URL (backend's callback endpoint)
            # Get the current request's host (protocol + host)
            scheme = request.scheme
            host = request.host
            callback_url = f"{scheme}://{host}/api/oauth/callback"

            # Generate state for CSRF protection
            state = secrets.token_urlsafe(16)
            # Store both workspace, frontend_origin, and callback_url in state
            _oauth_states[state] = {
                "workspace": workspace,
                "frontend_origin": frontend_origin,
                "callback_url": callback_url
            }

            # Build authorization URL with offline_access scope
            auth_url = (
                f"https://accounts.feishu.cn/open-apis/authen/v1/authorize"
                f"?client_id={app_id}"
                f"&response_type=code"
                f"&redirect_uri={callback_url}"
                f"&scope=bitable:app:readonly offline_access"
                f"&state={state}"
            )

            logger.info(f"Initiating OAuth flow for workspace: {workspace}, callback: {callback_url}")
            return redirect(auth_url)

        except Exception as e:
            logger.error(f"OAuth authorize error: {e}")
            return jsonify({"error": str(e)}), 500

    @oauth_bp.route('/oauth/callback', methods=['GET'])
    def callback():
        """
        Handle OAuth callback from Feishu.

        Query parameters:
        - code: Authorization code from Feishu
        - state: State parameter for CSRF validation
        - error: Error code if authorization failed

        Exchanges code for access_token and refresh_token.
        Notifies frontend via postMessage.
        """
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')

        # Validate state and get workspace info
        if state not in _oauth_states:
            return render_template_string("""
                <html><head><title>授权失败</title></head>
                <body><h1>授权失败</h1><p>无效的 state 参数</p><script>window.close();</script></body></html>
            """), 400

        state_data = _oauth_states.pop(state)
        workspace = state_data["workspace"]
        frontend_origin = state_data["frontend_origin"]
        callback_url = state_data["callback_url"]

        # Handle authorization denial
        if error == 'access_denied':
            return render_template_string(f"""
                <html>
                <head><title>授权失败</title></head>
                <body>
                    <h1>授权被拒绝</h1>
                    <p>您拒绝了飞书授权请求。如需使用此功能，请重新授权。</p>
                    <script>
                    if (window.opener) {{
                        window.opener.postMessage({{type: 'feishu:oauth:error', error: 'access_denied'}}, '{frontend_origin}');
                    }}
                    window.close();
                    </script>
                </body>
                </html>
            """), 200

        if not code:
            return render_template_string(f"""
                <html><head><title>授权失败</title></head>
                <body><h1>授权失败</h1><p>缺少授权码</p>
                <script>
                if (window.opener) {{
                    window.opener.postMessage({{type: 'feishu:oauth:error', error: 'missing_code'}}, '{frontend_origin}');
                }}
                window.close();
                </script></body></html>
            """), 400

        try:
            # Get workspace config
            workspace_config = Config.get_feishu_workspace_config(workspace)
            app_id = workspace_config.get('app_id')
            app_secret = workspace_config.get('app_secret')

            # Exchange code for tokens
            import requests
            url = "https://open.feishu.cn/open-apis/authen/v2/oauth/token"
            payload = {
                "grant_type": "authorization_code",
                "client_id": app_id,
                "client_secret": app_secret,
                "code": code,
                "redirect_uri": callback_url,  # Must match the authorize request
            }
            headers = {"Content-Type": "application/json; charset=utf-8"}

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("code", 0) != 0:
                error_msg = result.get("error", "unknown error")
                logger.error(f"Token exchange failed: {error_msg}")
                return render_template_string(f"""
                    <html>
                    <head><title>授权失败</title></head>
                    <body>
                        <h1>授权失败</h1>
                        <p>错误: {error_msg}</p>
                        <script>
                        if (window.opener) {{
                            window.opener.postMessage({{type: 'feishu:oauth:error', error: {json.dumps(error_msg)}}}, '{frontend_origin}');
                        }}
                        window.close();
                        </script>
                    </body>
                    </html>
                """), 400

            # Extract tokens
            access_token = result.get("access_token")
            refresh_token = result.get("refresh_token")
            expires_in = result.get("expires_in", 7200)
            refresh_expires_in = result.get("refresh_token_expires_in", 604800)

            if not access_token:
                return render_template_string(f"""
                    <html>
                    <head><title>授权失败</title></head>
                    <body>
                        <h1>授权失败</h1>
                        <p>未收到访问令牌</p>
                        <script>
                        if (window.opener) {{
                            window.opener.postMessage({{type: 'feishu:oauth:error', error: 'no_access_token'}}, '{frontend_origin}');
                        }}
                        window.close();
                        </script>
                    </body>
                    </html>
                """), 400

            if not refresh_token:
                logger.warning("No refresh_token returned - offline_access permission may be missing")

            # Save tokens to config
            Config.update_feishu_workspace_tokens(workspace, {
                'user_access_token': access_token,
                'refresh_token': refresh_token or '',
                'expires_in': expires_in,
                'refresh_token_expires_in': refresh_expires_in,
            })

            logger.info(f"Successfully obtained tokens for workspace: {workspace}")

            return render_template_string(f"""
                <html>
                <head><title>授权成功</title></head>
                <body>
                    <h1>授权成功！</h1>
                    <p>飞书授权已完成，您可以关闭此窗口返回应用。</p>
                    <script>
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'feishu:oauth:success',
                            workspace: '{workspace}',
                            hasRefreshToken: {str(refresh_token is not None).lower()}
                        }}, '{frontend_origin}');
                    }}
                    window.close();
                    </script>
                </body>
                </html>
            """), 200

        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            return render_template_string(f"""
                <html>
                <head><title>授权失败</title></head>
                <body>
                    <h1>授权失败</h1>
                    <p>错误: {str(e)}</p>
                    <script>
                    if (window.opener) {{
                        window.opener.postMessage({{type: 'feishu:oauth:error', error: {json.dumps(str(e))}}}, '{frontend_origin}');
                    }}
                    window.close();
                    </script>
                </body>
                </html>
            """), 500

    return oauth_bp
