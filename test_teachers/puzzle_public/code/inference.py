import argparse
import json
import os
import base64
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, required=True, help='输入JSONL文件路径')
    parser.add_argument('--image_folder', type=str, required=True, help='图片文件夹路径')
    parser.add_argument('--output_file', type=str, required=True, help='输出JSONL文件路径')
    parser.add_argument('--api_token', type=str, required=True, help='API令牌')
    parser.add_argument('--concurrency', type=int, default=4, help='并发线程数')
    return parser.parse_args()

def read_jsonl(file_path):
    """读取JSONL文件（每行一个JSON对象）"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def write_jsonl(data, file_path):
    """写入JSONL文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def process_item(item, args):
    """处理单个数据项（使用Base64编码图片）"""
    image_path = os.path.join(args.image_folder, item["image_file"])
    
    try:
        # 调用API（包含Base64图片）
        response = call_api_with_base64(image_path, item["prompt"], args.api_token)
        
        # 处理结果
        return {
            "question_id": item["puzzle_id"],
            "response": response["choices"][0]["message"]["content"],
            "ground_truth": item.get("answer", ""),
            "prompt": item["prompt"]  # 保留原始prompt
        }
    
    except Exception as e:
        print(f"处理失败: {item['puzzle_id']}, 错误: {str(e)}")
        return None

def call_api_with_base64(image_path, prompt, api_token):
    """将本地图片转为Base64并调用API"""
    # 读取图片并转为Base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 构建请求体
    payload = {
        "model": "Qwen/Qwen2.5-VL-72B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_string}"  # Base64格式
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "n": 1
    }
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # 发送请求
    response = requests.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        json=payload,
        headers=headers
    )
    
    response.raise_for_status()
    return response.json()

def main():
    args = parse_args()
    
    # 使用read_jsonl读取输入文件
    print(f"读取输入数据: {args.input_file}")
    data = read_jsonl(args.input_file)
    print(f"共加载 {len(data)} 条数据")
    
    # 并发处理
    print(f"开始并发处理（线程数: {args.concurrency}）")
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(process_item, item, args) for item in data]
        results = []
        
        # 使用tqdm显示进度条
        for future in tqdm(futures, desc="处理进度"):
            result = future.result()
            if result:
                results.append(result)
    
    # 写入结果
    print(f"写入结果到: {args.output_file}")
    write_jsonl(results, args.output_file)
    print(f"成功处理 {len(results)}/{len(data)} 条数据")

if __name__ == "__main__":
    main()