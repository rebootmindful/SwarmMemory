# 安装指南

## 环境要求

- Linux / macOS / WSL
- Node.js 18+
- Bash
- LLM API Key (OpenAI/Anthropic/DeepSeek 等)

## 安装步骤

### 1. 克隆

```bash
git clone https://github.com/your-repo/openclaw-swarm.git
cd openclaw-swarm
```

### 2. 配置

创建 `.env` 文件：

```bash
# 至少选择一个
OPENAI_API_KEY=sk-xxx
# 或
ANTHROPIC_API_KEY=sk-ant-xxx
# 或
DEEPSEEK_API_KEY=sk-xxx
```

### 3. 初始化

```bash
# 初始化记忆系统
./memory-profile/memory.sh init

# 设置执行权限
chmod +x swarm/scripts/*.sh
chmod +x memory-profile/*.sh
```

### 4. 测试

```bash
# 测试写作
./swarm/scripts/artgroup.sh "你好"

# 测试记忆
./memory-profile/memory.sh stats
```

---

## 配置 Cron 定时任务

```bash
# 编辑 crontab
crontab -e

# 添加以下行:
0 22 * * * /path/to/openclaw-swarm/memory-profile/memory.sh sync
45 22 * * * /path/to/openclaw-swarm/memory-profile/memory.sh reflect
0 22 * * 0 /path/to/openclaw-swarm/memory-profile/memory.sh gc
```

---

## 常见问题

### Q: API 调用失败

A: 检查环境变量是否正确配置

### Q: 记忆搜索不到

A: 运行 `./memory-profile/memory.sh gc` 清理缓存

### Q: 需要更多 Agent?

A: 修改 `swarm/scripts/agent.sh` 添加新的 Agent
