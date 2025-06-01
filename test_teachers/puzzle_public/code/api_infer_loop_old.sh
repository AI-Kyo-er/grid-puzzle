#!/bin/bash

input_file=../data/dev/dev.jsonl
image_folder=../data/dev/figures
api_token=sk-zbxbqattgtkohiwrzyqorysmorzjgrjflpsbelxeagxyytit

# 创建日志目录
mkdir -p ./logs

# 设置每个任务处理的数据量
batch_size=5

# 获取总数据量
total_lines=$(wc -l < $input_file)

START=0
END=25

# 计算需要多少个任务
num_batches=$(( (END - START + batch_size - 1) / batch_size ))

# 提交多个任务
for i in $(seq 0 $((num_batches-1))); do
    start=$((START + i * batch_size))
    end=$((start + batch_size))
    if [ $end -gt $END ]; then
        end=$END
    fi
    
    output_file="./logs/batch_${start}_${end}.jsonl"
    
    echo "提交任务 $i: 处理数据 $start 到 $end"
    python3 api_infer.py \
        --input_file $input_file \
        --image_folder $image_folder \
        --output_file $output_file \
        --api_token $api_token \
        --start $start \
        --end $end &
done

# 等待所有后台任务完成
wait
echo "所有任务已完成"