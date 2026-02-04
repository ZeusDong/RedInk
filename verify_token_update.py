"""Quick verification script for token update functionality"""
import sys
sys.path.insert(0, '.')

from backend.config import Config

# Check if the method exists
if hasattr(Config, 'update_feishu_workspace_tokens'):
    print("SUCCESS: update_feishu_workspace_tokens method exists on Config class")
    sys.exit(0)
else:
    print("FAILED: update_feishu_workspace_tokens method not found")
    print("Available methods:", [m for m in dir(Config) if not m.startswith('_')])
    sys.exit(1)
