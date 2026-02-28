#!/usr/bin/env python3
"""
自动路由 - 根据任务类型选择工作流
"""
import re

RULES = {
    "artgroup": [
        "写", "文章", "博客", "文案", "内容", "科普",
        "观点", "评论", "分析", "解读", "总结", "报告",
        "小说", "故事", "脚本", "台词",
        "改写", "重写", "精简", "扩展", "润色"
    ],
    "devgroup": [
        "开发", "代码", "功能", "接口", "API", "设计",
        "架构", "模块", "修复", "bug", "优化", "重构",
        "测试", "部署", "配置", "安装"
    ]
}

def classify_task(task):
    task_lower = task.lower()
    
    artgroup_score = sum(1 for w in RULES["artgroup"] if w in task_lower)
    devgroup_score = sum(1 for w in RULES["devgroup"] if w in task_lower)
    
    if artgroup_score > devgroup_score:
        return "artgroup"
    elif devgroup_score > artgroup_score:
        return "devgroup"
    else:
        return "artgroup"

def get_agent_sequence(workflow, task):
    task_lower = task.lower()
    
    # 改写类任务
    if any(w in task_lower for w in ["改写", "重写", "精简", "扩展"]):
        return ["m25", "gpt53", "dsr"]
    
    # 简单任务
    if any(w in task_lower for w in ["短", "一句话", "简单"]):
        return ["m25", "dsr"]
    
    # 标准流程
    if workflow == "artgroup":
        return ["m25", "gpt53", "dsr"]
    else:
        if any(w in task_lower for w in ["审查", "review", "检查"]):
            return ["gpt53review"]
        return ["m25plan", "gpt53review", "g53dev", "dsrtdd"]

def suggest_template(task):
    task_lower = task.lower()
    
    # 改写类
    if any(w in task_lower for w in ["改写", "重写"]):
        return "改写"
    elif "精简" in task_lower:
        return "精简"
    elif "扩展" in task_lower:
        return "扩展"
    
    # 文章类
    if any(w in task_lower for w in ["技术", "科普"]):
        return "技术文章"
    elif any(w in task_lower for w in ["观点", "评论"]):
        return "观点文"
    elif any(w in task_lower for w in ["解释", "了解"]):
        return "科普"
    
    # 开发类
    if any(w in task_lower for w in ["api", "接口"]):
        return "api设计"
    elif any(w in task_lower for w in ["开发", "功能", "模块"]):
        return "功能开发"
    elif any(w in task_lower for w in ["审查", "review"]):
        return "代码审查"
    
    return None

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "写一篇关于AI的文章"
    
    workflow = classify_task(task)
    agents = get_agent_sequence(workflow, task)
    template = suggest_template(task)
    
    print(f"任务: {task}")
    print(f"工作流: {workflow}")
    print(f"Agent序列: {agents}")
    print(f"建议模板: {template}")
