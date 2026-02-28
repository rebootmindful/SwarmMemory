#!/usr/bin/env python3
"""
自动决策 - 根据任务复杂度自动选择流程
"""
import re
from enum import Enum

class Complexity(Enum):
    SIMPLE = 1      # 简单任务
    MEDIUM = 2      # 中等任务
    COMPLEX = 3     # 复杂任务

class Decision:
    """决策器"""
    
    # 复杂度指标
    COMPLEXITY_KEYWORDS = {
        Complexity.SIMPLE: [
            "一句", "一句话", "短", "简单", "简洁",
            "什么", "什么是", "解释", "介绍"
        ],
        Complexity.MEDIUM: [
            "写", "文章", "分析", "总结",
            "开发", "设计", "实现"
        ],
        Complexity.COMPLEX: [
            "系统", "完整", "全面", "深入",
            "架构", "平台", "详细", "专业"
        ]
    }
    
    # 任务类型
    TASK_TYPES = {
        "rewrite": ["改写", "重写", "润色"],
        "write": ["写", "创作", "科普"],
        "analyze": ["分析", "研究", "探讨"],
        "develop": ["开发", "实现", "写代码"],
        "design": ["设计", "方案", "架构"],
        "review": ["审核", "审查", "检查"]
    }
    
    def __init__(self):
        self.history = []
    
    def analyze_complexity(self, task: str) -> Complexity:
        """分析任务复杂度"""
        task_lower = task.lower()
        
        # 简单指标
        simple_score = sum(1 for kw in self.COMPLEXITY_KEYWORDS[Complexity.SIMPLE] if kw in task_lower)
        medium_score = sum(1 for kw in self.COMPLEXITY_KEYWORDS[Complexity.MEDIUM] if kw in task_lower)
        complex_score = sum(1 for kw in self.COMPLEXITY_KEYWORDS[Complexity.COMPLEX] if kw in task_lower)
        
        # 长度指标
        length = len(task)
        if length < 20:
            simple_score += 2
        elif length > 100:
            complex_score += 1
        
        # 多任务指标
        separators = ["，", "和", "以及", "还有"]
        task_count = sum(task.count(s) for s in separators) + 1
        if task_count > 3:
            complex_score += 2
        
        # 决策
        if complex_score > medium_score and complex_score > simple_score:
            return Complexity.COMPLEX
        elif simple_score > medium_score:
            return Complexity.SIMPLE
        else:
            return Complexity.MEDIUM
    
    def identify_task_type(self, task: str) -> str:
        """识别任务类型"""
        task_lower = task.lower()
        for task_type, keywords in self.TASK_TYPES.items():
            if any(kw in task_lower for kw in keywords):
                return task_type
        return "write"  # 默认
    
    def decide_workflow(self, task: str) -> dict:
        """决策工作流"""
        complexity = self.analyze_complexity(task)
        task_type = self.identify_task_type(task)
        
        # 根据复杂度和类型决定
        decision = {
            "complexity": complexity.value,
            "task_type": task_type,
            "agents": [],
            "iterations": 1,
            "need_review": True,
            "need_parallel": False
        }
        
        # 简单任务
        if complexity == Complexity.SIMPLE:
            decision["agents"] = ["m25", "dsr"]
            decision["iterations"] = 1
            decision["need_review"] = False
        
        # 中等任务
        elif complexity == Complexity.MEDIUM:
            if task_type in ["write", "rewrite"]:
                decision["agents"] = ["m25", "gpt53", "dsr"]
                decision["iterations"] = 1
            elif task_type in ["develop", "design"]:
                decision["agents"] = ["m25plan", "gpt53review", "g53dev"]
                decision["iterations"] = 1
        
        # 复杂任务
        else:  # COMPLEX
            if task_type in ["write", "analyze"]:
                decision["agents"] = ["m25", "gpt53", "m25", "dsr"]  # 两轮
                decision["iterations"] = 2
                decision["need_review"] = True
            elif task_type == "develop":
                decision["agents"] = ["m25plan", "gpt53review", "g53dev", "dsrtdd"]
                decision["iterations"] = 1
                decision["need_review"] = True
        
        # 特殊判断
        if any(kw in task for kw in ["并发", "同时", "并行"]):
            decision["need_parallel"] = True
        
        return decision
    
    def explain(self, decision: dict) -> str:
        """解释决策"""
        complexity_names = {1: "简单", 2: "中等", 3: "复杂"}
        
        return f"""决策分析:
- 任务复杂度: {complexity_names[decision['complexity']]}
- 任务类型: {decision['task_type']}
- 使用 Agent: {' → '.join(decision['agents'])}
- 迭代次数: {decision['iterations']}
- 需要审核: {'是' if decision['need_review'] else '否'}
- 并行执行: {'是' if decision['need_parallel'] else '否'}"""

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "写一篇文章"
    
    dec = Decision()
    result = dec.decide_workflow(task)
    print(dec.explain(result))
