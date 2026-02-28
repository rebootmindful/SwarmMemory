#!/usr/bin/env python3
"""
用户反馈模块 - 收集评价并更新偏好
"""
import json
import os
from datetime import datetime
from typing import Dict, List

FEEDBACK_DIR = os.path.expanduser("~/.openclaw/swarm/feedback")

class Feedback:
    def __init__(self, workflow):
        self.workflow = workflow
        self.file = f"{FEEDBACK_DIR}/{workflow}_feedback.json"
        self.load()
    
    def load(self):
        os.makedirs(FEEDBACK_DIR, exist_ok=True)
        if os.path.exists(self.file):
            with open(self.file) as f:
                self.data = json.load(f)
        else:
            self.data = {"feedbacks": [], "scores": {}}
    
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add(self, task: str, agent: str, score: int, comment: str = ""):
        """添加反馈"""
        feedback = {
            "task": task[:100],
            "agent": agent,
            "score": score,  # 1-5 分
            "comment": comment,
            "time": datetime.now().isoformat()
        }
        self.data["feedbacks"].append(feedback)
        
        # 统计
        if agent not in self.data["scores"]:
            self.data["scores"][agent] = {"total": 0, "sum": 0}
        
        self.data["scores"][agent]["total"] += 1
        self.data["scores"][agent]["sum"] += score
        
        self.save()
        return feedback
    
    def get_agent_score(self, agent: str) -> float:
        """获取 Agent 平均分"""
        if agent not in self.data["scores"]:
            return 3.0  # 默认
        s = self.data["scores"][agent]
        return s["sum"] / s["total"] if s["total"] > 0 else 3.0
    
    def get_best_agent(self, task_type: str = None) -> str:
        """获取最佳 Agent"""
        scores = self.data.get("scores", {})
        if not scores:
            return None
        
        best = max(scores.items(), key=lambda x: x[1]["sum"]/x[1]["total"] if x[1]["total"] > 0 else 0)
        return best[0]
    
    def get_stats(self) -> dict:
        return {
            "total": len(self.data["feedbacks"]),
            "agent_scores": {
                agent: round(s["sum"]/s["total"], 2) if s["total"] > 0 else 0
                for agent, s in self.data.get("scores", {}).items()
            },
            "best_agent": self.get_best_agent()
        }

# 快速评分
def quick_score(workflow, score):
    """快速评分接口"""
    f = Feedback(workflow)
    return f.add("快速评价", "last_agent", score)

if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else "artgroup"
    f = Feedback(workflow)
    print(json.dumps(f.get_stats(), indent=2, ensure_ascii=False))
