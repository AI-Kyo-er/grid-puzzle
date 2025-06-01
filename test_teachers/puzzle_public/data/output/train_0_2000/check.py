import argparse
import json
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description='按task_type统计predicted_answer为空的数量')
    parser.add_argument('--input_file', type=str, help='输入JSONL文件路径', default="/inspire/hdd/project/foundationmodel/xialingying133-summer-133/test_teachers/puzzle_public/data/output/train_0_2000/wrong_list.jsonl")
    return parser.parse_args()

def count_empty_predicted_answers(input_file):
    """按task_type统计predicted_answer为空的数量"""
    # 使用defaultdict初始化计数器
    task_counts = defaultdict(int)
    total_empty = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                task_type = data.get('task_type', '未知类别')
                predicted = data.get('predicted_answer', '')
                
                if predicted == "":
                    task_counts[task_type] += 1
                    total_empty += 1
                    
            except json.JSONDecodeError:
                print(f"警告：跳过无效JSON行：{line}")
                continue
    
    return task_counts, total_empty

def main():
    args = parse_args()
    task_counts, total_empty = count_empty_predicted_answers(args.input_file)
    
    print("按task_type统计predicted_answer为空的数量：")
    for task_type, count in task_counts.items():
        print(f"- {task_type}: {count} 条")
    print(f"\n总空值数量：{total_empty} 条")

if __name__ == "__main__":
    main()