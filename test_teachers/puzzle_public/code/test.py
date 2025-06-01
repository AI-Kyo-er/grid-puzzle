import json

file_path = "../data/dev/dev.jsonl"

with open(file_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line.strip())
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON decode error at line {i}: {e}")
            print(f"   {line.strip()}")
            print(f"   {' ' * (e.colno - 1)}^ (column {e.colno})")

