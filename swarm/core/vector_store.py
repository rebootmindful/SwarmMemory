#!/usr/bin/env python3
"""
向量记忆模块 - N-gram 语义相似度 (无需 API)
"""
import json
import os
import hashlib
import re
from datetime import datetime
from collections import Counter
import math

class VectorStore:
    def __init__(self, workflow):
        self.workflow = workflow
        self.store_file = os.path.expanduser(f"~/.openclaw/swarm/{workflow}/knowledge/vector.json")
        self.ngram_file = os.path.expanduser(f"~/.openclaw/swarm/{workflow}/knowledge/ngram.json")
        self.load()
    
    def load(self):
        if os.path.exists(self.store_file):
            with open(self.store_file) as f:
                self.data = json.load(f)
        else:
            self.data = {"entries": []}
        
        if os.path.exists(self.ngram_file):
            with open(self.ngram_file) as f:
                self.ngrams = json.load(f)
        else:
            self.ngrams = {"corpus": {}}
    
    def save(self):
        os.makedirs(os.path.dirname(self.store_file), exist_ok=True)
        with open(self.store_file, 'w') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        with open(self.ngram_file, 'w') as f:
            json.dump(self.ngrams, f, ensure_ascii=False, indent=2)
    
    def _tokenize(self, text):
        """中文分词 (简单按字符)"""
        return list(text.lower())
    
    def _get_ngrams(self, text, n=2):
        """获取N-gram"""
        tokens = self._tokenize(text)
        return set([''.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)])
    
    def _tf(self, text):
        """计算词频"""
        tokens = self._tokenize(text)
        counter = Counter(tokens)
        total = len(tokens)
        return {k: v/total for k, v in counter.items()}
    
    def _cosine_similarity(self, vec1, vec2):
        """余弦相似度"""
        common = set(vec1.keys()) & set(vec2.keys())
        if not common:
            return 0.0
        
        dot = sum(vec1[k] * vec2[k] for k in common)
        mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)
    
    def add(self, task, result):
        """添加记忆"""
        entry = {
            "task": task,
            "result": result[:500],  # 截断
            "timestamp": datetime.now().isoformat()
        }
        self.data["entries"].append(entry)
        
        # 更新N-gram语料库
        ngrams = self._get_ngrams(task, 2)
        for ng in ngrams:
            if ng not in self.ngrams["corpus"]:
                self.ngrams["corpus"][ng] = 0
            self.ngrams["corpus"][ng] += 1
        
        self.save()
    
    def search(self, query, top_k=5):
        """搜索相似记忆"""
        if not self.data["entries"]:
            return []
        
        query_vec = self._tf(query)
        
        results = []
        for entry in self.data["entries"]:
            entry_vec = self._tf(entry["task"])
            sim = self._cosine_similarity(query_vec, entry_vec)
            if sim > 0:
                results.append({
                    "task": entry["task"],
                    "result": entry["result"],
                    "score": sim,
                    "timestamp": entry.get("timestamp")
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def clear(self):
        """清空记忆"""
        self.data = {"entries": []}
        self.ngrams = {"corpus": {}}
        self.save()

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: vector_store.py <add|search> <workflow> [内容]")
        sys.exit(1)
    
    op = sys.argv[1]
    workflow = sys.argv[2]
    vs = VectorStore(workflow)
    
    if op == "add":
        task = sys.argv[3] if len(sys.argv) > 3 else input("任务: ")
        result = sys.argv[4] if len(sys.argv) > 4 else input("结果: ")
        vs.add(task, result)
        print("✅ 已添加")
    
    elif op == "search":
        query = sys.argv[3] if len(sys.argv) > 3 else input("搜索: ")
        results = vs.search(query)
        for r in results:
            print(f"[{r['score']:.2f}] {r['task']}")
    
    elif op == "clear":
        vs.clear()
        print("✅ 已清空")
