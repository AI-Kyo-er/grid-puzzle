import json
from type20 import type_prompts

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f]

def test(file_path, num_items=5700):
    items = read_jsonl(file_path)[:num_items]
    
    for _, item in enumerate(items):
        text = type_prompts(item)
        # print(text)
    

if __name__ == "__main__":
    file_path = "/inspire/hdd/project/foundationmodel/xialingying133-summer-133/merged_output/ood.jsonl"
    test(file_path) 