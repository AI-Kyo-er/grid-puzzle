
input_file=../data/dev/dev.jsonl
image_folder=../data/dev/figures
output_file=../data/output/dev_original_train/dev.jsonl
python3 inference.py --model_path /inspire/hdd/project/foundationmodel/xialingying133-summer-133/ckpts/Qwen/Qwen2.5-VL-7B-Instruct --input_file $input_file --image_folder $image_folder --output_file $output_file
