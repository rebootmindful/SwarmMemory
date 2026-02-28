#!/usr/bin/env python3
"""
模板自动更新 - 根据执行结果自动升级模板
"""
import json
import os
import yaml
from datetime import datetime
from collections import Counter

TEMPLATE_DIR = os.path.expanduser("~/.openclaw/swarm")

# 分析结果提取模式
def analyze_result(workflow, task, result, review):
    """分析结果，提取改进点"""
    
    patterns = {
        "artgroup": {
            "structure": ["开头", "正文", "结尾", "结构", "层次"],
            "style": ["简洁", "专业", "通俗", "生动"],
            "content": ["案例", "数据", "引用", "观点"]
        },
        "devgroup": {
            "code": ["函数", "类", "模块", "接口"],
            "quality": ["注释", "规范", "测试", "错误处理"],
            "design": ["架构", "模式", "优化", "性能"]
        }
    }
    
    # 简单关键词提取
    words = []
    text = f"{task} {result} {review}"
    
    for category, keywords in patterns.get(workflow, {}).items():
        for kw in keywords:
            if kw in text:
                words.append(kw)
    
    return {
        "keywords": words,
        "task_type": detect_type(task),
        "result_length": len(result),
        "reviewed": bool(review)
    }

def detect_type(task):
    """识别任务类型"""
    task_lower = task.lower()
    
    types = {
        "artgroup": {
            "技术": "技术文章",
            "观点": "观点文",
            "科普": "科普",
            "解释": "科普"
        },
        "devgroup": {
            "api": "api设计",
            "接口": "api设计",
            "开发": "功能开发",
            "功能": "功能开发",
            "审查": "代码审查"
        }
    }
    
    for wf, mapping in types.items():
        for kw, template in mapping.items():
            if kw in task_lower:
                return template
    
    return "默认"

def update_template(workflow, task_type, analysis):
    """更新模板"""
    
    # 加载现有模板
    template_file = f"{TEMPLATE_DIR}/{workflow}/templates/custom.yaml"
    
    if os.path.exists(template_file):
        with open(template_file) as f:
            templates = yaml.safe_load(f) or {}
    else:
        templates = {}
    
    # 检查是否需要创建新模板
    if task_type not in templates:
        templates[task_type] = {
            "workflow": workflow,
            "description": f"自动生成的{task_type}模板",
            "default_task": task_type,
            "agents": get_default_agents(workflow),
            "stats": {
                "created": datetime.now().isoformat(),
                "uses": 1,
                "improvements": []
            }
        }
    else:
        # 更新统计
        if "stats" not in templates[task_type]:
            templates[task_type]["stats"] = {"uses": 0, "improvements": []}
        
        templates[task_type]["stats"]["uses"] = templates[task_type]["stats"].get("uses", 0) + 1
        
        # 添加改进点
        if analysis.get("keywords"):
            templates[task_type]["stats"]["improvements"].append({
                "at": datetime.now().isoformat(),
                "keywords": analysis["keywords"]
            })
    
    # 保存
    os.makedirs(f"{TEMPLATE_DIR}/{workflow}/templates", exist_ok=True)
    with open(template_file, "w") as f:
        yaml.dump(templates, f, allow_unicode=True, default_flow_style=False)
    
    return templates

def get_default_agents(workflow):
    """获取默认Agent序列"""
    if workflow == "artgroup":
        return ["m25", "gpt53", "dsr"]
    else:
        return ["m25plan", "gpt53review", "g53dev", "dsrtdd"]

def suggest_template_improvement(workflow, task, result, review):
    """建议模板改进"""
    
    analysis = analyze_result(workflow, task, result, review)
    
    suggestions = []
    
    # 基于分析结果给出建议
    if len(result) > 5000:
        suggestions.append("考虑拆分成长文章模板")
    
    if not review:
        suggestions.append("建议默认使用审核Agent")
    
    if analysis.get("keywords"):
        suggestions.append(f"可添加关键词过滤: {analysis['keywords']}")
    
    return {
        "task_type": analysis["task_type"],
        "suggestions": suggestions,
        "analysis": analysis
    }

if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else "artgroup"
    
    # 测试
    result = suggest_template_improvement(
        workflow,
        "写一篇关于AI的技术文章",
        "这是文章内容" * 100,
        "审核通过"
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
