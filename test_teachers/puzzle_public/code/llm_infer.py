import argparse
import json
import os
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

SYS = '''
You are a high-quality grid-puzzle teacher model. Your chain-of-thought (CoT) will be used to train a student model via supervised fine-tuning (SFT).

Thinking protocol  
1. Briefly restate which puzzle is being solved and its rules.  
2. Although I did not provide you with the picture, I will provide you with the information extracted from the picture in the usrs prompt. You need to use this information to pretend that you extracted it from the picture yourself, and write in the reasoning content that you got the key information for solving the problem from the picture: ...
3. **Option analysis** – Treat the task as a four-choice question (A, B, C, D).  
   • Examine A, then B, then C, then D in order.  
   • For every wrong option give exactly **one decisive fact** that rules it out.  
4. **Answer** – When only one option remains, output it as the final answer in the form `\\boxed{X}` where `X` is A, B, C or D.

Content constraints  
* Do not repeat information already provided in the task.  
* Keep reasoning concise yet complete—include every key logical step, omit all redundancy.  
* Ensure the reasoning is correct and easy for the student model to replicate.'''

def type_prompts(item):
    task = item["meta"]["task"]
    if task == "Kakuro":
        grid_size = item["meta"]["grid_size"]
        row_sums = item["meta"]["clues"]["row_sums"]
        col_sums = item["meta"]["clues"]["col_sums"]
        return f"You need to solve a {grid_size}x{grid_size} Kakuro puzzle.\nRow sums: {row_sums}\nColumn sums: {col_sums}\n"

    elif task == "Sudoku":
        size = item["meta"]["size"]
        return f"You need to solve a {size}x{size} Sudoku puzzle.\n"

    elif task == "Aquarium":
        size = item["meta"]["size"]
        row_constraints = item["meta"]["row_constraints"]
        col_constraints = item["meta"]["col_constraints"]
        compartments = item["meta"]["compartments"]
        return f"You need to solve an Aquarium puzzle (Size: {size}x{size}).\n" \
               f"Row water counts: {row_constraints}\n" \
               f"Column water counts: {col_constraints}\n" \
               f"Tank compartments: {compartments}\n"

    elif task == "Binairo":
        size = item["meta"]["size"]
        return f"You need to solve a Binairo puzzle (Size: {size}x{size}).\n" \

    return ""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, required=True, help='输入JSONL文件路径（每行一个JSON对象）')
    parser.add_argument('--output_file', type=str, required=True, help='输出JSONL文件路径')
    parser.add_argument('--api_token', type=str, required=True, help='API令牌')
    parser.add_argument('--concurrency', type=int, default=4, help='并发线程数（建议≤API允许的QPS）')
    parser.add_argument('--retry_times', type=int, default=3, help='单个请求失败后的重试次数')
    parser.add_argument('--batch_size', type=int, default=20, help='每个线程处理的批次大小（降低内存压力）')
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
                "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",  # 替换为实际文本模型（如Qwen-12B-Instruct）
                "messages": [
                    {"role": "system", "content": SYS},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "text"},
                "stream": False,
                "max_tokens": 2048,
                "temperature": 0.7,
                "n": 1
            }
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions",  # 替换为实际API地址
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
        meta_info = type_prompts(item)
        problem_description = item["prompt"][1]['content'][1]['text']
        prompt = meta_info + problem_description
        prompt += f'nPlease check carefully about each option. There must exist a right answer, and you must choose one from them'
        
        # prompt += f'\nThe above information is the task description, and the answer is {item["answer"]}. ' \
                #   f'Try to think about a reasonable solution about this task and why this answer is correct. ' \
                #   f'You must only output the step-by-step thinking process, and then provide your answer as a single letter (A, B, C, or D) in \\boxed{{}} corresponding to the correct option.'
        # prompt += "\nYou can refer to this example:\n" + FEW_SHOT  # 可选：启用少样本示例
        
        response = call_api(prompt, args.api_token, args.retry_times)
        if "choices" not in response or not response["choices"]:
            raise ValueError("API响应中缺少choices字段")
        
        return {
            "question_id": puzzle_id,
            "response": response["choices"][0]["message"]["reasoning_content"] + response["choices"][0]["message"]["content"],
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
    input_data = read_jsonl(args.input_file)[:10]
    print(f"加载 {len(input_data)} 条数据，开始并发处理（线程数={args.concurrency}）")
    
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        for i in range(0, len(input_data), args.batch_size):
            batch = input_data[i:i+args.batch_size]
            futures = [executor.submit(process_item, item, args) for item in batch]
            
            with tqdm(total=len(batch), desc=f"批次 {i//args.batch_size+1}") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)
    
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    print(f"处理完成：成功 {success_count} 条，失败 {fail_count} 条")
    
    write_jsonl(results, args.output_file)
    print(f"结果已保存至：{args.output_file}")

if __name__ == "__main__":
    main()