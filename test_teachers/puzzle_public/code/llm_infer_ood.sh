input_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/merged_output/ood.jsonl
output_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/CoTdata/CoT_dpsk_r1_7B_ood.jsonl
api_token=sk-zbxbqattgtkohiwrzyqorysmorzjgrjflpsbelxeagxyytit

python3 llm_infer_ood.py --input_file $input_file --output_file $output_file --api_token $api_token