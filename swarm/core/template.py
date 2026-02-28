#!/usr/bin/env python3
"""
模板系统 - 预定义任务模板
"""
import json
import os
import yaml

TEMPLATE_DIR = os.path.expanduser("~/.openclaw/swarm")

# ArtGroup 模板
ARTGROUP_TEMPLATES = {
    "技术文章": {
        "workflow": "artgroup",
        "description": "写一篇技术文章",
        "default_task": "写一篇关于{topic}的技术文章，要求专业但易懂",
        "agents": ["m25", "gpt53", "dsr"],
        "iterations": 2
    },
    "观点文": {
        "workflow": "artgroup",
        "description": "写一篇观点文章",
        "default_task": "写一篇关于{topic}的观点文章，要求有独特见解",
        "agents": ["m25", "gpt53", "dsr"],
        "iterations": 2
    },
    "科普": {
        "workflow": "artgroup",
        "description": "写一篇科普文章",
        "default_task": "用通俗易懂的语言解释{topic}",
        "agents": ["m25", "dsr"],
        "iterations": 1
    }
}

# DevGroup 模板
DEVGROUP_TEMPLATES = {
    "api设计": {
        "workflow": "devgroup",
        "description": "设计API接口",
        "default_task": "设计{topic}的API接口方案",
        "agents": ["m25plan", "gpt53review", "g53dev", "dsrtdd"],
        "iterations": 2
    },
    "功能开发": {
        "workflow": "devgroup",
        "description": "开发功能模块",
        "default_task": "开发{topic}功能模块",
        "agents": ["m25plan", "gpt53review", "g53dev", "dsrtdd"],
        "iterations": 2
    },
    "代码审查": {
        "workflow": "devgroup",
        "description": "代码审查",
        "default_task": "审查以下代码: {code}",
        "agents": ["gpt53review"],
        "iterations": 1
    }
}

def load_templates(workflow):
    """加载模板"""
    templates = ARTGROUP_TEMPLATES if workflow == "artgroup" else DEVGROUP_TEMPLATES
    
    # 检查自定义模板
    custom_path = f"{TEMPLATE_DIR}/{workflow}/templates/custom.yaml"
    if os.path.exists(custom_path):
        with open(custom_path) as f:
            custom = yaml.safe_load(f) or {}
            templates.update(custom)
    
    return templates

def list_templates(workflow):
    """列出模板"""
    return list(load_templates(workflow).keys())

def get_template(workflow, name):
    """获取模板"""
    templates = load_templates(workflow)
    return templates.get(name)

def apply_template(workflow, name, params):
    """应用模板"""
    template = get_template(workflow, name)
    if not template:
        return None
    
    task = template["default_task"].format(**params)
    return {
        "template": name,
        "task": task,
        "agents": template["agents"],
        "iterations": template["iterations"]
    }

if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else "artgroup"
    print(f"可用模板: {list_templates(workflow)}")
