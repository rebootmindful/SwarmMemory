#!/bin/bash
# ArtGroup - 写作工作流
# 多 Agent 协作流水线：初稿 -> 审核 -> 终审
# 
# 使用方式: ./artgroup.sh "你的任务描述"

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_DIR="$SCRIPT_DIR/../core"
TASK="$1"

if [ -z "$TASK" ]; then
    echo "用法: ./artgroup.sh \"任务描述\""
    exit 1
fi

echo "🎨 [ArtGroup] 写作工作流"
echo "   任务: $TASK"

# Stage 1: 初稿生成 (wand)
echo ""
echo "📝 Stage 1/3: 初稿生成 (wand)"
DRAFT=$(bash $SCRIPT_DIR/agent.sh wand "$TASK" 2>&1)

# Stage 2: 审核润色 (review)
echo ""
echo "✏️ Stage 2/3: 审核润色 (review)"
REVIEW=$(bash $SCRIPT_DIR/agent.sh review "$DRAFT" 2>&1)

# Stage 3: 终审优化 (final)
echo ""
echo "🎯 Stage 3/3: 终审优化 (final)"
FINAL=$(bash $SCRIPT_DIR/agent.sh final "$REVIEW" 2>&1)

echo ""
echo "========== 最终结果 =========="
echo "$FINAL"
echo "================================"

# 保存结果
echo "$FINAL" >> ~/.openclaw/swarm/artgroup/results.log
