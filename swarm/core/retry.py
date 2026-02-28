#!/usr/bin/env python3
"""
失败重试 - 自动换 Agent 重试
"""
import time
import json
from datetime import datetime
from typing import List, Callable, Optional

RETRY_DIR = "/tmp/swarm_retry"

class RetryConfig:
    """重试配置"""
    
    # 失败类型和应对策略
    STRATEGIES = {
        "timeout": ["换更快的模型", "减少内容长度"],
        "quality_low": ["换审核Agent", "增加迭代次数"],
        "api_error": ["换API", "等待后重试"],
        "rate_limit": ["等待", "换模型"]
    }
    
    # Agent 备选池
    AGENT_POOL = {
        "m25": ["m25", "dsr"],
        "gpt53": ["gpt53", "dsr"],
        "dsr": ["dsr", "gpt53"],
        "m25plan": ["m25plan", "dsr"],
        "gpt53review": ["gpt53review", "dsrtdd"],
        "g53dev": ["g53dev", "dsr"],
        "dsrtdd": ["dsrtdd", "g53dev"]
    }
    
    # 默认重试次数
    DEFAULT_MAX_RETRIES = 3

class RetryHandler:
    """重试处理器"""
    
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
        self.config = RetryConfig()
        self.history = []
    
    def analyze_error(self, error: str) -> str:
        """分析错误类型"""
        error_lower = error.lower()
        
        if "timeout" in error_lower or "超时" in error:
            return "timeout"
        elif "rate limit" in error_lower or "限流" in error:
            return "rate_limit"
        elif "api" in error_lower or "错误" in error:
            return "api_error"
        elif "质量" in error or "不好" in error or "差" in error:
            return "quality_low"
        else:
            return "unknown"
    
    def get_alternative_agent(self, agent: str, error_type: str) -> str:
        """获取备选 Agent"""
        pool = self.config.AGENT_POOL.get(agent, [agent])
        
        # 如果是质量相关错误，优先换审核Agent
        if error_type == "quality_low":
            if "gpt53" in agent:
                return "gpt53review"
            elif "dsr" in agent:
                return "dsrtdd"
        
        # 否则用备选
        if len(pool) > 1:
            return pool[1]
        return agent
    
    def get_strategy(self, error_type: str) -> List[str]:
        """获取应对策略"""
        return self.config.STRATEGIES.get(error_type, ["换Agent重试"])
    
    def execute_with_retry(self, agent: str, task: str, execute_func: Callable) -> dict:
        """带重试的执行"""
        attempts = []
        current_agent = agent
        error_type = None
        
        for attempt in range(self.max_retries):
            try:
                print(f"  尝试 {attempt + 1}/{self.max_retries} (Agent: {current_agent})")
                
                result = execute_func(current_agent, task)
                
                # 成功
                return {
                    "success": True,
                    "agent": current_agent,
                    "result": result,
                    "attempts": attempts
                }
            
            except Exception as e:
                error_str = str(e)
                error_type = self.analyze_error(error_str)
                
                attempts.append({
                    "attempt": attempt + 1,
                    "agent": current_agent,
                    "error": error_str[:100],
                    "error_type": error_type
                })
                
                # 获取备选 Agent
                current_agent = self.get_alternative_agent(agent, error_type)
                
                # 等待后重试
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待
                    print(f"  ⏳ 等待 {wait_time}s 后重试...")
                    time.sleep(wait_time)
        
        # 全部失败
        return {
            "success": False,
            "agent": current_agent,
            "error": error_type,
            "attempts": attempts,
            "strategies": self.get_strategy(error_type)
        }
    
    def save_history(self, workflow: str, result: dict):
        """保存历史"""
        import os
        os.makedirs(RETRY_DIR, exist_ok=True)
        
        history_file = f"{RETRY_DIR}/{workflow}_history.json"
        
        if os.path.exists(history_file):
            with open(history_file) as f:
                history = json.load(f)
        else:
            history = []
        
        history.append({
            "time": datetime.now().isoformat(),
            "result": result
        })
        
        # 只保留最近100条
        history = history[-100:]
        
        with open(history_file, "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 测试
    def mock_execute(agent, task):
        if "fail" in task.lower():
            raise Exception("模拟失败")
        return f"{agent} 执行结果: {task}"
    
    handler = RetryHandler(max_retries=2)
    
    # 成功案例
    result = handler.execute_with_retry("m25", "写一句测试", mock_execute)
    print(f"成功: {result['success']}")
    
    # 失败案例
    result = handler.execute_with_retry("m25", "模拟失败", mock_execute)
    print(f"失败: {result['success']}, 策略: {result.get('strategies')}")
