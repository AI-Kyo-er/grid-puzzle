import argparse
import json
import os
import base64
import requests
from tqdm import tqdm
from PIL import Image

FEW_SHOT = '''### **Step-by-Step Solution for Kakuro Puzzle:**

#### **1. Understand the Grid Structure:**
- **Rows:**  
  - Row 1 (Clue = 31): 5 cells  
  - Row 2 (Clue = 30): 5 cells  
  - Row 3 (Clue = 21): 5 cells  
  - Row 4 (Clue = 30): 5 cells  
  - Row 5 (Clue = 29): 5 cells  

- **Columns:**  
  - Column 1 (Clue = 33): 5 cells  
  - Column 2 (Clue = 22): 5 cells  
  - Column 3 (Clue = 32): 5 cells  
  - Column 4 (Clue = 25): 5 cells  
  - Column 5 (Clue = 29): 5 cells  

#### **2. Check Each Option for Validity:**
- **Kakuro Rules:**  
  - Sum of each row/column must match its clue.  
  - No duplicates in any row or column (digits 1-9).  

##### **Option A:**
- **Row 3:** 7 + 4 + 5 + 3 + 8 = **27 ≠ 21** → **Invalid** (Sum mismatch).  
- **Conclusion:** Discard Option A.  

##### **Option B:**
- **Row 2:** 9 + 2 + 7 + 2 + 4 = **24 ≠ 30** → **Invalid** (Sum mismatch).  
- **Conclusion:** Discard Option B.  

##### **Option C:**
- **Row Sums:**  
  - Row 1: 8 + 1 + 9 + 7 + 6 = **31 ✔**  
  - Row 2: 9 + 8 + 7 + 2 + 4 = **30 ✔**  
  - Row 3: 7 + 4 + 5 + 3 + 2 = **21 ✔**  
  - Row 4: 3 + 6 + 8 + 4 + 9 = **30 ✔**  
  - Row 5: 6 + 3 + 3 + 9 + 8 = **29 ✔**  

- **Column Sums:**  
  - Column 1: 8 + 9 + 7 + 3 + 6 = **33 ✔**  
  - Column 2: 1 + 8 + 4 + 6 + 3 = **22 ✔**  
  - Column 3: 9 + 7 + 5 + 8 + 3 = **32 ✔**  
  - Column 4: 7 + 2 + 3 + 4 + 9 = **25 ✔**  
  - Column 5: 6 + 4 + 2 + 9 + 8 = **29 ✔**  

- **Uniqueness Issue:**  
  - Row 5 has two "3"s → **Violates standard Kakuro rules**, but no other option fits.  
  - **Possible Justification:** If duplicates are allowed (unlikely), or if the puzzle has an error.  

##### **Option D:**
- **Row 3:** 7 + 4 + 4 + 3 + 2 = **20 ≠ 21** → **Invalid** (Sum mismatch).  
- **Conclusion:** Discard Option D.  

#### **3. Final Decision:**
- **Only Option C satisfies all sum constraints**, despite the minor uniqueness issue.  
- **Likely Explanation:** The puzzle might allow duplicates, or the options contain an error.  

### **Final Answer:**  
\\boxed{C}'''

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
    for attempt in range(retry_times):
        try:
            with open(image_path, "rb") as image_file:
                encoded_bytes = base64.b64encode(image_file.read())
                encoded_string = encoded_bytes.decode('utf-8')
            
            image_type = Image.open(image_path).format.lower()
            
            payload = {
                "model": "Qwen/Qwen2.5-VL-72B-Instruct",
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
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions",
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
    image_file = item.get("image_file")
    if not image_file:
        return {
            "question_id": puzzle_id,
            "error": "缺少image_file字段",
            "success": False
        }
    
    image_path = os.path.join(args.image_folder, image_file)
    if not os.path.exists(image_path):
        return {
            "question_id": puzzle_id,
            "error": f"图片文件不存在: {image_path}",
            "success": False
        }
    
    try:
        prompt = item["prompt"][1]['content'][1]['text']
        # prompt += f'nThe above information is the task description, and the answer is {item["answer"]}, try to think about a reasonable solution about this task and why is this answer. You must only output the step by step thinkging process, and then provide your answer as a single letter (A, B, C, or D) in \\boxed{{}} corresponding to the correct option.'
        prompt += "You can refer this example, " + FEW_SHOT
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
        return {
            "question_id": puzzle_id,
            "error": str(e),
            "success": False,
            "image_file": image_file
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