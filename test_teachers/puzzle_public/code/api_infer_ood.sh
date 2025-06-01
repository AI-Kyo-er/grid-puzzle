input_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/merged_output/aquarium_8x8/test-00000-of-00001_aligned.jsonl
image_folder=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/VGRP/aquarium_8x8/test-00000-of-00001_images
output_file=../data/output/dev/type20_out.jsonl
api_token=sk-zbxbqattgtkohiwrzyqorysmorzjgrjflpsbelxeagxyytit

python3 api_infer_ood.py --input_file $input_file --image_folder $image_folder --output_file $output_file --api_token $api_token