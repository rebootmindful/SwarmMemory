#!/bin/bash
# Memory Profile - 自动记忆系统
# 
# 使用方式:
#   ./memory.sh init      - 初始化
#   ./memory.sh add       - 添加记忆
#   ./memory.sh search    - 搜索记忆
#   ./memory.sh stats     - 查看统计

CMD="$1"

case "$CMD" in
    init)
        echo "🧠 初始化记忆系统..."
        mkdir -p memory/{lessons,decisions,people,reflections}
        echo "# Memory Index" > memory/INDEX.md
        echo "✅ 初始化完成"
        ;;
    add)
        echo "📝 添加记忆..."
        node scripts/memory_system.cjs add "log" "$2"
        ;;
    search)
        echo "🔍 搜索记忆..."
        node scripts/memory_system.cjs query "$2"
        ;;
    stats)
        echo "📊 记忆统计..."
        node scripts/memory_system.cjs stats
        ;;
    reflect)
        echo "🌙 运行夜间反思..."
        node scripts/nightly_reflection.cjs
        ;;
    gc)
        echo "🗑️ 运行归档..."
        node scripts/forget_model.cjs run
        ;;
    *)
        echo "用法:"
        echo "  ./memory.sh init       - 初始化"
        echo "  ./memory.sh add <内容> - 添加记忆"
        echo "  ./memory.sh search <关键词> - 搜索"
        echo "  ./memory.sh stats      - 查看统计"
        echo "  ./memory.sh reflect   - 夜间反思"
        echo "  ./memory.sh gc        - 垃圾归档"
        ;;
esac
