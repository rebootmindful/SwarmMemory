#!/usr/bin/env python3
"""
Discord 集成 - 在 Discord 触发 Swarm 任务
"""
import os
import json
import asyncio
from pathlib import Path

# OpenClaw Discord 配置
DISCORD_CONFIG = {
    "command_prefix": "swarm:",
    "workflows": {
        "artgroup": {
            "keywords": ["写", "文章", "改写", "分析"],
            "command": "artgroup"
        },
        "devgroup": {
            "keywords": ["开发", "代码", "设计", "debug"],
            "command": "devgroup"
        }
    }
}

SWARM_DIR = Path.home() / ".openclaw/swarm"

def handle_message(content, user_id):
    """处理 Discord 消息"""
    
    # 检查是否是 Swarm 命令
    if not content.startswith(DISCORD_CONFIG["command_prefix"]):
        return None
    
    # 解析命令
    command = content[len(DISCORD_CONFIG["command_prefix"]):].strip()
    
    # 解析任务
    parts = command.split(" ", 1)
    workflow = parts[0] if parts else "artgroup"
    task = parts[1] if len(parts) > 1 else ""
    
    return {
        "workflow": workflow,
        "task": task,
        "user": user_id,
        "status": "pending"
    }

async def run_workflow(workflow, task):
    """运行工作流"""
    import subprocess
    
    if workflow == "artgroup":
        cmd = f"{SWARM_DIR}/scripts/artgroup.sh '{task}'"
    elif workflow == "devgroup":
        cmd = f"{SWARM_DIR}/scripts/devgroup.sh '{task}'"
    else:
        return {"error": f"未知工作流: {workflow}"}
    
    # 执行
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    return {
        "workflow": workflow,
        "task": task,
        "output": result.stdout[:2000],
        "success": result.returncode == 0
    }

# CLI 接口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: discord_bot.py <消息> [用户ID]")
        sys.exit(1)
    
    msg = sys.argv[1]
    user = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    
    # 处理
    result = handle_message(msg, user)
    
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("不是有效的 Swarm 命令")
