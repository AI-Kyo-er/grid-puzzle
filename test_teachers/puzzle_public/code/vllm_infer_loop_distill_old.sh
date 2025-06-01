#!/bin/bash

# input_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/test_teachers/puzzle_public/data/output/train_0_2000/wrong_origin_file.jsonl
input_file=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/puzzle/data/train/train_shuffled.jsonl
image_folder=/inspire/hdd/project/foundationmodel/xialingying133-summer-133/test_teachers/puzzle_public/data/train/figures
api_token=sk-ugrnymnxkcwtuwhgaqgkkdhigkjeyzcysuufvefjunaufhrg

# 创建日志目录
mkdir -p ./logs

# 设置每个任务处理的数据量
batch_size=2

# 获取总数据量
total_lines=$(wc -l < $input_file)

START=0
END=100

# 计算需要多少个任务
num_batches=$(( (END - START + batch_size - 1) / batch_size ))

# 创建批次输出目录
output_dir="../data/output/train_${START}_${END}"
mkdir -p "$output_dir"

# 提交多个任务
for i in $(seq 0 $((num_batches-1))); do
    start=$((START + i * batch_size))
    end=$((start + batch_size))
    if [ $end -gt $END ]; then
        end=$END
    fi
    
    output_file="${output_dir}/batch_${start}_${end}.jsonl"
    log_file="./logs/batch_${start}_${end}.log"
    
    echo "提交任务 $i: 处理数据 $start 到 $end"
    python3 llm_infer_vllm.py \
        --input_file $input_file \
        --image_folder $image_folder \
        --output_file $output_file \
        --api_token $api_token \
        --start $start \
        --end $end > "$log_file" 2>&1 &
done

# 等待所有后台任务完成
wait
echo "所有任务已完成"