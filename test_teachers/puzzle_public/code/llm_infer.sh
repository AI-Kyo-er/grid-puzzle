
input_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/test_teachers/puzzle_public/data/dev/dev.jsonl
output_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/CoTdata/CoT_dpsk_r132B.jsonl
api_token=sk-zbxbqattgtkohiwrzyqorysmorzjgrjflpsbelxeagxyytit

python3 llm_infer.py --input_file $input_file --output_file $output_file --api_token $api_token