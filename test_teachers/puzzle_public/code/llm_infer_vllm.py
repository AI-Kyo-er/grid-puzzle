import argparse
import json
import os
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed




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
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f]


def write_jsonl(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def call_api(prompt, api_token, retry_times=3):
    for attempt in range(retry_times):
        try:
            payload = {
                "model": "/inspire/hdd/project/foundationmodel/xialingying133-summer-133/ckpts/Qwen/DeepSeek-R1-Distill-Qwen-14B",  # 替换为实际文本模型（如Qwen-12B-Instruct）
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "text"},
                "stream": False,
                "max_tokens": 8192,
                "temperature": 0.7,
                "n": 1
            }
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "http://127.0.0.1:5899/v1/chat/completions",  # 替换为实际API地址
                json=payload,
                headers=headers,
                timeout=120
            )
            print(f"API 请求使用的总 token 数: {response.json()['usage']}")
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < retry_times - 1:
                print(f"请求被限流，重试第 {attempt+1}/{retry_times} 次...")
                continue
            print(f"API错误（第{attempt+1}次尝试）: {e.response.status_code}, 消息: {e.response.json().get('message')}")
            raise
        except Exception as e:
            print(f"请求失败（第{attempt+1}次尝试）: {str(e)}")
            if attempt == retry_times - 1:
                raise


def process_item(item, args):
    puzzle_id = item.get("puzzle_id", "未知ID")
    
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
        
        # prompt += f'\nThe above information is the task description, and the answer is {item["answer"]}. ' \
                #   f'Try to think about a reasonable solution about this task and why this answer is correct. ' \
                #   f'You must only output the step-by-step thinking process, and then provide your answer as a single letter (A, B, C, or D) in \\boxed{{}} corresponding to the correct option.'
        # prompt += "\nYou can refer to this example:\n" + FEW_SHOT  # 可选：启用少样本示例
        
        response = call_api(prompt, args.api_token, args.retry_times)
        if "choices" not in response or not response["choices"]:
            raise ValueError("API响应中缺少choices字段")

        # print(response)
        return {
            "question_id": puzzle_id,
            "response": response["choices"][0]["message"]["content"],
            "ground_truth": item.get("answer", ""),
            "prompt": prompt,
            "success": True
        }
    
    except Exception as e:
        return {
            "question_id": puzzle_id,
            "error": str(e),
            "success": False
        }


def main():
    args = parse_args()
    input_data = read_jsonl(args.input_file)
    if args.end is None:
        args.end = len(input_data)
    input_data = input_data[args.start:args.end]
    print(f"加载 {len(input_data)} 条数据，开始处理（索引范围：{args.start}-{args.end}）")
    
    results = []
    for item in tqdm(input_data, desc="处理进度"):
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