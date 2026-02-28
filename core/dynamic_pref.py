#!/usr/bin/env python3
"""
动态偏好注入 - 智能风格匹配
"""
import os
import yaml

STYLES_FILE = "/home/user/.openclaw/swarm/artgroup/styles.yaml"

class DynamicPreference:
    def __init__(self):
        self.load_styles()
    
    def load_styles(self):
        if os.path.exists(STYLES_FILE):
            with open(STYLES_FILE) as f:
                data = yaml.safe_load(f)
                self.styles = data.get("styles", {})
        else:
            self.styles = {}
    
    def identify_style(self, task: str) -> str:
        """根据任务识别风格 - 优先级匹配"""
        task_lower = task.lower()
        
        # 优先级规则 (新风格优先)
        priority_rules = [
            # 新增风格
            ("生物主权", ["生物主权", "主权", "算法殖民", "夺回", "生存"]),
            ("system0123", ["system 0", "system0", "system 1", "system2", "system3", "预测误差", "认知框架"]),
            ("升级人类", ["升级人类", "外挂", "认知扩展", "人机融合"]),
            ("具身认知", ["具身", "身体认知", "身体传感器"]),
            # 原有风格
            ("技术文档", ["技术", "代码", "接口", "模块", "API", "架构", "Swarm", "文档"]),
            ("科普", ["科普", "解释", "什么是", "原理", "为什么", "介绍"]),
            ("对话式", ["对话", "聊天", "你说", "咱们", "写给"]),
            ("科幻未来", ["未来", "AI时代", "人类将", "将会", "预测", "趋势"]),
            ("科学实证", ["实验", "研究", "数据", "证明", "实证"]),
            ("心理学", ["心理", "情绪", "意识", "潜意识", "抑郁", "焦虑"]),
            ("观点评论", ["观点", "评论", "我认为", "应该", "批判"]),
            ("荣格式叙事", ["荣格", "原型", "无意识", "命运", "觉醒", "心理"])
        ]
        
        for style_name, keywords in priority_rules:
            for kw in keywords:
                if kw in task_lower:
                    return style_name
        
        return "荣格式叙事"  # 默认
    
    def get_preferences(self, task: str, task_type: str = None) -> dict:
        style_name = self.identify_style(task)
        style = self.styles.get(style_name, self.styles.get("荣格式叙事", {}))
        
        return {
            "style": style_name,
            "description": style.get("description", ""),
            "tone": style.get("tone", "专业但易懂"),
            "length": style.get("length", "中等"),
            "structure": style.get("structure", ""),
            "focus": self.get_focus(task_type)
        }
    
    def get_focus(self, task_type: str) -> str:
        focuses = {
            "rewrite": "保持原风格基础上优化",
            "write": "清晰表达核心观点",
            "develop": "简洁规范的代码",
            "analyze": "深入分析问题",
            "review": "指出问题和建议"
        }
        return focuses.get(task_type, "清晰表达")
    
    def build_prompt(self, task: str) -> str:
        prefs = self.get_preferences(task)
        
        prompt = f"""请用【{prefs['style']}】风格撰写。
{prefs['description']}
语气: {prefs['tone']}
长度: {prefs['length']}
结构: {prefs.get('structure', '')}
重点: {prefs['focus']}

任务: {task}"""
        
        return prompt

if __name__ == "__main__":
    dp = DynamicPreference()
    
    tests = [
        "夺回生物主权",
        "什么是System 0",
        "用System 0/1/2/3解释AI",
        "升级人类认知",
        "具身认知是什么",
        "写一篇关于AI的文章",
        "科普量子计算",
    ]
    
    print("=== 风格识别测试 ===\n")
    for t in tests:
        prefs = dp.get_preferences(t)
        print(f"📝 {t}")
        print(f"   → 风格: {prefs['style']}")
        print(f"   → 语气: {prefs['tone']}")
        print(f"   → 结构: {prefs.get('structure', '')}")
        print()
