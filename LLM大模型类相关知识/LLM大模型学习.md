

## 什么是Agent?

> [!NOTE]
>
> 询问问题:
>
> 京东开源了一个项目是JoyAgent-JDGenie,里面提到的"开源agent"这个名词我想知道agent是代表的什么意思,我理解下来他好像就是一个脚手架,既不是llm大模型也不是mcp等协议封装,到底是什么,帮我解释下



### **1. Agent的核心定义：基于LLM的自主任务执行系统**

在JoyAgent-JDGenie的语境中，**Agent（智能体）** 是**以LLM（大模型）为核心**，通过**感知-规划-执行-反思**闭环，自主完成用户任务的智能系统。它不是简单的“脚手架”，而是具备**自主决策能力**的执行单元，能理解用户意图、拆解任务、调用工具、整合结果，并最终输出符合需求的产物（如报告、PPT、数据分析结论等）。

### **2. Agent与LLM的关系：LLM是Agent的“大脑”**

LLM是Agent的核心组件，承担**任务规划、逻辑推理、工具选择**等关键决策功能。例如，当用户输入“生成2025年美元与黄金走势分析报告”时，LLM会先分析任务目标（生成报告），再拆解为“获取美元走势数据”“获取黄金价格数据”“整合数据并撰写报告”等子任务，随后调用对应的工具（如ReportTool生成报告、DeepSearchTool获取数据）执行。LLM的推理能力决定了Agent的“智能水平”，而Agent则是LLM能力的**具体执行载体**。

### **3. Agent与MCP协议的关系：MCP是Agent的“工具连接器”**

MCP（Model Context Protocol）是Agent调用**外部工具/服务**的标准协议，解决的是Agent与第三方工具的**兼容性问题**。例如，JoyAgent-JDGenie中的“DeepSearchTool（深度搜索）”“ReportTool（报告生成）”等工具，均通过MCP协议与Agent交互。MCP协议定义了统一的接口规范，让Agent无需针对每个工具开发定制化集成代码，只需遵循协议即可调用符合规范的工具，提升了Agent的**扩展性**（可快速接入新工具）和**灵活性**（支持多种工具组合）。

### **4. Agent与“脚手架”的本质区别：“脚手架”是工具，“Agent”是系统**

用户理解的“脚手架”（如SDK、框架）通常是**开发工具**，提供基础组件和模板，需开发者自行搭建业务逻辑；而Agent是**完整的智能系统**，具备**自主执行能力**，无需开发者从零开始编写任务流程。例如，JoyAgent-JDGenie中的PlanningAgent（规划代理）会自动拆解任务、生成计划，ExecutorAgent（执行代理）会自动调用工具、跟踪进度，这些功能均由Agent自身完成，开发者只需配置工具或添加子智能体（如通过BaseTool接口实现自定义工具），即可快速搭建定制化智能体应用。

### **5. JoyAgent-JDGenie中Agent的具体角色：端到端任务执行者**

在JoyAgent-JDGenie项目中，Agent的角色是**端到端的任务执行者**，涵盖从用户请求到结果输出的全流程：

- •**感知**：通过LLM理解用户意图（如“生成报告”）；
- •**规划**：PlanningAgent拆解任务为子任务（如“获取数据”“生成报告”）；
- •**执行**：ExecutorAgent调用对应工具（如ReportTool生成报告、DeepSearchTool获取数据）；
- •**反思**：通过Memory模块记录执行过程，优化后续任务处理。



## **SSE（服务器推送事件）**

> [!IMPORTANT]
>
> **Server-Sent Events**

SSE是一种**基于HTTP协议的轻量级单向通信技术**，核心功能是允许服务器通过**持久化连接**主动向客户端推送实时数据流（如文本、JSON等结构化数据）。它解决了传统HTTP请求-响应模式中“客户端需主动发起请求才能获取更新”的痛点，适用于需要“服务器→客户端”实时数据同步的场景。

### **SSE的核心特性**

1. 1.**单向通信**：仅支持服务器向客户端推送数据，客户端无法通过同一连接向服务器发送信息（若需客户端交互，需结合其他技术如HTTP请求）。
2. 2.**基于HTTP协议**：复用现有HTTP基础设施（如端口80/443、防火墙规则），无需额外协议升级（如WebSocket的`ws://`升级），兼容性好。
3. 3.**轻量高效**：协议头精简（仅需`Content-Type: text/event-stream`等必要字段），数据以纯文本格式传输（支持UTF-8编码），内存占用低，适合高并发场景。
4. 4.**自动重连**：浏览器原生支持断线重连机制（默认3秒间隔），客户端无需手动实现心跳检测，提升连接稳定性。
5. 5.**有序性**：服务器推送的消息按发送顺序到达客户端，保证数据流的连贯性（如AI生成文本的逐字输出）。

### **SSE的协议格式与工作流程**

#### **1. 协议格式**

SSE通过**文本流**传输数据，每条消息由多行字段组成，以`\n\n`结尾。常见字段包括：

- •`data`：必填，包含有效负载（如文本、JSON字符串），可多行拼接（每行以`\n`结尾）；
- •`id`：可选，消息唯一标识（用于断线后恢复连接，客户端通过`Last-Event-ID`头传递）；
- •`event`：可选，自定义事件类型（客户端通过`addEventListener`监听特定事件）；
- •`retry`：可选，重连间隔（毫秒，控制客户端断线后的重试频率）。

**示例消息**：

```json
data: {"type": "text", "content": "Hello, SSE!"}\n\n
id: 123\n
event: message\n
retry: 5000\n\n
```

#### **2. 工作流程**

- •**连接建立**：客户端通过`EventSource` API发起HTTP GET请求（如`new EventSource('/stream')`），服务器返回`200 OK`状态及SSE协议头；
- •**数据推送**：服务器保持连接开启，通过`res.write()`发送格式化消息（如`data: ${chunk}\n\n`），客户端实时接收并解析；
- •**连接维护**：若连接中断，客户端自动重连（携带`Last-Event-ID`头），服务器根据ID恢复数据流（如补发错过的消息）











## B站UP的一些视频学习

### 【DeepSeek+LoRA+FastAPI】开发人员如何微调大模型并暴露接口给后端调用

Demo前端Github地址：https://github.com/huangyf2013320506/magic_conch_frontend.git 

Demo后端Github地址（含数据集）：https://github.com/huangyf2013320506/magic_conch_backend.git 

笔记文档（.md）：https://pan.quark.cn/s/57939e67d3d0 

笔记文档（.pdf）：https://pan.quark.cn/s/d5ed78ef4f76 

所有资料：https://pan.quark.cn/s/802cd0c232b4





### 【知识科普】【纯本地化搭建】【不本地也行】DeepSeek+RAGFlow构建个人知识库

笔记 https://pan.quark.cn/s/851214dbec60

RAGFlow源代码：https://pan.quark.cn/s/3beb27b5224f 

ollama安装包（win版）：https://pan.quark.cn/s/d5dec665e03d 

docker桌面版安装包（win版）：https://pan.quark.cn/s/15e4a6bcaf95



### 《Attention is all you need》论文解读及Transformer架构详细介绍

PPT、论文笔记版github地址：https://github.com/huangyf2013320506/bilibili_repository





### 什么是Function Calling与MCP协议？它们为何要这样设计？

文档飞书链接：https://oigi8odzc5w.feishu.cn/wiki/LWqEwXNkBibT0ykrbI0cvptBnAf 密码：4892@u29 

文档 pdf 及 word：https://github.com/huangyf2013320506/bilibili_repository