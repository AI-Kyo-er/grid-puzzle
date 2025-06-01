import os, json, torch
from datasets import load_dataset
from transformers import (AutoTokenizer, Qwen2VLForCausalLM,
                          BitsAndBytesConfig, TrainingArguments, Trainer)
from peft import LoraConfig, get_peft_model
from PIL import Image

MODEL_NAME = "/inspire/hdd/project/foundationmodel/xialingying133-summer-133/ckpts/Qwen/Qwen2.5-VL-7B-Instruct"         # 或你的本地路径
IMAGE_ROOT = "./images"
CKPT_OUT   = "./lora_qwen_vl"             # 输出目录

# 1) 加载 tokenizer (fast 模式)
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME, trust_remote_code=True, use_fast=True
)
tokenizer.pad_token = tokenizer.eos_token  # Qwen 系列常见做法

# 2) 加载模型 (8-bit & BF16)
bnb_cfg = BitsAndBytesConfig(load_in_8bit=True)
model = Qwen2VLForCausalLM.from_pretrained(
    MODEL_NAME, quantization_config=bnb_cfg, torch_dtype=torch.bfloat16,
    device_map="auto"
)

# 3) 注入 LoRA
lora_cfg = LoraConfig(
    r=8, lora_alpha=32, lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj","k_proj","v_proj","o_proj",
                    "gate_proj","up_proj","down_proj"]
)
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()   # sanity-check

# ---------------------- 数据集 ---------------------- #
def preprocess(example):
    # 加载图片 → 嵌入 <img>
    image_path = os.path.join(IMAGE_ROOT, example["image_file"])
    image = Image.open(image_path).convert("RGB")
    # chat_template 会在 run-time 处理图片，这里仅拼 prompt
    messages = example["prompt"]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False)
    # 加 end-of-assistant token
    prompt += tokenizer.eos_token
    example["input_ids"] = tokenizer(prompt).input_ids
    example["pixel_values"] = image  # lazy, collator 再处理
    return example

ds = load_dataset("json", data_files={
        "train":"data/train.jsonl",
        "validation":"data/val.jsonl"
    })
ds = ds.map(preprocess, remove_columns=ds["train"].column_names,
            num_proc=4, desc="tokenizing")

# ------------------ 自定义 collator ------------------ #
from transformers import AutoImageProcessor
proc = AutoImageProcessor.from_pretrained(MODEL_NAME, use_fast=True)

def collate(batch):
    images = [proc(x["pixel_values"])["pixel_values"][0] for x in batch]
    input_ids = [torch.tensor(x["input_ids"]) for x in batch]
    input_ids = torch.nn.utils.rnn.pad_sequence(
        input_ids, batch_first=True, padding_value=tokenizer.pad_token_id)
    labels = input_ids.clone()  # 全部参与 LM 损失
    pixel_values = torch.stack(images)             # (B,3,H,W)
    return {"input_ids":input_ids,
            "labels":labels,
            "pixel_values":pixel_values}

# ------------------- 训练参数 ------------------- #
args = TrainingArguments(
    output_dir=CKPT_OUT,
    fp16=False, bf16=True,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=2,
    learning_rate=2e-5,
    logging_steps=50,
    save_strategy="steps", save_steps=1000,
    eval_strategy="steps", eval_steps=1000,
    report_to="none"
)

trainer = Trainer(model=model, args=args,
                  train_dataset=ds["train"],
                  eval_dataset=ds["validation"],
                  data_collator=collate)

trainer.train()

# -------------- 保存为 safetensors -------------- #
model.save_pretrained(CKPT_OUT, safe_serialization=True)
tokenizer.save_pretrained(CKPT_OUT)
print("LoRA adapter 已保存 ->", CKPT_OUT)