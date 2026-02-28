#!/usr/bin/env python3
"""
偏好学习模块 - 根据执行效果自动更新偏好
"""
import json
import os
import yaml
from datetime import datetime

MEMORY_FILE = os.path.expanduser("~/.openclaw/skills/memory-profile/MEMORY.yaml")
PREFERENCE_DIR = os.path.expanduser("~/.openclaw/swarm/preferences")

class PreferenceLearner:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.pref_dir = PREFERENCE_DIR
        os.makedirs(PREFERENCE_DIR, exist_ok=True)
    
    def load_memory(self):
        """加载 memory profile"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file) as f:
                return yaml.safe_load(f)
        return {}
    
    def save_memory(self, data):
        """保存 memory profile"""
        with open(self.memory_file, "w") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    def update_from_feedback(self, workflow, agent_scores: dict):
        """根据反馈更新偏好"""
        memory = self.load_memory()
        
        # 初始化
        if "preferences" not in memory:
            memory["preferences"] = {}
        if "behavior" not in memory["preferences"]:
            memory["preferences"]["behavior"] = {}
        
        # 根据 Agent 表现调整
        for agent, score in agent_scores.items():
            weight = min(1.0, score / 5.0)  # 归一化
            
            if agent in ["m25", "m25plan"]:
                # 写作/方案风格
                if score >= 4:
                    memory["preferences"]["behavior"]["detail_level"] = "详细"
                elif score <= 2:
                    memory["preferences"]["behavior"]["detail_level"] = "简洁"
            
            elif agent in ["gpt53", "gpt53review"]:
                # 审核严格度
                if score >= 4:
                    memory["preferences"]["behavior"]["review_strictness"] = "严格"
                else:
                    memory["preferences"]["behavior"]["review_strictness"] = "宽松"
            
            elif agent in ["dsr", "dsrtdd"]:
                # 创意程度
                if score >= 4:
                    memory["preferences"]["behavior"]["creativity"] = "高"
                else:
                    memory["preferences"]["behavior"]["creativity"] = "保守"
        
        # 更新时间
        memory["preferences"]["updated"] = datetime.now().isoformat()
        
        # 保存
        self.save_memory(memory)
        
        return memory
    
    def get_task_preferences(self, task_type: str) -> dict:
        """根据任务类型获取偏好"""
        memory = self.load_memory()
        
        # 默认偏好
        prefs = {
            "writing_style": "荣格式叙事",
            "tone": "专业但易懂",
            "length": "中等"
        }
        
        # 从 memory 读取
        behavior = memory.get("preferences", {}).get("behavior", {})
        
        if task_type == "rewrite":
            prefs["focus"] = behavior.get("detail_level", "保持原风格")
        elif task_type == "develop":
            prefs["focus"] = behavior.get("code_style", "简洁规范")
        elif task_type == "analyze":
            prefs["focus"] = behavior.get("analysis_depth", "深入分析")
        
        return prefs
    
    def suggest_agent_combo(self, task_type: str, feedback_scores: dict) -> list:
        """根据反馈建议 Agent 组合"""
        # 基础组合
        combos = {
            "write": ["m25", "gpt53", "dsr"],
            "rewrite": ["m25", "dsr"],
            "develop": ["m25plan", "g53dev", "dsrtdd"],
            "review": ["gpt53review"]
        }
        
        base = combos.get(task_type, ["m25", "dsr"])
        
        # 根据评分调整
        adjusted = []
        for agent in base:
            score = feedback_scores.get(agent, 3)
            
            # 低分Agent换掉
            if score <= 2:
                if agent == "m25":
                    adjusted.append("dsr")
                elif agent == "gpt53":
                    adjusted.append("dsr")
                else:
                    adjusted.append(agent)
            else:
                adjusted.append(agent)
        
        return adjusted if adjusted else base

if __name__ == "__main__":
    learner = PreferenceLearner()
    
    # 测试
    print("当前偏好:", learner.get_task_preferences("write"))
    
    # 模拟更新
    print("\n模拟更新偏好...")
    learner.update_from_feedback("artgroup", {"m25": 4, "gpt53": 3, "dsr": 5})
    print("更新后偏好:", learner.get_task_preferences("write"))
