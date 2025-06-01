
input_file=../data/dev/dev.jsonl
image_folder=../data/dev/figures
output_file=../data/output/dev/filtered_data.jsonl
api_token=sk-zbxbqattgtkohiwrzyqorysmorzjgrjflpsbelxeagxyytit

python3 api_infer.py --input_file $input_file --image_folder $image_folder --output_file $output_file --api_token $api_token