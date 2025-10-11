"""
Agent类 - 支持多厂商大模型API的智能代理
支持OpenAI、百度文心一言、阿里通义千问、DeepSeek等主流大模型
"""

import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import time
from openai import OpenAI
from .config_loader import get_provider_config, get_setting


class BaseLLMProvider(ABC):
    """大模型提供商基类"""
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        """聊天补全接口"""
        pass
    
    @abstractmethod
    def get_model_list(self) -> List[str]:
        """获取支持的模型列表"""
        pass

class AlibabaTongyiClient(BaseLLMProvider):
    """阿里通义千问API客户端"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            )
    
    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
                # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
                extra_body={"enable_thinking": False},
            )
        return completion
    
    def get_model_list(self) -> List[str]:
        """获取通义千问支持的模型列表"""
        return [
            "qwen-turbo", "qwen-plus", "qwen-max", "qwen-vl-plus",
            "qwen-audio-turbo", "qwen2-7b-instruct"
        ]


class DeepSeekClient(BaseLLMProvider):
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        """DeepSeek聊天补全"""
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": kwargs.get("model", "deepseek-chat"),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "stream": False
        }
        
        # 添加可选参数
        optional_params = ["top_p", "frequency_penalty", "presence_penalty"]
        for param in optional_params:
            if param in kwargs:
                data[param] = kwargs[param]
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"DeepSeek API请求失败: {str(e)}"}
    
    def get_model_list(self) -> List[str]:
        """获取DeepSeek支持的模型列表"""
        return [
            "deepseek-chat", "deepseek-coder", "deepseek-reasoner",
            "deepseek-math", "deepseek-v2", "deepseek-v2-lite"
        ]


class LLMAgent:
    """智能代理类 - 支持多厂商大模型"""
    
    def __init__(self, provider: str = "openai", config_path: Optional[str] = None, **override_config):
        """
        初始化代理
        
        Args:
            provider: 大模型提供商 (openai, baidu, alibaba, deepseek)
            config_path: 配置文件路径，如果为None则自动查找
            **override_config: 覆盖配置文件的参数
        """
        self.provider_name = provider.lower()
        self.config_path = config_path
        self.llm_client = self._init_provider(provider, config_path, override_config)
        self.conversation_history = []
        self.max_history_length = get_setting("max_history_length", 20, config_path)
    
    def _init_provider(self, provider: str, config_path: Optional[str], override_config: Dict) -> BaseLLMProvider:
        """初始化大模型提供商"""
        provider_map = {
            "alibaba": AlibabaTongyiClient,
            "deepseek": DeepSeekClient
        }
        
        if provider not in provider_map:
            raise ValueError(f"不支持的提供商: {provider}。支持的提供商: {list(provider_map.keys())}")
        
        provider_class = provider_map[provider]
        
        # 从配置文件读取配置
        try:
            config = get_provider_config(provider, config_path)
        except Exception as e:
            raise ValueError(f"读取提供商配置失败: {str(e)}")
        
        # 使用覆盖配置更新
        config.update(override_config)
        
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("API密钥未配置，请在配置文件中设置或通过参数传递")
        base_url = config.get("base_url", None)
        if not base_url:
            raise ValueError("base_url 未配置，请在配置文件中设置或通过参数传递")
        
        return provider_class(api_key=api_key, base_url=base_url)
    
    
    def ask(self, question: str, **kwargs) -> str:
        # 构建消息
        messages = [{"role": "user", 
                     "content": f"你是一个学术助手，后面的对话将围绕着以下论文内容进行。请你作出专业的回答，不要出现第一人称，当涉及到分点回答时，鼓励你以markdown格式输出。论文中的数学公式可能无法保留原始格式，请你尽力理解它们，并在需要输出数学公式的时候以latex格式输出。 {question}"}]
        # 添加对话历史（如果存在）
        if self.conversation_history:
            messages = self.conversation_history + messages
        
        # 调用大模型
        response = self.llm_client.chat_completion(messages, **kwargs)
        
        # 处理响应
        if "error" in response:
            return f"错误: {response['error']}"
        
        # 提取回答内容（不同提供商的响应格式不同）
        answer = self._extract_answer(response)
        
        # 更新对话历史
        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": answer})
        
        # 限制对话历史长度
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
        
        return answer
    
    def _extract_answer(self, response: Dict) -> str:
        """从不同提供商的响应中提取回答内容"""
        if self.provider_name == "alibaba":
            return json.loads(response.model_dump_json())['choices'][0]['message']['content']
        elif self.provider_name == "deepseek":
            return response["choices"][0]["message"]["content"]
        else:
            return str(response)
    
    def get_available_models(self) -> List[str]:
        """获取当前提供商支持的模型列表"""
        return self.llm_client.get_model_list()
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        # 如果有对话历史且第一条是系统消息，则更新它
        if self.conversation_history and self.conversation_history[0].get("role") == "system":
            self.conversation_history[0]["content"] = prompt
        else:
            # 否则在开头插入系统消息
            self.conversation_history.insert(0, {"role": "system", "content": prompt})


# 使用示例
if __name__ == "__main__":
    print("=== 配置驱动的Agent使用示例 ===")
    
    try:
        # 方式1: 使用配置文件（推荐）- 需要提供API密钥
        print("\n1. 使用配置文件创建代理:")
        openai_agent = LLMAgent("openai", api_key="test-key")
        print("✓ OpenAI代理创建成功（从配置文件读取配置）")
        
        # 查看支持的模型
        print(f"OpenAI支持的模型: {openai_agent.get_available_models()}")
        
        # 方式2: 覆盖配置文件中的特定参数
        print("\n2. 覆盖配置文件参数创建代理:")
        deepseek_agent = LLMAgent("deepseek", api_key="test-key")
        print("✓ DeepSeek代理创建成功（使用覆盖参数）")
        
        # 方式3: 使用自定义配置文件路径
        print("\n3. 使用自定义配置文件路径:")
        custom_agent = LLMAgent("openai", config_path="config/config.yaml", api_key="test-key")
        print("✓ 自定义配置代理创建成功")
        
        print("\n=== 配置说明 ===")
        print("1. 默认配置文件路径: config/config.yaml")
        print("2. 请在配置文件中设置各厂商的API密钥")
        print("3. 可以通过参数覆盖配置文件中的设置")
        print("4. 支持YAML和JSON格式配置文件")
        
    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        print("\n请确保:")
        print("1. 配置文件 config/config.yaml 存在")
        print("2. 在配置文件中设置了必要的API密钥")
        print("3. 安装了必要的依赖: pip install pyyaml requests")
