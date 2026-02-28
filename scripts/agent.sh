#!/bin/bash
# 通用 Agent 调用器
# 支持多种 LLM 提供商

AGENT="$1"
TASK="$2"

# 默认使用环境变量中的 API
API_KEY="${OPENAI_API_KEY:-}"
API_BASE="${OPENAI_BASE_URL:-https://api.openai.com/v1}"
MODEL="${OPENAI_MODEL:-gpt-4}"

call_api() {
    local prompt="$1"
    local model="$2"
    
    curl -s "$API_BASE/chat/completions" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"$model\", \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}], \"max_tokens\": 4000}" \
        2>/dev/null | jq -r '.choices[0].message.content' 2>/dev/null || echo "API 调用失败"
}

case "$AGENT" in
    wand)
        echo "🎨 生成初稿中..."
        call_api "你是一个专业作家。请根据以下任务生成初稿：$TASK" "gpt-4o"
        ;;
    review)
        echo "✏️ 审核润色中..."
        call_api "你是一个专业编辑。请审核并润色以下内容：$TASK" "gpt-4o"
        ;;
    final)
        echo "🎯 终审优化中..."
        call_api "你是一个内容优化专家。请做最终优化：$TASK" "gpt-4o"
        ;;
    planner)
        echo "📋 规划中..."
        call_api "你是一个技术架构师。请规划这个任务：$TASK" "gpt-4o"
        ;;
    coder)
        echo "⚡ 开发中..."
        call_api "你是一个专业程序员。请实现：$TASK" "gpt-4o"
        ;;
    tester)
        echo "🧪 测试中..."
        call_api "你是一个测试工程师。请验证：$TASK" "gpt-4o"
        ;;
    *)
        echo "未知 Agent: $AGENT"
        exit 1
        ;;
esac
