import json

def read_jsonl_to_dict(file_path):
    data_dict = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line.strip())
                # 对于test.jsonl，使用question_id作为key
                if 'question_id' in item:
                    data_dict[item['question_id']] = item
                # 对于test1.jsonl，使用puzzle_id作为key
                elif 'puzzle_id' in item:
                    data_dict[item['puzzle_id']] = item
            except json.JSONDecodeError as e:
                print(f"Error decoding line: {e}")
    return data_dict

def merge_data(test_data, test1_data):
    merged_items = []
    for question_id, test_item in test_data.items():
        if question_id in test1_data:
            # 合并两个数据项
            merged_item = {
                **test_item,  # 包含test.jsonl的所有字段
                'puzzle_data': test1_data[question_id]  # 添加test1.jsonl的对应数据
            }
            merged_items.append(merged_item)
    return merged_items

def write_jsonl(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    # 读取两个jsonl文件
    print("Reading test.jsonl...")
    test_data = read_jsonl_to_dict('/inspire/hdd/project/foundationmodel/xialingying133-summer-133/test_teachers/puzzle_public/data/output/train_0_2000/wrong_list.jsonl')
    print(f"Found {len(test_data)} items in test.jsonl")
    
    print("Reading test1.jsonl...")
    test1_data = read_jsonl_to_dict('/inspire/hdd/project/foundationmodel/xialingying133-summer-133/CoTdata/train/train.jsonl')
    print(f"Found {len(test1_data)} items in test1.jsonl")
    
    # 合并数据
    print("Merging data...")
    merged_data = merge_data(test_data, test1_data)
    print(f"Created {len(merged_data)} merged items")
    
    # 写入新的jsonl文件
    print("Writing to wrong_origin_file.jsonl...")
    write_jsonl(merged_data, '/inspire/hdd/project/foundationmodel/xialingying133-summer-133/test_teachers/puzzle_public/data/output/train_0_2000/wrong_origin_file.jsonl')
    print("Done!")

if __name__ == "__main__":
    main() 