import os
import torch
import safetensors.torch

def load_and_convert_pth_to_safetensors(input_dir, output_dir):
    """
    将指定目录下的所有 .pth 文件加载并转换为 .safetensors 格式。
    过滤掉非张量数据。
    
    参数：
    - input_dir: 包含 .pth 文件的目录
    - output_dir: 保存转换后的 .safetensors 文件的目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 遍历输入目录下的所有 .pth 文件
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".pth"):
            # 构造完整的输入文件路径
            input_path = os.path.join(input_dir, file_name)
            # 构造输出文件名和路径
            output_file_name = file_name.replace(".pth", ".safetensors")
            output_path = os.path.join(output_dir, output_file_name)

            data = torch.load(input_path, map_location="cuda")

            # 将权重保存为 .safetensors 格式
            safetensors.torch.save_file(data, output_path)
            print(f"成功转换文件：{input_path} → {output_path}")


    print("所有文件转换完成！")

# 示例路径
input_directory = "/inspire/hdd/project/foundationmodel/xialingying133-summer-133/LLaMA-Factory/saves/qwen2_5vl-7b_pth/lora_sft_original_train_set/checkpoint-96"  # 包含 .pth 文件的目录
output_directory = "/inspire/hdd/project/foundationmodel/xialingying133-summer-133/test_teachers"  # 保存 .safetensors 文件的目录

# 调用函数
load_and_convert_pth_to_safetensors(input_directory, output_directory)