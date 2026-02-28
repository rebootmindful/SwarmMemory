# Swarm + Memory Profile

> 轻量级多 Agent 协作系统 + 自动记忆框架

让 AI 记住一切，让协作自动发生。

---

## ✨ 特性

- 🐝 **多 Agent 流水线** - 分工明确，写作/开发自动化
- 🧠 **三层记忆架构** - 即时/短期/长期，自动遗忘
- ⚡ **全自动化** - 定时同步、夜间反思、垃圾归档
- 🔄 **自我进化** - 根据成功率自动优化
- 🛠️ **易扩展** - 简单配置即可添加新 Agent

---

## 🚀 快速开始

### 1. 克隆

```bash
git clone https://github.com/your-username/swarm-memory.git
cd swarm-memory
```

### 2. 配置环境变量

```bash
# 至少配置一个
export OPENAI_API_KEY="sk-xxx"

# 可选：其他 API
export ANTHROPIC_API_KEY="sk-ant-xxx"
export DEEPSEEK_API_KEY="sk-xxx"
```

### 3. 初始化

```bash
# 初始化记忆系统
./memory-profile/memory.sh init

# 设置权限
chmod +x swarm/scripts/*.sh
chmod +x memory-profile/*.sh
```

### 4. 运行

```bash
# 写作工作流 (初稿→审核→终审)
./swarm/scripts/artgroup.sh "写一篇关于AI的文章"

# 开发工作流 (规划→开发→测试)
./swarm/scripts/devgroup.sh "开发一个用户登录功能"

# 查看记忆统计
./memory-profile/memory.sh stats
```

---

## 🐝 Swarm 工作流

### ArtGroup - 写作流水线

```
用户输入
    ↓
wand (初稿生成)
    ↓
review (审核润色)
    ↓
final (终审优化)
    ↓
最终输出
```

每个 Agent 只做一件事，分工带来稳定。

### DevGroup - 开发流水线

```
用户输入
    ↓
planner (需求规划)
    ↓
coder (代码开发)
    ↓
tester (测试验证)
    ↓
最终输出
```

适合：代码开发、技术文档、功能实现

### Agent 扩展

编辑 `swarm/scripts/agent.sh` 添加更多 Agent：

```bash
# 添加新 Agent
translator)
    echo "🌍 翻译中..."
    call_api "翻译成英文：$TASK" "$MODEL"
    ;;
esac
```

---

## 🧠 Memory Profile

### 三层记忆架构

| 层级 | 容量 | 用途 |
|------|------|------|
| L0 | 100条 | 即时记忆，当前任务 |
| L1 | 500条 | 短期记忆，本周内容 |
| L2 | 无限 | 长期记忆，永久知识 |

### 遗忘模型

自动计算记忆"温度"：

```
温度 = 0.5 × 时间衰减 + 0.3 × 引用次数 + 0.2 × 优先级
```

- 🔥 热门 (>0.7): 保持活跃
- 🌤️ 温热 (0.3-0.7): 降权检索
- 🧊 冷冻 (<0.3): 移至归档

### 命令

```bash
# 初始化
./memory-profile/memory.sh init

# 添加记忆
./memory-profile/memory.sh add "今天学到了新东西"

# 搜索
./memory-profile/memory.sh search "AI"

# 统计
./memory-profile/memory.sh stats

# 夜间反思
./memory-profile/memory.sh reflect

# 归档
./memory-profile/memory.sh gc
```

---

## ⚙️ 配置

### 环境变量

```bash
# API 配置
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1

# 可选：其他 LLM
ANTHROPIC_API_KEY=sk-ant-xxx
DEEPSEEK_API_KEY=sk-xxx
```

### Agent 配置

编辑 `swarm/scripts/agent.sh` 自定义 Agent 行为：

```bash
# 修改初稿 Agent 的 prompt
wand)
    call_api "你是一个专业作家。请用活泼的风格写作：$TASK" "gpt-4o"
    ;;
```

---

## ⏰ 定时任务

系统会自动执行以下任务：

| 时间 | 任务 | 说明 |
|------|------|------|
| 22:00 | sync | 增量同步记忆 |
| 22:45 | reflect | 夜间反思 |
| 周日 22:00 | gc | 垃圾归档 |

### 手动设置 Cron

```bash
# 编辑 crontab
crontab -e

# 添加:
0 22 * * * /path/to/swarm-memory/memory-profile/memory.sh sync
45 22 * * * /path/to/swarm-memory/memory-profile/memory.sh reflect
0 22 * * 0 /path/to/swarm-memory/memory-profile/memory.sh gc
```

---

## 📁 目录结构

```
swarm-memory/
├── README.md                    # 本文件
├── INSTALL.md                  # 安装指南
│
├── swarm/                      # 多 Agent 协作
│   ├── scripts/
│   │   ├── artgroup.sh        # 写作工作流
│   │   ├── devgroup.sh        # 开发工作流
│   │   └── agent.sh           # Agent 调用器
│   └── core/                  # 核心模块
│
└── memory-profile/            # 自动记忆
    ├── memory.sh              # 主入口
    ├── scripts/
    │   ├── memory_system.cjs  # 记忆系统
    │   ├── nightly_reflection.cjs
    │   ├── forget_model.cjs
    │   └── crud_validator.cjs
    └── memory/                # 记忆存储
        ├── lessons/           # 经验
        ├── decisions/         # 决策
        ├── people/           # 人物
        └── reflections/       # 反思
```

---

## 🔧 开发

### 添加新工作流

1. 复制 `artgroup.sh` 为新脚本
2. 修改 Agent 组合
3. 添加执行权限

```bash
cp swarm/scripts/artgroup.sh swarm/scripts/analyze.sh
chmod +x swarm/scripts/analyze.sh
```

### 添加记忆路由

编辑 `memory-profile/scripts/crud_validator.cjs` 修改知识分类逻辑。

---

## 📊 效果

运行一段时间后：

- Agent 不再重复问同样的问题
- 跨任务知识可以复用
- 新任务上手更快
- 系统仍然高效运行

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

## 📝 License

MIT
>>>>>>> 4f36430 (feat: Swarm + Memory Profile - 轻量级多 Agent 协作系统)
