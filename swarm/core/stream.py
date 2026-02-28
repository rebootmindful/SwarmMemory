#!/usr/bin/env python3
"""
流式输出模块 - 实时显示生成过程
"""
import json
import requests
import sys

def stream_response(api_key, model, messages, on_chunk=None):
    """流式调用 API"""
    
    if "deepseek" in api_key:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "stream": True
        }
    else:
        # aigocode
        url = "https://api.aigocode.com/v1/responses"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "input": messages,
            "stream": True
        }
    
    try:
        response = requests.post(url, json=data, headers=headers, stream=True, timeout=60)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    content = line[6:]
                    if content == '[DONE]':
                        break
                    try:
                        chunk = json.loads(content)
                        if "deepseek" in api_key:
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            text = delta.get("content", "")
                        else:
                            # aigocode 格式
                            delta = chunk.get("output", [{}])[0]
                            text = delta.get("content", [{}])[-1].get("text", "")
                        
                        if text and on_chunk:
                            on_chunk(text)
                        elif text:
                            sys.stdout.write(text)
                            sys.stdout.flush()
                    except:
                        pass
        print()  # 换行
        return True
    except Exception as e:
        print(f"流式输出错误: {e}")
        return False

if __name__ == "__main__":
    # 测试
    stream_response(
        "sk-c71efbf355a342a08f2537c0003592c0",
        "deepseek-reasoner",
        [{"role": "user", "content": "用一句话介绍AI"}]
    )
