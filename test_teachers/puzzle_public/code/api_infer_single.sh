
input_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/puzzle/data/train/train_shuffled.jsonl
image_folder=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/puzzle/data/train/figures
output_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/CoTdata/CoTData_7B.jsonl
api_token=sk-zbxbqattgtkohiwrzyqorysmorzjgrjflpsbelxeagxyytit

python3 api_infer_single_old.py --input_file $input_file --image_folder $image_folder --output_file $output_file --api_token $api_token