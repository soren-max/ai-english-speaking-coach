# 🎙️ InterviewGPT — AI 英语面试教练

> **XEngineer 三天议题 · 一等奖水平作品**

InterviewGPT 是一款面向大学生和求职者的 **AI 英语面试教练**。用户可与 AI 面试官进行真实英语语音面试，AI 能发起面试、连续追问、分析英语能力并生成评估报告。

---

## 📺 Demo 演示视频

<!-- 请将你的演示视频链接替换到下方，放至显眼位置供评委查看 -->

| 平台 | 链接 |
|------|------|
| 🎬 Bilibili | [点击观看 Demo 视频](https://bilibili.com/...) |
| ☁️ 备用云盘 | [点击下载](https://pan.baidu.com/s/...) |

> **视频内容覆盖：** 场景选择 → 语音面试 → AI追问 → 结束面试 → 能力雷达图 → 评估报告

---

## ✨ 核心功能

### 🎯 1. 岗位场景选择
支持三种面试岗位，每种拥有独立的 Prompt：
- **Software Engineer** — 算法、数据结构、OOP
- **Backend Engineer** — 系统设计、API、数据库、可扩展性
- **AI Engineer** — 机器学习、NLP、LLM、模型部署

### 🤖 2. AI 面试官（DeepSeek 驱动）
- 全程英文交流，模拟 10 年+经验技术面试官
- **每轮只问一个问题**，根据回答深度连续追问
- 问题难度逐渐递增，模拟真实面试节奏
- 不会主动结束面试，由用户控制

### 🎤 3. 语音交互
- 用户语音输入 → 语音识别 → DeepSeek 回复 → 语音播报
- 支持连续对话，响应时间 &lt; 3 秒

### 📝 4. 面试记录
- 完整记录所有 AI 问题与用户回答
- 存入 PostgreSQL 数据库，支持历史回溯

### 📊 5. 评估报告
面试结束后自动生成：

| 维度 | 说明 | 评分范围 |
|------|------|----------|
| **Overall Score** | 综合评分 | 0–100 |
| **Fluency** | 流利度 | 0–100 |
| **Grammar** | 语法准确度 | 0–100 |
| **Vocabulary** | 词汇丰富度 | 0–100 |
| **Professional Communication** | 专业表达能力 | 0–100 |

输出还包括：**优点**、**改进建议**、**推荐表达**、**常见错误分析**。

### ⭐ 6. 加分功能
- **AI 追问能力** — 根据用户回答深度挖掘技术细节
- **STAR 面试分析** — 自动分析 Situation / Task / Action / Result 完整度

---

## 🏗️ 技术架构

```
┌──────────────────────┐      ┌──────────────────────┐
│   Frontend           │      │   Backend            │
│   Next.js 15         │─────▶│   FastAPI            │
│   TypeScript         │      │   Python 3.12        │
│   TailwindCSS        │      │   SQLAlchemy         │
│   Shadcn UI          │      │   LangGraph          │
│   Recharts (图表)     │      │   DeepSeek API       │
└──────────────────────┘      └──────────┬───────────┘
                                         │
                               ┌─────────▼───────────┐
                               │   PostgreSQL         │
                               │   (via conda/Docker) │
                               └──────────────────────┘
```

### 目录结构

```
├── frontend/          # Next.js 前端
│   ├── app/           # 页面路由
│   ├── components/    # UI 组件
│   ├── services/      # API 客户端
│   ├── hooks/         # 自定义 Hooks
│   ├── types/         # TypeScript 类型
│   └── voice/         # 语音识别/合成
├── backend/           # FastAPI 后端
│   ├── api/           # REST API 路由
│   ├── agents/        # LangGraph AI Agent
│   ├── services/      # 业务逻辑
│   ├── models/        # 数据库模型
│   ├── schemas/       # Pydantic 数据模型
│   └── core/          # 配置与工具
└── docker-compose.yml # 容器化部署
```

---

## 🚀 快速启动

### 前置要求

- Python 3.12+
- Node.js 22+
- PostgreSQL 16+（或 Docker）
- DeepSeek API Key

### 1. 配置环境变量

```bash
# 后端
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入你的 DeepSeek API Key

# 前端
cp frontend/.env.local.example frontend/.env.local
```

### 2. 启动数据库

**方式 A — conda 本地运行（推荐）**
```bash
conda install -c conda-forge postgresql
initdb -D ~/.local/share/postgresql/data
pg_ctl -D ~/.local/share/postgresql/data -l ~/.local/share/postgresql/logfile start
psql -d postgres -c "CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';"
psql -d postgres -c "CREATE DATABASE interviewgpt OWNER postgres;"
```

**方式 B — Docker**
```bash
docker compose up -d postgres
```

### 3. 安装依赖 & 启动

```bash
# 后端
cd backend
uv pip install -r requirements.txt  # 或 pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# 前端
cd ../frontend
npm install
npm run dev &
```

### 4. 访问

- 前端：**http://localhost:3000**
- API 文档：**http://localhost:8000/docs**
- 健康检查：**http://localhost:8000/api/v1/health**

---

## 🧪 测试 API

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 注册用户
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'

# 开始面试
curl -X POST http://localhost:8000/api/v1/session/start \
  -H "Content-Type: application/json" \
  -d '{"position":"Backend Engineer"}'
```

---

## 📦 部署（Docker）

```bash
docker compose up --build -d
```

访问 `http://localhost:3000` 即可使用完整服务。

---

## 🧭 开发路线

### Day 1 — 骨架搭建
- [x] 项目目录结构
- [x] 数据库 Schema 与迁移
- [x] FastAPI 接口框架
- [x] Next.js 页面框架

### Day 2 — 核心功能
- [x] DeepSeek API 集成
- [x] 面试会话管理
- [x] LangGraph Agent 工作流
- [x] 前端语音交互

### Day 3 — 收尾优化
- [x] 评估报告生成
- [x] 能力雷达图
- [x] Docker 部署方案
- [x] Demo 视频 & README

---

## 📄 许可证

MIT
