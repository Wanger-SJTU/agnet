# Arxiv Agent - 配置驱动的多厂商大模型代理

一个支持多厂商大模型API的智能代理，支持OpenAI、百度文心一言、阿里通义千问、DeepSeek等主流大模型。

## 新特性：配置驱动

现在Agent的URL和API密钥都从配置文件读取，支持灵活的配置管理。

### 主要特性

- ✅ **配置驱动**: 所有API配置从配置文件读取
- ✅ **多厂商支持**: OpenAI、百度文心一言、阿里通义千问、DeepSeek
- ✅ **灵活配置**: 支持YAML和JSON格式配置文件
- ✅ **参数覆盖**: 可以通过代码参数覆盖配置文件设置
- ✅ **自动配置**: 自动查找和创建默认配置文件

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `config/config.yaml` 文件，设置各厂商的API密钥：

```yaml
# 大模型API配置
providers:
  openai:
    api_key: "your-openai-api-key"
    base_url: "https://api.openai.com/v1"
    default_model: "gpt-3.5-turbo"
    
  baidu:
    api_key: "your-baidu-api-key"
    secret_key: "your-baidu-secret-key"
    base_url: "https://aip.baidubce.com"
    default_model: "ERNIE-Bot-turbo"
    
  alibaba:
    api_key: "your-alibaba-api-key"
    base_url: "https://dashscope.aliyuncs.com/api/v1"
    default_model: "qwen-turbo"
    
  deepseek:
    api_key: "your-deepseek-api-key"
    base_url: "https://api.deepseek.com/v1"
    default_model: "deepseek-chat"

# 通用配置
settings:
  timeout: 60
  max_history_length: 20
  default_temperature: 0.7
  default_max_tokens: 1000
```

### 3. 使用Agent

#### 方式1: 使用配置文件（推荐）

```python
from src.agent import LLMAgent

# 从配置文件读取配置
agent = LLMAgent("openai")
response = agent.ask("你好，请介绍一下你自己")
print(response)
```

#### 方式2: 覆盖配置文件参数

```python
# 覆盖配置文件中的API密钥
agent = LLMAgent("openai", api_key="your-api-key")
```

#### 方式3: 使用自定义配置文件路径

```python
# 使用自定义配置文件
agent = LLMAgent("openai", config_path="path/to/your/config.yaml")
```

### 4. 运行演示

```bash
python demo_config_agent.py
```

## 配置说明

### 支持的提供商

- `openai`: OpenAI GPT系列模型
- `baidu`: 百度文心一言系列模型  
- `alibaba`: 阿里通义千问系列模型
- `deepseek`: DeepSeek系列模型

### 配置项说明

每个提供商支持以下配置项：

- `api_key`: API密钥（必需）
- `base_url`: API基础URL（可选，有默认值）
- `default_model`: 默认模型（可选，有默认值）

通用设置：

- `timeout`: 请求超时时间（秒）
- `max_history_length`: 最大对话历史长度
- `default_temperature`: 默认温度参数
- `default_max_tokens`: 默认最大token数

## 高级用法

### 对话历史管理

```python
agent = LLMAgent("openai", api_key="your-key")

# 设置系统提示词
agent.set_system_prompt("你是一个专业的AI助手")

# 多轮对话
response1 = agent.ask("什么是机器学习？")
response2 = agent.ask("能详细解释一下监督学习吗？")

# 查看对话历史
history = agent.get_history()
print(f"对话历史: {len(history)} 条记录")

# 清空历史
agent.clear_history()
```

### 模型参数调整

```python
response = agent.ask(
    "请写一首关于AI的诗",
    model="gpt-4",
    temperature=0.8,
    max_tokens=500
)
```

## 测试

运行测试套件：

```bash
python tests/test_agent.py
```

## 故障排除

### 常见问题

1. **导入错误**: 确保Python路径包含项目根目录
2. **配置错误**: 检查配置文件格式和路径
3. **API错误**: 验证API密钥是否正确，网络是否通畅

### 依赖要求

- Python 3.7+
- requests >= 2.25.0
- PyYAML >= 6.0

## 许可证

MIT License
