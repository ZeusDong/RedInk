import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 12398
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:3000']
    OUTPUT_DIR = 'output'

    _image_providers_config = None
    _text_providers_config = None
    _feishu_providers_config = None

    @classmethod
    def load_image_providers_config(cls):
        if cls._image_providers_config is not None:
            return cls._image_providers_config

        config_path = Path(__file__).parent.parent / 'image_providers.yaml'
        logger.debug(f"加载图片服务商配置: {config_path}")

        if not config_path.exists():
            logger.warning(f"图片配置文件不存在: {config_path}，使用默认配置")
            cls._image_providers_config = {
                'active_provider': 'google_genai',
                'providers': {}
            }
            return cls._image_providers_config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._image_providers_config = yaml.safe_load(f) or {}
            logger.debug(f"图片配置加载成功: {list(cls._image_providers_config.get('providers', {}).keys())}")
        except yaml.YAMLError as e:
            logger.error(f"图片配置文件 YAML 格式错误: {e}")
            raise ValueError(
                f"配置文件格式错误: image_providers.yaml\n"
                f"YAML 解析错误: {e}\n"
                "解决方案：\n"
                "1. 检查 YAML 缩进是否正确（使用空格，不要用Tab）\n"
                "2. 检查引号是否配对\n"
                "3. 使用在线 YAML 验证器检查格式"
            )

        return cls._image_providers_config

    @classmethod
    def load_text_providers_config(cls):
        """加载文本生成服务商配置"""
        if cls._text_providers_config is not None:
            return cls._text_providers_config

        config_path = Path(__file__).parent.parent / 'text_providers.yaml'
        logger.debug(f"加载文本服务商配置: {config_path}")

        if not config_path.exists():
            logger.warning(f"文本配置文件不存在: {config_path}，使用默认配置")
            cls._text_providers_config = {
                'active_provider': 'google_gemini',
                'providers': {}
            }
            return cls._text_providers_config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._text_providers_config = yaml.safe_load(f) or {}
            logger.debug(f"文本配置加载成功: {list(cls._text_providers_config.get('providers', {}).keys())}")
        except yaml.YAMLError as e:
            logger.error(f"文本配置文件 YAML 格式错误: {e}")
            raise ValueError(
                f"配置文件格式错误: text_providers.yaml\n"
                f"YAML 解析错误: {e}\n"
                "解决方案：\n"
                "1. 检查 YAML 缩进是否正确（使用空格，不要用Tab）\n"
                "2. 检查引号是否配对\n"
                "3. 使用在线 YAML 验证器检查格式"
            )

        return cls._text_providers_config

    @classmethod
    def get_active_image_provider(cls):
        config = cls.load_image_providers_config()
        active = config.get('active_provider', 'google_genai')
        logger.debug(f"当前激活的图片服务商: {active}")
        return active

    @classmethod
    def get_image_provider_config(cls, provider_name: str = None):
        config = cls.load_image_providers_config()

        if provider_name is None:
            provider_name = cls.get_active_image_provider()

        logger.info(f"获取图片服务商配置: {provider_name}")

        providers = config.get('providers', {})
        if not providers:
            raise ValueError(
                "未找到任何图片生成服务商配置。\n"
                "解决方案：\n"
                "1. 在系统设置页面添加图片生成服务商\n"
                "2. 或手动编辑 image_providers.yaml 文件\n"
                "3. 确保文件中有 providers 字段"
            )

        if provider_name not in providers:
            available = ', '.join(providers.keys()) if providers else '无'
            logger.error(f"图片服务商 [{provider_name}] 不存在，可用服务商: {available}")
            raise ValueError(
                f"未找到图片生成服务商配置: {provider_name}\n"
                f"可用的服务商: {available}\n"
                "解决方案：\n"
                "1. 在系统设置页面添加该服务商\n"
                "2. 或修改 active_provider 为已存在的服务商\n"
                "3. 检查 image_providers.yaml 文件"
            )

        provider_config = providers[provider_name].copy()

        # 验证必要字段
        if not provider_config.get('api_key'):
            logger.error(f"图片服务商 [{provider_name}] 未配置 API Key")
            raise ValueError(
                f"服务商 {provider_name} 未配置 API Key\n"
                "解决方案：\n"
                "1. 在系统设置页面编辑该服务商，填写 API Key\n"
                "2. 或手动在 image_providers.yaml 中添加 api_key 字段"
            )

        provider_type = provider_config.get('type', provider_name)
        if provider_type in ['openai', 'openai_compatible', 'image_api']:
            if not provider_config.get('base_url'):
                logger.error(f"服务商 [{provider_name}] 类型为 {provider_type}，但未配置 base_url")
                raise ValueError(
                    f"服务商 {provider_name} 未配置 Base URL\n"
                    f"服务商类型 {provider_type} 需要配置 base_url\n"
                    "解决方案：在系统设置页面编辑该服务商，填写 Base URL"
                )

        logger.info(f"图片服务商配置验证通过: {provider_name} (type={provider_type})")
        return provider_config

    @classmethod
    def reload_config(cls):
        """重新加载配置（清除缓存）"""
        logger.info("重新加载所有配置...")
        cls._image_providers_config = None
        cls._text_providers_config = None
        cls._feishu_providers_config = None

    @classmethod
    def load_feishu_providers_config(cls):
        """加载飞书工作区配置"""
        if cls._feishu_providers_config is not None:
            return cls._feishu_providers_config

        config_path = Path(__file__).parent.parent / 'feishu_providers.yaml'
        logger.debug(f"加载飞书工作区配置: {config_path}")

        if not config_path.exists():
            logger.warning(f"飞书配置文件不存在: {config_path}，使用默认配置")
            cls._feishu_providers_config = {
                'active_workspace': 'default',
                'workspaces': {
                    'default': {
                        'name': '默认工作区',
                        'app_id': '',
                        'app_secret': '',
                        'base_url': '',
                        'user_access_token': '',
                        'cache_enabled': True,
                        'cache_ttl': 3600,
                    }
                }
            }
            return cls._feishu_providers_config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cls._feishu_providers_config = yaml.safe_load(f) or {}
            logger.debug(f"飞书配置加载成功: {list(cls._feishu_providers_config.get('workspaces', {}).keys())}")
        except yaml.YAMLError as e:
            logger.error(f"飞书配置文件 YAML 格式错误: {e}")
            raise ValueError(
                f"配置文件格式错误: feishu_providers.yaml\n"
                f"YAML 解析错误: {e}\n"
                "解决方案：\n"
                "1. 检查 YAML 缩进是否正确（使用空格，不要用Tab）\n"
                "2. 检查引号是否配对\n"
                "3. 使用在线 YAML 验证器检查格式"
            )

        return cls._feishu_providers_config

    @classmethod
    def get_active_feishu_workspace(cls):
        """获取当前激活的飞书工作区名称"""
        config = cls.load_feishu_providers_config()
        active = config.get('active_workspace', 'default')
        logger.debug(f"当前激活的飞书工作区: {active}")
        return active

    @classmethod
    def get_feishu_workspace_config(cls, workspace_name: str = None):
        """获取飞书工作区配置"""
        config = cls.load_feishu_providers_config()

        if workspace_name is None:
            workspace_name = cls.get_active_feishu_workspace()

        logger.info(f"获取飞书工作区配置: {workspace_name}")

        workspaces = config.get('workspaces', {})
        if not workspaces:
            raise ValueError(
                "未找到任何飞书工作区配置。\n"
                "解决方案：\n"
                "1. 在系统设置页面添加飞书工作区\n"
                "2. 或手动编辑 feishu_providers.yaml 文件\n"
                "3. 确保文件中有 workspaces 字段"
            )

        if workspace_name not in workspaces:
            available = ', '.join(workspaces.keys()) if workspaces else '无'
            logger.error(f"飞书工作区 [{workspace_name}] 不存在，可用工作区: {available}")
            raise ValueError(
                f"未找到飞书工作区配置: {workspace_name}\n"
                f"可用的工区: {available}\n"
                "解决方案：\n"
                "1. 在系统设置页面添加该工作区\n"
                "2. 或修改 active_workspace 为已存在的工作区\n"
                "3. 检查 feishu_providers.yaml 文件"
            )

        workspace_config = workspaces[workspace_name].copy()

        # 验证必要字段
        if not workspace_config.get('app_id'):
            logger.warning(f"飞书工作区 [{workspace_name}] 未配置 app_id")
        if not workspace_config.get('app_secret'):
            logger.warning(f"飞书工作区 [{workspace_name}] 未配置 app_secret")
        if not workspace_config.get('base_url'):
            logger.warning(f"飞书工作区 [{workspace_name}] 未配置 base_url")

        logger.info(f"飞书工作区配置验证通过: {workspace_name}")
        return workspace_config

    @classmethod
    def save_feishu_providers_config(cls, config: dict) -> None:
        """
        保存飞书工作区配置到文件

        Args:
            config: 完整的飞书配置字典
        """
        config_path = Path(__file__).parent.parent / 'feishu_providers.yaml'

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            # 清除缓存，强制重新加载
            cls._feishu_providers_config = None
            logger.info(f"飞书配置已保存到: {config_path}")

        except Exception as e:
            logger.error(f"保存飞书配置失败: {e}")
            raise ValueError(f"保存飞书配置失败: {e}")

    @classmethod
    def update_feishu_workspace_tokens(cls, workspace_name: str, tokens: dict) -> None:
        """
        Update access token and refresh token for a workspace.

        Args:
            workspace_name: Name of the workspace
            tokens: Dict containing:
                - user_access_token: New access token
                - refresh_token: New refresh token
                - expires_in: Access token expiry in seconds
                - refresh_token_expires_in: Refresh token expiry in seconds
        """
        from datetime import datetime, timedelta

        config = cls.load_feishu_providers_config()

        if workspace_name not in config.get('workspaces', {}):
            raise ValueError(f"Workspace {workspace_name} not found")

        workspace = config['workspaces'][workspace_name]

        # Calculate expiry timestamps
        now = datetime.now()
        access_token_expiry = now + timedelta(seconds=tokens['expires_in'])
        refresh_token_expiry = now + timedelta(seconds=tokens['refresh_token_expires_in'])

        # Update tokens
        workspace['user_access_token'] = tokens['user_access_token']
        workspace['refresh_token'] = tokens['refresh_token']
        workspace['token_expires_at'] = access_token_expiry.isoformat()
        workspace['refresh_token_expires_at'] = refresh_token_expiry.isoformat()

        # Save updated config
        cls.save_feishu_providers_config(config)
        logger.info(f"Updated tokens for workspace {workspace_name}, expires at {access_token_expiry}")
