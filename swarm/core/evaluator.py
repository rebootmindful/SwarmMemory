#!/usr/bin/env python3
"""
自动评估模块 - 用 LLM 评估结果质量
"""
import json
import requests

def evaluate(task, result, criteria=None):
    """评估结果质量"""
    
    default_criteria = """
    评估标准：
    1. 完整性 - 是否完成了任务要求
    2. 准确性 - 内容是否正确
    3. 流畅性 - 文字是否通顺
    4. 价值 - 是否有独到见解
    """
    
    prompt = f"""你是一个严格的审核专家。请根据以下标准评估结果：

任务: {task}
结果: {result[:1000]}

{criteria or default_criteria}

请返回JSON格式的评估结果:
{{
    "score": 0-100,
    "完整性": "描述",
    "准确性": "描述", 
    "流畅性": "描述",
    "价值": "描述",
    "问题": ["问题1", "问题2"],
    "建议": ["建议1", "建议2"]
}}
"""
    
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": "Bearer sk-c71efbf355a342a08f2537c0003592c0"},
            json={"model": "deepseek-reasoner", "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        
        result_text = resp.json()["choices"][0]["message"]["content"]
        
        # 尝试解析 JSON
        try:
            # 提取 JSON 部分
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {"score": 50, "评估": result_text[:200]}
    
    except Exception as e:
        return {"error": str(e)}

def evaluate_batch(tasks_results):
    """批量评估"""
    return [evaluate(t, r) for t, r in tasks_results]

if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "测试任务"
    result = sys.argv[2] if len(sys.argv) > 2 else "测试结果"
    print(json.dumps(evaluate(task, result), indent=2, ensure_ascii=False))
