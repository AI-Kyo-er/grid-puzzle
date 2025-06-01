import argparse
import json
import os
import base64
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image


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

def type_prompts(type, item):
        # 假设当前数据项为 item
    if item["meta"]["task"] == "Kakuro":
        # 提取 Kakuro 相关元数据
        grid_size = item["meta"]["grid_size"]
        row_sums = item["meta"]["clues"]["row_sums"]
        col_sums = item["meta"]["clues"]["col_sums"]
        
        meta_info = f"You need to solve a {grid_size}x{grid_size} Kakuro puzzle.\nRow sums: {row_sums}\nColumn sums: {col_sums}\n"

    elif item["meta"]["task"] == "Sudoku":
        # 提取 Sudoku 相关元数据
        size = item["meta"]["size"]
        
        # 构建 prompt（示例：强调宫格约束）
        meta_info = f"You need to solve a {size}x{size} Sudoku puzzle.\n"


    elif item["meta"]["task"] == "Aquarium":
        # 提取 Aquarium 相关元数据
        size = item["meta"]["size"]
        row_constraints = item["meta"]["row_constraints"]
        col_constraints = item["meta"]["col_constraints"]
        compartments = item["meta"]["compartments"]
        
        # 构建 prompt（示例：展示行列约束和区域划分）
        meta_info = f"You need to solve an Aquarium puzzle (Size: {size}x{size}).\n" \
                     f"Row water counts: {row_constraints}\n" \
                     f"Column water counts: {col_constraints}\n" \
                     f"Tank compartments: {compartments}\n" \

    elif item["meta"]["task"] == "Binairo":
        # 提取 Binairo 相关元数据
        size = item["meta"]["size"]
        
        meta_info = f"You need to solve a Binairo puzzle (Size: {size}x{size}).\n" \

    return meta_info



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, required=True, help='输入JSONL文件路径（每行一个JSON对象）')
    parser.add_argument('--image_folder', type=str, required=True, help='图片文件夹路径')
    parser.add_argument('--output_file', type=str, required=True, help='输出JSONL文件路径')
    parser.add_argument('--api_token', type=str, required=True, help='API令牌')
    parser.add_argument('--concurrency', type=int, default=4, help='并发线程数（建议≤API允许的QPS）')
    parser.add_argument('--retry_times', type=int, default=3, help='单个请求失败后的重试次数')
    parser.add_argument('--batch_size', type=int, default=20, help='每个线程处理的批次大小（降低内存压力）')
    return parser.parse_args()

def read_jsonl(file_path):
    """读取JSONL文件（每行一个JSON对象）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f]

def append_to_jsonl(item, file_path):
    """向JSONL文件追加一条记录"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

def write_jsonl(data, file_path):
    """写入JSONL文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def call_api_with_base64(image_path, prompt, api_token, retry_times=3):
    """调用API（带重试机制）"""
    for attempt in range(retry_times):
        try:
            with open(image_path, "rb") as image_file:
                encoded_bytes = base64.b64encode(image_file.read())
                encoded_string = encoded_bytes.decode('utf-8')
            
            image_type = Image.open(image_path).format.lower()
            
            payload = {
                "model": "Qwen/Qwen2.5-VL-7B-Instruct",
                "messages": [
                    {"role": "system", "content": SYS},
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
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions  ",
                json=payload,
                headers=headers,
                timeout=1000
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

def process_item(item, args, output_file):
    """处理单个数据项（包含错误隔离和重试）并立即写入结果"""
    puzzle_id = item.get("puzzle_id", "未知ID")
    image_file = item.get("image_file")
    if not image_file:
        result = {
            "question_id": puzzle_id,
            "error": "缺少image_file字段",
            "success": False
        }
        append_to_jsonl(result, output_file)
        return result
    
    image_path = os.path.join(args.image_folder, image_file)
    if not os.path.exists(image_path):
        result = {
            "question_id": puzzle_id,
            "error": f"图片文件不存在: {image_path}",
            "success": False
        }
        append_to_jsonl(result, output_file)
        return result

    meta_info = type_prompts(item["meta"]["task"], item)
    prompt = meta_info + item["prompt"][1]['content'][1]['text']
    prompt += f'nPlease check carefully about each option and show your checking process. There must exist a right answer, and you must choose one from them'
    try:
        response = call_api_with_base64(image_path, prompt, args.api_token, args.retry_times)
        if "choices" not in response or not response["choices"]:
            raise ValueError("API响应中缺少choices字段")
        print(f"API 请求使用的总 token 数: {response['usage']}")
        result = {
            "question_id": puzzle_id,
            "response": response["choices"][0]["message"]["content"],
            "ground_truth": item.get("answer", ""),
            "prompt": prompt,
            "image_file": image_file,
            "success": True
        }
    except Exception as e:
        print(e)
        result = {
            "question_id": puzzle_id,
            "error": str(e),
            "prompt": prompt,
            "image_file": image_file,
            "success": False
        }
    
    # 立即写入结果到文件
    append_to_jsonl(result, output_file)
    return result


def main():
    args = parse_args()
    input_data = read_jsonl(args.input_file)
    print(f"加载 {len(input_data)} 条数据，开始并发处理（线程数={args.concurrency}）")
    
    # 确保输出文件是空的
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, 'w', encoding='utf-8') as f:
        pass  # 创建空文件
    
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        # 分批次提交任务，避免内存占用过高
        for i in range(0, len(input_data), args.batch_size):
            batch = input_data[i:i+args.batch_size]
            futures = [executor.submit(process_item, item, args, args.output_file) for item in batch]
            
            # 实时显示进度
            with tqdm(total=len(batch), desc=f"批次 {i//args.batch_size+1}") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    print(f"处理完成：成功 {success_count} 条，失败 {fail_count} 条")
    print(f"结果已保存至：{args.output_file}")

if __name__ == "__main__":
    main()