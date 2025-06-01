import base64
import requests
import json
from PIL import Image
import os
# 配置项
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_TOKEN = "sk-zbxbqattgtkohiwrzyqorysmorzjgrjflpsbelxeagxyytit"  # 替换为实际Token
IMAGE_PATH = "test.png"  # 本地测试图片路径
PROMPT = "请描述这张图片的内容"  # 测试提示词

def main():
    # 1. 读取图片并转为Base64（不带data URI前缀）
    with open(IMAGE_PATH, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    print(encoded_string)
    # 2. 构建请求体（根据官方文档格式）
    payload = {
        "model": "Qwen/Qwen2.5-VL-72B-Instruct",  # 替换为文档中支持的模型
        "messages": [
            {"role": "system", "content": "You are a puzzle solver."},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url":f"data:image/png;base64,{encoded_string}"}},  # 类型为image，直接传Base64
                    {"type": "text", "text": PROMPT}
                ]
            }
        ],
        "response_format": {"type": "text"},  # 强制文本响应
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "n": 1
    }
    
    # 3. 设置请求头
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 4. 发送请求
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()  # 检查HTTP状态码
    
    except requests.exceptions.HTTPError as e:
        print(f"API请求失败，状态码: {e.response.status_code}")
        print(f"错误信息: {e.response.json().get('message', '无详细信息')}")
        return
    except Exception as e:
        print(f"请求处理失败: {str(e)}")
        return
    
    # 5. 解析响应
    try:
        result = response.json()
        print("API响应结果:")
        print(json.dumps(result, indent=2))
        
        if result["choices"]:
            message = result["choices"][0]["message"]["content"]
            print(f"\n模型回答: {message}")
    
    except json.JSONDecodeError:
        print("无效的JSON响应:", response.text)
    except KeyError as e:
        print(f"响应结构异常，缺少字段: {str(e)}")

if __name__ == "__main__":
    # 验证图片文件存在
    if not os.path.exists(IMAGE_PATH):
        print(f"错误: 图片文件 {IMAGE_PATH} 不存在")
        exit(1)
    
    try:
        # 验证图片格式（可选）
        img = Image.open(IMAGE_PATH)
        img.verify()
    except Exception as e:
        print(f"错误: 无效的图片文件 {IMAGE_PATH}: {str(e)}")
        exit(1)
    
    main()