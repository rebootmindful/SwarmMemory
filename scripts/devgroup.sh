#!/bin/bash
# DevGroup - 开发工作流
# 多 Agent 协作流水线：规划 -> 开发 -> 测试

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TASK="$1"

if [ -z "$TASK" ]; then
    echo "用法: ./devgroup.sh \"任务描述\""
    exit 1
fi

echo "💻 [DevGroup] 开发工作流"
echo "   任务: $TASK"

# Stage 1: 规划
echo ""
echo "📋 Stage 1/3: 需求规划 (planner)"
PLAN=$(bash $SCRIPT_DIR/agent.sh planner "$TASK" 2>&1)

# Stage 2: 开发
echo ""
echo "⚡ Stage 2/3: 代码开发 (coder)"
CODE=$(bash $SCRIPT_DIR/agent.sh coder "$PLAN" 2>&1)

# Stage 3: 测试
echo ""
echo "🧪 Stage 3/3: 测试验证 (tester)"
TEST=$(bash $SCRIPT_DIR/agent.sh tester "$CODE" 2>&1)

echo ""
echo "========== 最终结果 =========="
echo "$TEST"
echo "================================"
