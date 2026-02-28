#!/usr/bin/env python3
"""
缓存层 - 避免重复执行相同任务
"""
import json
import os
import hashlib
from datetime import datetime, timedelta

CACHE_DIR = os.path.expanduser("~/.openclaw/swarm/cache")

class Cache:
    def __init__(self, ttl_hours=24):
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    def _key(self, task, workflow):
        return hashlib.sha256(f"{workflow}:{task}".encode()).hexdigest()[:16]
    
    def get(self, task, workflow):
        """获取缓存"""
        key = self._key(task, workflow)
        path = f"{CACHE_DIR}/{workflow}_{key}.json"
        
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            
            # 检查过期
            created = datetime.fromisoformat(data["created"])
            if datetime.now() - created < self.ttl:
                return data["result"]
            else:
                os.remove(path)
        return None
    
    def set(self, task, workflow, result):
        """设置缓存"""
        key = self._key(task, workflow)
        path = f"{CACHE_DIR}/{workflow}_{key}.json"
        
        data = {
            "task": task,
            "result": result,
            "created": datetime.now().isoformat()
        }
        
        with open(path, "w") as f:
            json.dump(data, f)
        
        return True
    
    def clear(self, workflow=None):
        """清理缓存"""
        import glob
        pattern = f"{CACHE_DIR}/{workflow or '*'}_*.json"
        for f in glob.glob(pattern):
            os.remove(f)
        return True

if __name__ == "__main__":
    c = Cache()
    print(f"缓存目录: {CACHE_DIR}")
    print(f"清理缓存: {c.clear()}")
