import argparse
import json
import os
import base64
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, required=True, help='输入JSONL文件路径（每行一个JSON对象）')
    parser.add_argument('--image_folder', type=str, required=True, help='图片文件夹路径')
    parser.add_argument('--output_file', type=str, required=True, help='输出JSONL文件路径')
    parser.add_argument('--api_token', type=str, required=True, help='API令牌')
    parser.add_argument('--retry_times', type=int, default=3, help='单个请求失败后的重试次数')
    parser.add_argument('--start', type=int, default=0, help='起始索引')
    parser.add_argument('--end', type=int, default=None, help='结束索引（不包含）')
    return parser.parse_args()

def read_jsonl(file_path):
    """读取JSONL文件（每行一个JSON对象）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f]

def write_jsonl(data, file_path):
    """写入JSONL文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def call_api_with_base64(image_path, prompt, api_token, retry_times=3):
    """调用API（带重试机制）"""
    print(api_token)
    for attempt in range(retry_times):
        try:
            with open(image_path, "rb") as image_file:
                encoded_bytes = base64.b64encode(image_file.read())
                encoded_string = encoded_bytes.decode('utf-8')
            
            image_type = Image.open(image_path).format.lower()
            
            payload = {
                "model": "/inspire/hdd/project/foundationmodel/xialingying133-summer-133/ckpts/Qwen/Qwen2.5-VL-72B-Instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url":f"data:image/png;base64,{encoded_string}"}},
                            {"type": "text", "text": prompt}
                        ]
                    }
                ],
                "response_format": {"type": "text"},
                "stream": False,
                "max_tokens": 2048,
                "temperature": 0.7,
                "n": 1
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "http://127.0.0.1:5899/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < retry_times - 1:  # 处理限流
                print(f"请求被限流，重试第 {attempt+1}/{retry_times} 次...")
                continue
            print(f"API错误（第{attempt+1}次尝试）: {e.response.status_code}, 消息: {e.response.json().get('message')}")
            raise
        except Exception as e:
            print(f"请求失败（第{attempt+1}次尝试）: {str(e)}")
            if attempt == retry_times - 1:
                raise

def process_item(item, args):
    """处理单个数据项（包含错误隔离和重试）"""
    puzzle_id = item.get("puzzle_id", "未知ID")
    image_file = item.get("file_name")
    if not image_file:
        return {
            "question_id": puzzle_id,
            "error": "缺少image_file字段",
            "success": False
        }
    
    image_path = image_file
    if not os.path.exists(image_path):
        return {
            "question_id": puzzle_id,
            "error": f"图片文件不存在: {image_path}",
            "success": False
        }
    
    try:
        problem_description = item["prompt"][1]['content'][1]['text']
        prompt = problem_description
        prompt += '''Let's think step by step:\n
                                1. First, analyze the puzzle type and understand the rules.\n
                                2. Examine the given constraints and initial conditions.\n
                                3. Apply logical reasoning to solve the puzzle.\n
                                4. Verify your solution against all rules.\n
                                5. Finally, provide your answer.\n
                                '''
        print("准备好数据")
        response = call_api_with_base64(image_path, prompt, args.api_token, args.retry_times)
        if "choices" not in response or not response["choices"]:
            raise ValueError("API响应中缺少choices字段")
        
        return {
            "question_id": puzzle_id,
            "response": response["choices"][0]["message"]["content"],
            "ground_truth": item.get("answer", ""),
            "prompt": prompt,
            "image_file": image_file,
            "success": True
        }
    
    except Exception as e:
        print(e)
        return {
            "question_id": puzzle_id,
            "error": str(e),
            "success": False,
            "image_file": image_file
        }

def main():
    print(1)
    args = parse_args()
    input_data = read_jsonl(args.input_file)
    if args.end is None:
        args.end = len(input_data)
    input_data = input_data[args.start:args.end]
    print(2)
    print(f"加载 {len(input_data)} 条数据，开始处理（索引范围：{args.start}-{args.end}）")
    results = []
    for item in tqdm(input_data, desc="处理进度"):
        print(3)
        result = process_item(item, args)
        results.append(result)
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    print(f"处理完成：成功 {success_count} 条，失败 {fail_count} 条")
    
    # 写入结果
    write_jsonl(results, args.output_file)
    print(f"结果已保存至：{args.output_file}")


if __name__ == "__main__":
    main()