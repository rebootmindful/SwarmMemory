#!/usr/bin/env python3
"""意图识别模块"""
import json
import re
from enum import Enum

class Intent(Enum):
    WRITE = "write"
    REWRITE = "rewrite"
    SUMMARY = "summary"
    EXPAND = "expand"
    ANALYZE = "analyze"
    EXPLAIN = "explain"
    CREATE = "create"
    DESIGN = "design"
    DEVELOP = "develop"
    DEBUG = "debug"
    REVIEW = "review"
    OPTIMIZE = "optimize"
    QUESTION = "question"
    UNKNOWN = "unknown"

INTENT_RULES = {
    (Intent.WRITE,): ["写", "文章", "博客", "写一篇"],
    (Intent.REWRITE,): ["改写", "重写", "润色", "改"],
    (Intent.SUMMARY,): ["总结", "摘要", "概括"],
    (Intent.EXPAND,): ["扩展", "展开", "详细"],
    (Intent.ANALYZE,): ["分析", "剖析", "解读"],
    (Intent.EXPLAIN,): ["解释", "说明", "讲解", "什么是"],
    (Intent.CREATE,): ["创作", "创造"],
    (Intent.DESIGN,): ["设计", "方案", "架构"],
    (Intent.DEVELOP,): ["开发", "实现", "写代码"],
    (Intent.DEBUG,): ["调试", "修复", "bug", "错误"],
    (Intent.REVIEW,): ["审查", "审核", "检查"],
    (Intent.OPTIMIZE,): ["优化", "性能", "改进"],
}

DOMAINS = {
    "技术": ["AI", "代码", "编程", "技术"],
    "金融": ["投资", "股票", "理财", "金融"],
    "心理": ["心理", "情绪", "意识", "荣格"],
    "健康": ["健康", "养生", "身体"],
}

def identify_intent(task):
    task_lower = task.lower()
    for intents, keywords in INTENT_RULES.items():
        for kw in keywords:
            if kw in task_lower:
                return intents[0].value, kw
    return Intent.UNKNOWN.value, None

def identify_domain(task):
    for domain, keywords in DOMAINS.items():
        for kw in keywords:
            if kw in task:
                return domain
    return "通用"

def extract_params(task):
    params = {}
    length_match = re.search(r'(\d+)[字篇段]', task)
    if length_match:
        params["length"] = int(length_match.group(1))
    if "荣格" in task:
        params["style"] = "荣格式叙事"
    return params

def analyze(task):
    intent, match_keyword = identify_intent(task)
    return {
        "intent": intent,
        "match_keyword": match_keyword,
        "domain": identify_domain(task),
        "params": extract_params(task)
    }

if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "写文章"
    print(json.dumps(analyze(task), indent=2, ensure_ascii=False))
