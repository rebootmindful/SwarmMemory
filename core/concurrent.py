#!/usr/bin/env python3
"""
并发执行模块 - 并行运行独立任务
"""
import concurrent.futures
import time
from dataclasses import dataclass
from typing import List, Callable, Any
import json

@dataclass
class Task:
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}

class ConcurrentRunner:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run(self, tasks: List[Task], show_progress=True):
        """并发执行任务"""
        self.start_time = time.time()
        self.results = {}
        
        if show_progress:
            print(f"🚀 启动 {len(tasks)} 个并发任务 (最多{self.max_workers}个并行)")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(task.func, *task.args, **task.kwargs): task 
                for task in tasks
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    self.results[task.name] = {
                        "status": "success",
                        "result": result,
                        "time": time.time() - self.start_time
                    }
                    if show_progress:
                        print(f"  ✅ {task.name} 完成 ({self.results[task.name]['time']:.1f}s)")
                except Exception as e:
                    self.results[task.name] = {
                        "status": "error",
                        "error": str(e),
                        "time": time.time() - self.start_time
                    }
                    if show_progress:
                        print(f"  ❌ {task.name} 失败: {e}")
        
        self.end_time = time.time()
        return self.results
    
    def get_result(self, name):
        return self.results.get(name, {}).get("result")
    
    def summary(self):
        total = len(self.results)
        success = sum(1 for r in self.results.values() if r["status"] == "success")
        elapsed = self.end_time - self.start_time if self.end_time else 0
        
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "elapsed": elapsed
        }

# 便捷函数
def run_parallel(*tasks):
    """并行运行多个任务"""
    runner = ConcurrentRunner(max_workers=len(tasks))
    return runner.run(tasks)

if __name__ == "__main__":
    # 测试
    def task1():
        time.sleep(1)
        return "任务1结果"
    
    def task2():
        time.sleep(1)
        return "任务2结果"
    
    def task3():
        time.sleep(1)
        return "任务3结果"
    
    runner = ConcurrentRunner(max_workers=3)
    results = runner.run([
        Task("t1", task1),
        Task("t2", task2),
        Task("t3", task3)
    ])
    print(f"\n总结: {json.dumps(runner.summary(), indent=2)}")
