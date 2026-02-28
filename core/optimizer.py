#!/usr/bin/env python3
"""
学习优化模块 - 根据历史成功率调整 Agent 组合
"""
import json
import os
from datetime import datetime
from collections import defaultdict

LEARN_DIR = os.path.expanduser("~/.openclaw/swarm/learn")

class Optimizer:
    def __init__(self, workflow):
        self.workflow = workflow
        self.stats_file = f"{LEARN_DIR}/{workflow}_stats.json"
        self.load()
    
    def load(self):
        os.makedirs(LEARN_DIR, exist_ok=True)
        if os.path.exists(self.stats_file):
            with open(self.stats_file) as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "agent_combinations": {},
                "template_performance": {},
                "task_types": {}
            }
    
    def save(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def record(self, agents, task_type, score):
        """记录执行结果"""
        combo = "+".join(agents)
        
        if combo not in self.stats["agent_combinations"]:
            self.stats["agent_combinations"][combo] = {"total": 0, "scores": []}
        
        self.stats["agent_combinations"][combo]["total"] += 1
        self.stats["agent_combinations"][combo]["scores"].append(score)
        
        # 任务类型统计
        if task_type not in self.stats["task_types"]:
            self.stats["task_types"][task_type] = {"total": 0, "scores": []}
        self.stats["task_types"][task_type]["total"] += 1
        self.stats["task_types"][task_type]["scores"].append(score)
        
        self.save()
    
    def get_best_combo(self, task_type=None):
        """获取最佳组合"""
        combos = self.stats.get("agent_combinations", {})
        
        if not combos:
            return None
        
        best_combo = None
        best_avg = 0
        
        for combo, data in combos.items():
            scores = data.get("scores", [])
            if scores:
                avg = sum(scores) / len(scores)
                if avg > best_avg:
                    best_avg = avg
                    best_combo = combo
        
        return best_combo, best_avg
    
    def suggest_improvements(self):
        """建议改进"""
        suggestions = []
        
        # 分析最差的组合
        combos = self.stats.get("agent_combinations", {})
        for combo, data in combos.items():
            scores = data.get("scores", [])
            if scores and len(scores) >= 3:
                avg = sum(scores) / len(scores)
                if avg < 60:
                    suggestions.append(f"组合 {combo} 表现较差 (平均{avg:.0f}分)，建议更换")
        
        # 分析任务类型
        task_types = self.stats.get("task_types", {})
        for task_type, data in task_types.items():
            scores = data.get("scores", [])
            if scores and len(scores) >= 3:
                avg = sum(scores) / len(scores)
                if avg < 70:
                    suggestions.append(f"任务类型 {task_type} 表现较差，考虑优化模板")
        
        return suggestions
    
    def get_stats(self):
        return {
            "total_runs": sum(d.get("total", 0) for d in self.stats.get("agent_combinations", {}).values()),
            "best_combo": self.get_best_combo(),
            "suggestions": self.suggest_improvements()
        }

if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else "artgroup"
    opt = Optimizer(workflow)
    print(json.dumps(opt.get_stats(), indent=2, ensure_ascii=False))
