#!/usr/bin/env python3
"""
知识图谱 - 实体关系可视化
"""
import json
import os
from datetime import datetime
from collections import defaultdict

KG_DIR = os.path.expanduser("~/.openclaw/swarm")

class KnowledgeGraph:
    def __init__(self, workflow):
        self.workflow = workflow
        self.path = f"{KG_DIR}/{workflow}/kg/graph.json"
        self.load()
    
    def load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
                self.nodes = data.get("nodes", [])
                self.edges = data.get("edges", [])
        else:
            self.nodes = []
            self.edges = []
    
    def save(self):
        data = {"nodes": self.nodes, "edges": self.edges}
        os.makedirs(f"{KG_DIR}/{workflow}/kg", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_node(self, node_type, name, data=None):
        """添加实体"""
        # 检查是否存在
        for n in self.nodes:
            if n["type"] == node_type and n["name"] == name:
                return n["id"]
        
        node = {
            "id": f"{node_type}_{len(self.nodes)}",
            "type": node_type,
            "name": name,
            "data": data or {},
            "created": datetime.now().isoformat()
        }
        self.nodes.append(node)
        self.save()
        return node["id"]
    
    def add_edge(self, from_id, to_id, relation):
        """添加关系"""
        edge = {
            "from": from_id,
            "to": to_id,
            "relation": relation,
            "created": datetime.now().isoformat()
        }
        self.edges.append(edge)
        self.save()
    
    def query(self, node_type=None, name=None):
        """查询"""
        results = []
        for n in self.nodes:
            if node_type and n["type"] != node_type:
                continue
            if name and name not in n["name"]:
                continue
            results.append(n)
        return results
    
    def get_stats(self):
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "types": list(set(n["type"] for n in self.nodes))
        }
    
    def to_cytoscape(self):
        """转换为 Cytoscape 格式 (用于可视化)"""
        elements = []
        
        for n in self.nodes:
            elements.append({
                "data": {
                    "id": n["id"],
                    "label": n["name"],
                    "type": n["type"]
                }
            })
        
        for e in self.edges:
            elements.append({
                "data": {
                    "source": e["from"],
                    "target": e["to"],
                    "label": e["relation"]
                }
            })
        
        return elements

# CLI
if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else "artgroup"
    kg = KnowledgeGraph(workflow)
    print(json.dumps(kg.get_stats(), indent=2))
