"""
测试agent类的功能
"""

import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import LLMAgent


def test_agent_initialization():
    """测试agent初始化"""
    print("=== 测试Agent初始化 ===")
    
    try:
        # 测试OpenAI代理初始化（使用覆盖参数）
        openai_agent = LLMAgent("openai", api_key="test-key")
        print("✓ OpenAI代理初始化成功")
        
        # 测试百度代理初始化（使用覆盖参数）
        baidu_agent = LLMAgent("baidu", api_key="test-key", secret_key="test-secret")
        print("✓ 百度文心一言代理初始化成功")
        
        # 测试阿里代理初始化（使用覆盖参数）
        alibaba_agent = LLMAgent("alibaba", api_key="test-key")
        print("✓ 阿里通义千问代理初始化成功")
        
        # 测试DeepSeek代理初始化（使用覆盖参数）
        deepseek_agent = LLMAgent("deepseek", api_key="test-key")
        print("✓ DeepSeek代理初始化成功")
        
        # 测试不支持的提供商
        try:
            invalid_agent = LLMAgent("unknown", api_key="test")
            print("✗ 不支持的提供商应该抛出异常")
        except ValueError as e:
            print(f"✓ 不支持的提供商正确抛出异常: {e}")
        
        # 测试缺少API密钥的情况
        try:
            no_key_agent = LLMAgent("openai")  # 没有提供API密钥
            print("✗ 缺少API密钥应该抛出异常")
        except ValueError as e:
            print(f"✓ 缺少API密钥正确抛出异常: {e}")
            
    except Exception as e:
        print(f"✗ 初始化测试失败: {e}")


def test_agent_methods():
    """测试agent的各种方法"""
    print("\n=== 测试Agent方法 ===")
    
    # 使用模拟配置
    agent = LLMAgent("openai", api_key="test-key")
    
    try:
        # 测试获取模型列表
        models = agent.get_available_models()
        print(f"✓ 获取模型列表成功: {len(models)} 个模型")
        
        # 测试设置系统提示词
        agent.set_system_prompt("你是一个有用的助手")
        print("✓ 设置系统提示词成功")
        
        # 测试清空历史
        agent.clear_history()
        print("✓ 清空对话历史成功")
        
        # 测试获取历史
        history = agent.get_history()
        print(f"✓ 获取对话历史成功: {len(history)} 条记录")
        
    except Exception as e:
        print(f"✗ 方法测试失败: {e}")


def test_ask_method():
    """测试提问方法（模拟响应）"""
    print("\n=== 测试提问方法 ===")
    
    # 创建一个模拟的agent来测试ask方法的结构
    class MockAgent:
        def __init__(self):
            self.conversation_history = []
        
        def ask(self, question, **kwargs):
            # 模拟响应
            return f"这是对问题 '{question}' 的模拟回答"
        
        def get_available_models(self):
            return ["mock-model-1", "mock-model-2"]
    
    mock_agent = MockAgent()
    
    try:
        # 测试提问
        response = mock_agent.ask("你好")
        print(f"✓ 提问方法调用成功")
        print(f"  问题: '你好'")
        print(f"  模拟回答: '{response}'")
        
        # 测试带参数的提问
        response = mock_agent.ask("今天天气怎么样？", temperature=0.8, max_tokens=500)
        print(f"✓ 带参数提问成功")
        
    except Exception as e:
        print(f"✗ 提问方法测试失败: {e}")


def test_conversation_history():
    """测试对话历史功能"""
    print("\n=== 测试对话历史 ===")
    
    # 创建一个模拟agent来测试对话历史
    class MockHistoryAgent:
        def __init__(self):
            self.conversation_history = []
        
        def ask(self, question, **kwargs):
            # 模拟回答
            answer = f"回答: {question}"
            
            # 更新对话历史
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            # 限制历史长度
            if len(self.conversation_history) > 4:  # 保留最近2轮对话
                self.conversation_history = self.conversation_history[-4:]
            
            return answer
        
        def get_history(self):
            return self.conversation_history.copy()
        
        def clear_history(self):
            self.conversation_history = []
    
    mock_agent = MockHistoryAgent()
    
    try:
        # 进行多轮对话
        mock_agent.ask("第一轮对话")
        mock_agent.ask("第二轮对话")
        mock_agent.ask("第三轮对话")
        
        history = mock_agent.get_history()
        print(f"✓ 对话历史记录成功: {len(history)} 条记录")
        for i, msg in enumerate(history):
            print(f"  {i+1}. {msg['role']}: {msg['content']}")
        
        # 测试清空历史
        mock_agent.clear_history()
        history_after_clear = mock_agent.get_history()
        print(f"✓ 清空历史成功: {len(history_after_clear)} 条记录")
        
    except Exception as e:
        print(f"✗ 对话历史测试失败: {e}")


def main():
    """主测试函数"""
    print("开始测试Agent类功能...\n")
    
    # 运行所有测试
    test_agent_initialization()
    test_agent_methods()
    test_ask_method()
    test_conversation_history()
    
    print("\n=== 测试总结 ===")
    print("所有基础功能测试完成！")
    print("\n注意: 实际API调用需要配置真实的API密钥")
    print("要使用真实API，请:")
    print("1. 获取相应厂商的API密钥")
    print("2. 在agent.py的示例部分替换为真实密钥")
    print("3. 取消注释相应的测试代码")


if __name__ == "__main__":
    main()
