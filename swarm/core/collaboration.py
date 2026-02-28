#!/usr/bin/env python3
"""
Agent 协作优化 - 智能上下文传递
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any

CONTEXT_DIR = os.path.expanduser("~/.openclaw/swarm/context")

class Context:
    """上下文管理器"""
    
    def __init__(self, workflow, task_id):
        self.workflow = workflow
        self.task_id = task_id
        self.file = f"{CONTEXT_DIR}/{workflow}_{task_id}.json"
        self.data = {
            "task": "",
            "steps": [],
            "shared": {},  # Agent 间共享的数据
            "created": datetime.now().isoformat()
        }
        self.load()
    
    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                self.data = json.load(f)
    
    def save(self):
        os.makedirs(CONTEXT_DIR, exist_ok=True)
        with open(self.file, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def set_task(self, task):
        self.data["task"] = task
        self.save()
    
    def add_step(self, agent, result, metadata=None):
        """添加执行步骤"""
        step = {
            "agent": agent,
            "result": result[:500] if len(result) > 500 else result,
            "metadata": metadata or {},
            "time": datetime.now().isoformat()
        }
        self.data["steps"].append(step)
        self.save()
        return step
    
    def share(self, key, value):
        """共享数据给下一个 Agent"""
        self.data["shared"][key] = value
        self.save()
    
    def get_shared(self, key):
        return self.data["shared"].get(key)
    
    def get_context_for_next(self, next_agent):
        """为下一个 Agent 准备上下文"""
        context = {
            "task": self.data["task"],
            "history": [],
            "shared": self.data["shared"]
        }
        
        # 提取相关历史
        for step in self.data["steps"]:
            context["history"].append({
                "agent": step["agent"],
                "summary": step["result"][:200]
            })
        
        return context
    
    def build_prompt(self, next_agent, task):
        """构建带上下文的 prompt"""
        ctx = self.get_context_for_next(next_agent)
        
        prompt = f"""任务: {ctx['task']}\n\n"""
        
        if ctx["history"]:
            prompt += "执行历史:\n"
            for h in ctx["history"]:
                prompt += f"- {h['agent']}: {h['summary']}...\n"
            prompt += "\n"
        
        if ctx["shared"]:
            prompt += "共享信息:\n"
            for k, v in ctx["shared"].items():
                prompt += f"- {k}: {v}\n"
            prompt += "\n"
        
        prompt += f"当前任务: {task}"
        
        return prompt

class AgentCollaboration:
    """Agent 协作器"""
    
    def __init__(self, workflow):
        self.workflow = workflow
    
    def create_context(self, task):
        task_id = f"{workflow}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return Context(self.workflow, task_id)
    
    def run_chain(self, agents: List[str], task: str, executor_func):
        """运行 Agent 链"""
        ctx = self.create_context(task)
        ctx.set_task(task)
        
        results = []
        
        for i, agent in enumerate(agents):
            # 构建上下文 prompt
            if i == 0:
                prompt = task
            else:
                prompt = ctx.build_prompt(agent, task)
            
            # 执行
            result = executor_func(agent, prompt)
            
            # 保存结果
            ctx.add_step(agent, result)
            
            # 提取共享信息
            if "方案" in result:
                ctx.share("last_plan", result[:200])
            if "代码" in result:
                ctx.share("last_code", result[:200])
            
            results.append({"agent": agent, "result": result})
        
        return results, ctx

if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else "artgroup"
    collab = AgentCollaboration(workflow)
    print(f"协作器已就绪: {workflow}")
