import sys
sys.path.insert(0, "/home/user/.openclaw/swarm")
from core.dynamic_pref import DynamicPreference

dp = DynamicPreference()

# 检查加载的风格
print(f"已加载风格数量: {len(dp.styles)}")
print(f"风格列表: {list(dp.styles.keys())}")

print("\n=== 风格识别测试 ===\n")

tests = [
    "夺回生物主权",
    "什么是System 0",
    "用System 0/1/2/3解释AI",
    "升级人类认知",
    "具身认知是什么",
]

for t in tests:
    prefs = dp.get_preferences(t)
    print(f"📝 {t}")
    print(f"   → 风格: {prefs['style']}")
    print(f"   → 语气: {prefs['tone']}")
    print()
