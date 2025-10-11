"""
配置加载器 - 从配置文件读取大模型API配置
支持YAML和JSON格式配置文件
"""

import os
import yaml
import json
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，如果为None则自动查找
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
    
    def _find_config_file(self) -> str:
        """查找配置文件"""
        # 可能的配置文件路径
        possible_paths = [
            "config/config.yaml",
            "config/config.yml", 
            "config/config.json",
            "config.yaml",
            "config.yml",
            "config.json",
            "../config/config.yaml",
            "../config/config.yml",
            "../config/config.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 如果没有找到配置文件，创建默认配置
        default_config_path = "config/config.yaml"
        os.makedirs(os.path.dirname(default_config_path), exist_ok=True)
        
        default_config = {
            "providers": {
                "openai": {
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "default_model": "gpt-3.5-turbo"
                },
                "baidu": {
                    "api_key": "",
                    "secret_key": "",
                    "base_url": "https://aip.baidubce.com",
                    "default_model": "ERNIE-Bot-turbo"
                },
                "alibaba": {
                    "api_key": "",
                    "base_url": "https://dashscope.aliyuncs.com/api/v1",
                    "default_model": "qwen-turbo"
                },
                "deepseek": {
                    "api_key": "",
                    "base_url": "https://api.deepseek.com/v1",
                    "default_model": "deepseek-chat"
                }
            },
            "settings": {
                "timeout": 60,
                "max_history_length": 20,
                "default_temperature": 0.7,
                "default_max_tokens": 1000
            }
        }
        
        with open(default_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"创建默认配置文件: {default_config_path}")
        return default_config_path
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.json'):
                    return json.load(f)
                else:  # YAML文件
                    return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"加载配置文件失败: {str(e)}")
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        获取指定提供商的配置
        
        Args:
            provider: 提供商名称 (openai, baidu, alibaba, deepseek)
            
        Returns:
            Dict: 提供商配置
        """
        providers = self.config.get("providers", {})
        if provider not in providers:
            raise ValueError(f"不支持的提供商: {provider}")
        
        return providers[provider]
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        获取通用设置
        
        Args:
            key: 设置键名
            default: 默认值
            
        Returns:
            Any: 设置值
        """
        return self.config.get("settings", {}).get(key, default)
    
    def get_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """获取所有提供商的配置"""
        return self.config.get("providers", {})
    
    def update_provider_config(self, provider: str, config: Dict[str, Any]):
        """
        更新提供商配置
        
        Args:
            provider: 提供商名称
            config: 新的配置
        """
        if "providers" not in self.config:
            self.config["providers"] = {}
        
        self.config["providers"][provider] = config
        self._save_config()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.endswith('.json'):
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            raise Exception(f"保存配置文件失败: {str(e)}")


# 全局配置加载器实例
_config_loader = None


def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """
    获取配置加载器实例（单例模式）
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigLoader: 配置加载器实例
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader


def get_provider_config(provider: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    快速获取提供商配置
    
    Args:
        provider: 提供商名称
        config_path: 配置文件路径
        
    Returns:
        Dict: 提供商配置
    """
    loader = get_config_loader(config_path)
    return loader.get_provider_config(provider)


def get_setting(key: str, default: Any = None, config_path: Optional[str] = None) -> Any:
    """
    快速获取通用设置
    
    Args:
        key: 设置键名
        default: 默认值
        config_path: 配置文件路径
        
    Returns:
        Any: 设置值
    """
    loader = get_config_loader(config_path)
    return loader.get_setting(key, default)
