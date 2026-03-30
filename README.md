# 智扫通机器人智能客服 🤖

> 基于 LangChain ReAct Agent + RAG + Streamlit 的扫地机器人智能客服系统
>
<img width="1280" height="660" alt="示例1" src="https://github.com/user-attachments/assets/41fb5a9a-b43f-4171-9dec-f16637adb39d" />

---

# 使用必看

请务必安装好相关配置环境，其中 `config/agent.yml` 文件中的 `gaodekey` 需要改为实际申请的高德 Key，同时根据网络环境在 `config/rag.yml` 中选择合适的 `api_region`（`domestic` 或 `international`）。

---

## 📖 项目简介

**智扫通机器人智能客服**是一款面向扫地机器人/扫拖一体机器人用户的 AI 智能体应用。系统以 Streamlit 构建轻量级前端网页，后端基于 LangChain 搭建 ReAct（Reasoning + Acting）Agent，整合以下核心能力：

- **RAG 增强检索**：将产品手册、常见问题、维护指南等文档向量化存储，AI 回答时优先检索知识库，确保答案准确可靠。
- **高德 MCP 服务**：调用高德地图 API 实时获取用户定位与天气信息。
- **总结汇报模式**：中间件通过识别特定意图，动态切换系统提示词，自动生成使用情况报告（Markdown 格式）。
- **多轮工具调用**：Agent 可自主规划并多轮调用所配备的工具，直至满足用户需求。
- **流式响应**：最终结果在网页端以逐字流式方式呈现，提升交互体验。
- **完善的日志与历史**：配备结构化日志（文件 + 控制台）与对话历史记录。
- **短期记忆**：每轮对话完整保留会话历史，Agent 可感知上下文，支持多轮连续交互。
- **双区域 API 支持**：模型工厂支持国内版 DashScope 原生调用与国际版（新加坡）OpenAI 兼容端双模式，按需切换，无需改动业务代码。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **LLM（国内版）** | 阿里云通义千问 `qwen3-max`（通过 `ChatTongyi`） |
| **LLM（国际版）** | 阿里云 DashScope 新加坡节点 OpenAI 兼容端（通过 `ChatOpenAI`） |
| **Embedding（国内版）** | 阿里云 DashScope `text-embedding-v4`（原生 SDK） |
| **Embedding（国际版）** | 阿里云 DashScope 新加坡节点兼容端（OpenAI 客户端封装） |
| **向量数据库** | Chroma（本地持久化） |
| **Agent 框架** | LangChain ReAct Agent + LangGraph |
| **前端** | Streamlit Web 界面，支持对话历史 |
| **外部服务** | 高德地图 REST API（天气、IP 定位） |
| **短期记忆** | `st.session_state` 维护完整对话历史，每轮请求携带全部上下文传入 Agent |
| **动态提示词** | 中间件根据上下文信号量自动切换 System Prompt |
| **去重机制** | MD5 哈希追踪已处理文档，避免重复入库 |
| **日志** | 按天分文件，同时输出到控制台与文件 |

---

## 🏗 系统架构

```
┌──────────────────────────────────────────────┐
│          Streamlit 前端 (app.py)              │
│  - 对话历史  - 流式显示  - 会话状态管理        │
└──────────────────────┬───────────────────────┘
                       │
┌──────────────────────▼───────────────────────┐
│        ReAct Agent (agent/react_agent.py)     │
│  ┌─────────────────────────────────────────┐ │
│  │  中间件层 (middleware.py)                │ │
│  │  ├─ monitor_tool   工具调用监控与日志    │ │
│  │  ├─ log_before_model  模型调用前日志     │ │
│  │  └─ report_prompt_switch 动态提示词切换  │ │
│  └─────────────────────────────────────────┘ │
│  工具集：rag_summarize / get_weather /        │
│         get_user_location / get_user_id /     │
│         get_current_month / fetch_external_data│
│         fill_context_for_report               │
└──┬──────────────┬───────────────┬────────────┘
   │              │               │
   ▼              ▼               ▼
┌──────────┐ ┌─────────────┐ ┌────────────────┐
│ RAG 服务 │ │  高德 API   │ │  外部 CSV 数据 │
│(rag/)    │ │ 天气 / 定位 │ │ data/external/ │
└────┬─────┘ └─────────────┘ └────────────────┘
     │
┌────▼─────────────────────────┐
│  Chroma 向量数据库 (chroma_db/)│
│  知识库文档 (data/)           │
│  ├─ PDF / TXT 文档            │
│  └─ chunk_size=200, k=3       │
└─────────────┬────────────────┘
              │
┌─────────────▼────────────────────────────────┐
│         模型工厂 (model/factory.py)           │
│  ┌──────────────────┬─────────────────────┐  │
│  │ api_region=domestic│api_region=international│
│  │ ChatTongyi（原生）  │ ChatOpenAI（兼容端）   │
│  │ DashScopeEmbeddings│ OpenAI Client 封装    │
│  └──────────────────┴─────────────────────┘  │
│  国际端点：dashscope-intl.aliyuncs.com        │
└──────────────────────────────────────────────┘
```

---

## 📂 目录结构

```
LangChain-ReAct-Agent/
├── app.py                        # Streamlit 前端入口
├── agent/
│   ├── react_agent.py            # ReAct Agent 核心逻辑
│   └── tools/
│       ├── agent_tools.py        # 工具函数定义
│       └── middleware.py         # Agent 中间件
├── rag/
│   ├── rag_service.py            # RAG 检索摘要服务
│   └── vector_store.py           # Chroma 向量库管理
├── model/
│   └── factory.py                # 模型工厂（LLM + Embedding，支持双区域）
├── utils/
│   ├── config_handler.py         # YAML 配置加载器
│   ├── logger_handler.py         # 日志工具
│   ├── prompt_loader.py          # 提示词加载器
│   ├── file_handler.py           # 文档加载（PDF/TXT）
│   └── path_tool.py              # 路径工具
├── config/
│   ├── agent.yml                 # Agent 配置（高德 API Key 等）
│   ├── rag.yml                   # 模型配置（含 api_region 区域选择）
│   ├── chroma.yml                # 向量库配置
│   └── prompts.yml               # 提示词文件路径
├── prompts/
│   ├── main_prompt.txt           # 主 ReAct 提示词
│   ├── rag_summarize.txt         # RAG 摘要提示词
│   └── report_prompt.txt         # 报告生成提示词
├── data/
│   ├── 扫地机器人100问.pdf
│   ├── 扫地机器人100问2.txt
│   ├── 扫拖一体机器人100问.txt
│   ├── 故障排除.txt
│   ├── 维护保养.txt
│   ├── 选购指南.txt
│   └── external/
│       └── records.csv           # 用户使用记录（外部数据）
├── chroma_db/                    # Chroma 持久化目录（自动生成）
├── logs/                         # 日志文件目录（自动生成）
└── md5.text                      # 文档 MD5 去重记录
```

---

## 📦 环境依赖

### Python 版本

建议使用 **Python 3.10+**（代码中使用了 `tuple[str, str]` 等 3.10+ 类型注解语法）。

### 主要依赖包

| 包名 | 用途 |
|------|------|
| `streamlit` | 前端 Web 框架 |
| `langchain` | Agent / Chain / Tool 框架 |
| `langchain-core` | LangChain 核心抽象 |
| `langchain-community` | 通义千问、DashScope Embedding 等集成（国内版） |
| `langchain-openai` | ChatOpenAI 封装（国际版兼容端调用） |
| `langgraph` | 基于图的 Agent 执行引擎 |
| `langchain-chroma` | LangChain 与 Chroma 向量库集成 |
| `chromadb` | Chroma 向量数据库 |
| `dashscope` | 阿里云 DashScope SDK（国内版 LLM / Embedding） |
| `openai` | OpenAI 客户端（国际版 Embedding 封装使用） |
| `pypdf` / `pypdf2` | PDF 文档加载 |
| `pyyaml` | YAML 配置文件解析 |

### 安装依赖

```bash
pip install streamlit langchain langchain-core langchain-community langchain-openai \
            langgraph langchain-chroma chromadb dashscope openai pypdf pyyaml
```

---

## ⚙️ 配置说明

### 1. 阿里云 API Key

本项目使用阿里云通义千问大模型和 DashScope Embedding，需要配置系统环境变量：

```bash
# Linux / macOS
export DASHSCOPE_API_KEY="your_dashscope_api_key"

# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_dashscope_api_key"
```

> **国内版**：可在 [阿里云百炼平台](https://bailian.console.aliyun.com/) 获取 API Key。  
> **国际版**：可在 [阿里云国际站](https://www.alibabacloud.com/help/en/model-studio/) 获取 API Key，端点为新加坡节点。

### 2. 选择调用区域（国内 / 国际）

编辑 `config/rag.yml`，通过 `api_region` 字段一键切换调用方式：

```yaml
# config/rag.yml

# API 调用区域配置
# domestic      = 国内版 dashscope（原生调用，推荐）
# international = 新加坡地域 OpenAI 兼容端（海外/无法访问国内端点时使用）
api_region: domestic

chat_model_name: qwen3-max
embedding_model_name: text-embedding-v4
```

| `api_region` 值 | 适用场景 | 底层实现 |
|-----------------|----------|----------|
| `domestic`（默认） | 国内网络环境，直接访问 DashScope | `ChatTongyi` + `DashScopeEmbeddings` |
| `international` | 海外/境外网络环境，访问新加坡节点 | `ChatOpenAI` + 自定义 OpenAI 客户端封装 |

两种模式共用同一个 `DASHSCOPE_API_KEY`，无需分别申请。

### 3. 高德地图 API Key

编辑 `config/agent.yml`，将 `gaodekey` 替换为你的高德地图 Web 服务 API Key：

```yaml
# config/agent.yml
external_data_path: data/external/records.csv
gaodekey: 你的高德key!        # ← 替换这里
gaode_base_url: https://restapi.amap.com
gaode_timeout: 5
```

> 可在 [高德开放平台](https://console.amap.com/) 申请 Web 服务类型的 API Key。

### 4. 向量库配置

编辑 `config/chroma.yml` 可调整 RAG 检索参数：

```yaml
# config/chroma.yml
collection_name: agent
persist_directory: chroma_db
k: 3                    # 检索返回的最相关文档数量
data_path: data
md5_hex_store: md5.text
allow_knowledge_file_type: ["txt", "pdf"]
chunk_size: 200         # 文本分块大小
chunk_overlap: 20       # 分块重叠长度
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd LangChain-ReAct-Agent
```

### 2. 安装依赖

```bash
pip install streamlit langchain langchain-core langchain-community langchain-openai \
            langgraph langchain-chroma chromadb dashscope openai pypdf pyyaml
```

### 3. 配置 API Key

```bash
# 设置阿里云 DashScope API Key（国内版与国际版共用）
export DASHSCOPE_API_KEY="your_dashscope_api_key"

# 在 config/agent.yml 中配置高德地图 API Key
```

### 4. 选择调用区域（可选）

如果你身处海外或无法访问国内 DashScope 端点，编辑 `config/rag.yml`：

```yaml
api_region: international   # 切换为新加坡节点 OpenAI 兼容端
```

### 5. 启动应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`，即可开始与智扫通机器人智能客服对话。

---

## 💬 使用方式

启动后，用户可以在网页聊天界面进行以下操作：

### 产品咨询

直接提问关于扫地机器人的使用、维护、故障排除等问题，Agent 会优先从知识库中检索相关资料进行回答：

```
用户：扫地机器人的滤网多久需要更换一次？
用户：扫拖一体机器人和扫地机器人有什么区别？
用户：扫地机器人吸力变弱了怎么办？
```

### 天气与定位查询

Agent 可调用高德 API 获取实时信息：

```
用户：我现在所在城市今天的天气怎么样？
```

> ⚠️ **提示**：高德 IP 定位功能有时会出现偏差（定位到运营商节点所在城市）。由于系统保留了完整的会话上下文（短期记忆），若定位不准确，你可以直接接着说出正确的城市名，Agent 会基于上下文继续完成天气查询任务，无需重新发起请求。
>
> ```
> 用户：我现在所在城市今天的天气怎么样？
> 助手：您当前定位在上海，上海今天……（定位有误）
> 用户：不对，我在成都
> 助手：好的，成都今天天气……（基于上下文正确响应）
> ```

### 使用报告生成

Agent 会自动检测报告生成意图，切换到报告提示词，并调用外部数据生成 Markdown 格式的使用情况报告：

```
用户：帮我生成我的使用报告
用户：给我一份扫地机器人的使用分析和保养建议
```

---

## 🛠 工具列表

Agent 配备了以下 7 个工具：

| 工具名 | 描述 |
|--------|------|
| `rag_summarize` | 从向量知识库中检索参考资料，回答产品相关问题 |
| `get_weather` | 获取指定城市的实时天气（高德 API） |
| `get_user_location` | 通过 IP 获取用户所在城市（高德 API） |
| `get_user_id` | 获取当前用户 ID |
| `get_current_month` | 获取当前月份 |
| `fetch_external_data` | 从外部系统获取指定用户指定月份的使用记录 |
| `fill_context_for_report` | 触发报告模式，通知中间件切换为报告生成提示词 |

---

## 🔄 中间件机制

Agent 的三个中间件负责监控、日志和动态提示词切换：

```
monitor_tool         工具调用监控
  ├─ 记录每次工具调用的名称和参数
  ├─ 记录工具调用成功/失败状态
  └─ 检测 fill_context_for_report 调用，将 context["report"] 置为 True

log_before_model     模型调用前日志
  └─ 记录当前消息数量及最新消息内容

report_prompt_switch 动态提示词切换
  ├─ context["report"] == True  → 使用报告生成提示词
  └─ context["report"] == False → 使用主 ReAct 提示词
```

---

## 🧠 短期记忆机制

本项目实现了基于会话的**短期记忆**，让 Agent 能感知完整的对话上下文，支持多轮连续交互。

### 实现原理

```
Streamlit 前端 (app.py)
  └─ st.session_state["message"]   # 完整对话历史列表（本次会话内持久）
       ├─ {"role": "user",      "content": "..."}
       ├─ {"role": "assistant", "content": "..."}
       └─ ...

每次用户发送消息：
  1. 新消息追加到 session_state["message"]
  2. 将完整历史列表传入 ReactAgent.execute_stream(query, history)
  3. Agent 构造 input_dict = {"messages": [全部历史 + 当前问题]}
  4. LLM 接收完整上下文，感知前序对话
  5. 助手回复追加回 session_state["message"]，供下一轮携带
```

### 典型场景：弥补高德定位偏差

高德 IP 定位有时会将用户定位到运营商节点城市（而非实际所在城市）。有了短期记忆，用户无需重新完整描述需求，只需直接补充正确城市名，Agent 即可基于上下文完成任务：

```
用户：我现在所在城市今天的天气怎么样？
助手：您当前定位在上海，上海今天晴，气温 22°C……  ← 定位有误
用户：不对，我在成都                               ← 只需补充城市名
助手：好的，成都今天多云，气温 18°C……             ← Agent 基于上下文正确响应
```

---

## 🌐 国际版 API 说明

本项目在原有国内版 DashScope 调用的基础上，新增了**阿里云国际版（新加坡节点）OpenAI 兼容端**的支持。

### 实现原理

模型工厂（`model/factory.py`）采用抽象工厂 + 单例模式，根据 `config/rag.yml` 中的 `api_region` 配置，在启动时选择对应的底层实现：

```
api_region = domestic      → ChatTongyi / DashScopeEmbeddings（国内原生 SDK）
api_region = international → ChatOpenAI / DashscopeCompatEmbeddings（OpenAI 兼容端）
```

国际版端点地址：

```
https://dashscope-intl.aliyuncs.com/compatible-mode/v1
```

### Embedding 兼容适配

国际版 Embedding 通过自定义 `DashscopeCompatEmbeddings` 类实现，直接使用 `openai.OpenAI` 客户端调用兼容端，规避了原生 DashScope SDK 在兼容端上的 `contents` 结构兼容问题。

### 注意事项

- 国内版与国际版使用**同一个 `DASHSCOPE_API_KEY`**，在对应平台申请后无需额外配置。
- 切换区域只需修改 `config/rag.yml` 中的 `api_region` 字段，无需改动任何业务代码。
- 已向量化入库的数据（`chroma_db/`）在切换区域后需**重新构建**，因为不同模型产生的向量空间不兼容。

---

## 📋 日志说明

日志文件存放在 `logs/` 目录下，按天自动创建：

```
logs/
└── agent_20250101.log    # 格式：{name}_{YYYYMMDD}.log
```

日志格式：

```
2025-01-01 12:00:00,123 - agent - INFO - middleware.py:19 - [tool monitor]执行工具：get_weather
```

- **控制台**：输出 INFO 及以上级别日志
- **文件**：输出 DEBUG 及以上级别日志（更详细）

---

## 📚 知识库

知识库文档存放在 `data/` 目录下，支持 `.txt` 和 `.pdf` 格式。首次启动时，系统会自动将文档向量化并存入 Chroma 数据库（`chroma_db/`）。已处理文档通过 MD5 哈希追踪，重启后不会重复入库。

**内置知识库文档：**

| 文件 | 内容 |
|------|------|
| `扫地机器人100问.pdf` | 扫地机器人常见问题解答（PDF） |
| `扫地机器人100问2.txt` | 扫地机器人补充问答 |
| `扫拖一体机器人100问.txt` | 扫拖一体机器人常见问题解答 |
| `故障排除.txt` | 故障排除指南 |
| `维护保养.txt` | 日常维护保养说明 |
| `选购指南.txt` | 购买建议与选型指南 |

如需扩展知识库，只需将新的 `.txt` 或 `.pdf` 文件放入 `data/` 目录，重启服务后会自动加载。

---

## 🔮 后续优化方向

- 将向量数据库从 Chroma 替换为 Redis（更适合生产部署）
- 地点、天气等功能完整迁移至高德 MCP 协议
- 增加用户身份认证与多用户会话隔离
- 支持更多文档格式（Word、Excel 等）

---

## 📄 许可证

本项目仅供学习与参考使用。  
感谢黑马程序员开源免费项目、阿里云和高德地图等开放平台。
部分代码以及README的实现参考了网友项目：https://github.com/bamboo-moon/zhisaotong-Agent
