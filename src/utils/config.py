"""
Configuration Management
Loads and manages application configuration
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for AI Coding Assistant"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config' / 'default.yaml'
        
        self.config = self._load_config(config_path)
        
        # Override with environment variables
        self._override_with_env()
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _override_with_env(self):
        """Override config values with environment variables"""
        # iFlow API settings
        if 'IFLOW_API_KEY' in os.environ:
            self.config.setdefault('ai', {})['api_key'] = os.environ['IFLOW_API_KEY']
        
        # GitHub settings
        if 'GITHUB_TOKEN' in os.environ:
            self.config.setdefault('github', {})['token'] = os.environ['GITHUB_TOKEN']
        
        if 'GITHUB_REPOSITORY' in os.environ:
            self.config.setdefault('github', {})['repository'] = os.environ['GITHUB_REPOSITORY']
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def iflow_api_key(self) -> str:
        """Get iFlow API key"""
        return self.get('ai.api_key') or os.environ.get('IFLOW_API_KEY', '')
    
    @property
    def github_token(self) -> str:
        """Get GitHub token"""
        return self.get('github.token') or os.environ.get('GITHUB_TOKEN', '')
    
    @property
    def github_repository(self) -> str:
        """Get GitHub repository"""
        return self.get('github.repository') or os.environ.get('GITHUB_REPOSITORY', '')