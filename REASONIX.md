# Reasonix project memory

Notes the user pinned via the `#` prompt prefix. The whole file is
loaded into the immutable system prefix every session — keep it terse.

- 项目名称

InterviewGPT —— AI英语面试教练

# 项目背景

你是一名资深全栈工程师、AI产品架构师和技术负责人。

请帮助我开发一个可在3天内完成并上这是按照 **XEngineer 三天议题一等奖水平**设计的，不追求炫技，而是追求：

* 能跑通
* 能演示
* 有商业价值
* 有架构设计
* 有 AI 特色

---

线演示的AI产品。

项目目标：

构建一个面向大学生和求职者的AI英语面试教练。

用户能够通过语音与AI面试官进行真实英语面试。

AI能够：

* 发起面试
* 连续追问
* 记录对话
* 分析用户英语能力
* 给出面试反馈报告

项目最终需要达到：

一个真实用户可以直接使用的MVP产品，而非技术Demo。

---

# 核心用户场景

用户：

计算机专业大学生

需求：

准备英语面试

使用流程：

进入系统

↓

选择岗位

* Backend Developer
* Software Engineer
* AI Engineer

↓

开始英语面试

↓

语音交流

↓

AI连续追问

↓

结束面试

↓

生成评估报告

---

# MVP功能范围

必须完成：

## 1. 场景选择

支持：

* Software Engineer
* Backend Engineer
* AI Engineer

每个场景拥有独立Prompt

---

## 2. AI面试官

使用DeepSeek API

模型：

deepseek-chat

能力：

* 提问
* 多轮追问
* 保持上下文
* 模拟真实面试官

要求：

不要一次输出多个问题

每轮只问一个问题

根据用户回答深度继续追问

---

## 3. 英语语音交互

流程：

用户语音

↓

Speech To Text

↓

DeepSeek

↓

Text Response

↓

Text To Speech

↓

播放语音

支持连续对话

保证响应时间尽量低于3秒

---

## 4. 面试记录

记录：

* 用户回答
* AI问题
* 时间
* 会话ID

存入数据库

---

## 5. 面试结束报告

生成：

### Overall Score

0-100

### Fluency

0-100

### Grammar

0-100

### Vocabulary

0-100

### Professional Communication

0-100

---

输出：

优点

改进建议

推荐表达

常见错误

---

# 技术架构

前端：

Next.js 15
TypeScript
TailwindCSS
Shadcn UI

后端：

FastAPI

数据库：

PostgreSQL

缓存：

Redis

AI：

DeepSeek API

模型：

deepseek-chat

部署：

Docker

---

# 数据库设计

Table: interview_session

字段：

id
user_id
position
start_time
end_time
overall_score

---

Table: conversation

字段：

id
session_id
role
content
timestamp

---

Table: report

字段：

id
session_id
fluency
grammar
vocabulary
communication
summary

---

# Prompt Engineering设计

系统Prompt：

你是一名拥有10年以上经验的英语技术面试官。

目标：

帮助候选人提升英语面试能力。

规则：

1. 全程使用英文交流
2. 每轮只提一个问题
3. 根据用户回答追问
4. 模拟真实面试官
5. 不主动结束面试
6. 保持专业友好
7. 问题难度逐渐增加

---

# 评估Agent

当面试结束时：

分析全部对话内容

输出：

{
"overall_score": 85,
"fluency": 80,
"grammar": 88,
"vocabulary": 82,
"communication": 90,
"strengths": [],
"weaknesses": [],
"suggestions": []
}

---

# UI页面设计

页面1：

Landing Page

功能：

开始面试

选择岗位

---

页面2：

Interview Room

功能：

实时语音交流

聊天记录

麦克风按钮

结束按钮

---

页面3：

Report Page

功能：

能力雷达图

分数展示

错误分析

改进建议

---

# 加分项

如果时间允许：

增加：

## AI追问能力

例如：

用户：

I developed a vending machine system.

AI：

Interesting.

What challenges did you encounter while designing the inventory synchronization module?

---

## STAR面试分析

自动分析：

Situation
Task
Action
Result

完整度评分

---

# 输出要求

请生成：

1. 项目目录结构
2. 前后端代码框架
3. FastAPI接口设计
4. Next.js页面代码
5. DeepSeek API调用代码
6. 数据库Schema
7. Docker部署方案
8. README
9. 开发任务拆解
10. 三天开发计划

代码必须能够直接运行。
不要伪代码。
优先实现MVP闭环。
- 项目名称

InterviewGPT —— AI英语面试教练

# 项目背景

你是一名资深全栈工程师、AI产品架构师和技术负责人。

请帮助我开发一个可在3天内完成并上这是按照 **XEngineer 三天议题一等奖水平**设计的，不追求炫技，而是追求：

* 能跑通
* 能演示
* 有商业价值
* 有架构设计
* 有 AI 特色

---

线演示的AI产品。

项目目标：

构建一个面向大学生和求职者的AI英语面试教练。

用户能够通过语音与AI面试官进行真实英语面试。

AI能够：

* 发起面试
* 连续追问
* 记录对话
* 分析用户英语能力
* 给出面试反馈报告

项目最终需要达到：

一个真实用户可以直接使用的MVP产品，而非技术Demo。

---

# 核心用户场景

用户：

计算机专业大学生

需求：

准备英语面试

使用流程：

进入系统

↓

选择岗位

* Backend Developer
* Software Engineer
* AI Engineer

↓

开始英语面试

↓

语音交流

↓

AI连续追问

↓

结束面试

↓

生成评估报告

---

# MVP功能范围

必须完成：

## 1. 场景选择

支持：

* Software Engineer
* Backend Engineer
* AI Engineer

每个场景拥有独立Prompt

---

## 2. AI面试官

使用DeepSeek API

模型：

deepseek-chat

能力：

* 提问
* 多轮追问
* 保持上下文
* 模拟真实面试官

要求：

不要一次输出多个问题

每轮只问一个问题

根据用户回答深度继续追问

---

## 3. 英语语音交互

流程：

用户语音

↓

Speech To Text

↓

DeepSeek

↓

Text Response

↓

Text To Speech

↓

播放语音

支持连续对话

保证响应时间尽量低于3秒

---

## 4. 面试记录

记录：

* 用户回答
* AI问题
* 时间
* 会话ID

存入数据库

---

## 5. 面试结束报告

生成：

### Overall Score

0-100

### Fluency

0-100

### Grammar

0-100

### Vocabulary

0-100

### Professional Communication

0-100

---

输出：

优点

改进建议

推荐表达

常见错误

---

# 技术架构

前端：

Next.js 15
TypeScript
TailwindCSS
Shadcn UI

后端：

FastAPI

数据库：

PostgreSQL

缓存：

Redis

AI：

DeepSeek API

模型：

deepseek-chat

部署：

Docker

---

# 数据库设计

Table: interview_session

字段：

id
user_id
position
start_time
end_time
overall_score

---

Table: conversation

字段：

id
session_id
role
content
timestamp

---

Table: report

字段：

id
session_id
fluency
grammar
vocabulary
communication
summary

---

# Prompt Engineering设计

系统Prompt：

你是一名拥有10年以上经验的英语技术面试官。

目标：

帮助候选人提升英语面试能力。

规则：

1. 全程使用英文交流
2. 每轮只提一个问题
3. 根据用户回答追问
4. 模拟真实面试官
5. 不主动结束面试
6. 保持专业友好
7. 问题难度逐渐增加

---

# 评估Agent

当面试结束时：

分析全部对话内容

输出：

{
"overall_score": 85,
"fluency": 80,
"grammar": 88,
"vocabulary": 82,
"communication": 90,
"strengths": [],
"weaknesses": [],
"suggestions": []
}

---

# UI页面设计

页面1：

Landing Page

功能：

开始面试

选择岗位

---

页面2：

Interview Room

功能：

实时语音交流

聊天记录

麦克风按钮

结束按钮

---

页面3：

Report Page

功能：

能力雷达图

分数展示

错误分析

改进建议

---

# 加分项

如果时间允许：

增加：

## AI追问能力

例如：

用户：

I developed a vending machine system.

AI：

Interesting.

What challenges did you encounter while designing the inventory synchronization module?

---

## STAR面试分析

自动分析：

Situation
Task
Action
Result

完整度评分

---

# 输出要求

请生成：

1. 项目目录结构
2. 前后端代码框架
3. FastAPI接口设计
4. Next.js页面代码
5. DeepSeek API调用代码
6. 数据库Schema
7. Docker部署方案
8. README
9. 开发任务拆解
10. 三天开发计划

代码必须能够直接运行。
不要伪代码。
优先实现MVP闭环。
