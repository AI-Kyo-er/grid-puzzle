#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遍历 VGRP/test-*.json
  - 读取 file_name / prompt / sample_answer
  - 仅保留 prompt 中前两句
  - 从 sample_answer 提取正确网格, e→0, s→1
  - 生成 3 个扰动网格作干扰项
  - 将 4 个选项随机排列，记录正确字母
  - 输出仅含 file_name / prompt (messages) / answer
"""

import os, re, json, random, argparse
from glob import glob
from tqdm import tqdm

GRID_RE = re.compile(r'"answer"\s*:\s*(\[\s*\[.*?]]\s*)', re.S)

def extract_true_grid(sample_answer: str):
    m = GRID_RE.search(sample_answer)
    if not m:
        raise ValueError("answer grid not found")
    grid = json.loads(m.group(1).replace("'", '"'))
    return [[1 if c == 's' else 0 for c in row] for row in grid]

def perturb(g, flips=2):
    h,w=len(g),len(g[0]); out=[row[:] for row in g]
    tried=set()
    while flips:
        r,c=random.randint(0,h-1),random.randint(0,w-1)
        if (r,c) in tried: continue
        out[r][c]^=1
        tried.add((r,c)); flips-=1
    return out

def grid_txt(g): return "\n".join(" ".join(map(str,row)) for row in g)

def shorten_prompt(full_prompt: str) -> str:
    """
    从原 prompt 中截取 “Indexing starts at 0” 之前的部分。
    若找不到该关键词，则返回全文去首尾空格。
    """
    key = "Indexing starts at 0"
    idx = full_prompt.find(key)
    if idx != -1:
        return full_prompt[:idx].rstrip()
    return full_prompt.strip()

def build_text(base_prompt,opt_dict):
    parts=[base_prompt,"\nChoose the correct grid from the options below.\n"]
    for k in ("A","B","C","D"):
        parts.append(f"Option {k}:\n```\n{grid_txt(opt_dict[k])}\n```\n")
    parts.append("Please provide your answer (A, B, C, or D) in \\boxed{}.")
    return "".join(parts)

def align_entry(entry):
    true_grid = extract_true_grid(entry["sample_answer"])
    fake1,fake2,fake3 = perturb(true_grid,2), perturb(true_grid,4), perturb(true_grid,6)
    grids=[("true",true_grid),("fake1",fake1),("fake2",fake2),("fake3",fake3)]
    random.shuffle(grids)
    letter_map=dict(zip("ABCD",[g for _,g in grids]))
    correct_letter="ABCD"[ [kind for kind,_ in grids].index("true") ]

    base_prompt=shorten_prompt(entry["prompt"])
    text_msg=build_text(base_prompt,letter_map)

    msg_user={
        "role":"user",
        "content":[
            {"type":"image","image":os.path.basename(entry["file_name"])},
            {"type":"text","text":text_msg}
        ]
    }
    return {
        "file_name":entry["file_name"],
        "prompt":[
            {"role":"system","content":"You are a puzzle solver."},
            msg_user
        ],
        "answer":correct_letter
    }

def process(src,dst):
    raw=[json.loads(l) for l in open(src,encoding="utf-8")]
    aligned=[align_entry(r) for r in tqdm(raw,desc=os.path.basename(src))]
    os.makedirs(os.path.dirname(dst),exist_ok=True)
    with open(dst,"w",encoding="utf-8") as f:
        for a in aligned: f.write(json.dumps(a,ensure_ascii=False)+"\n")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--vgrp_root",required=True)
    ap.add_argument("--out_root", required=True)
    args=ap.parse_args()
    files=glob(os.path.join(args.vgrp_root,"**","test-*.json"),recursive=True)
    print("found",len(files),"json files")
    for src in files:
        rel=os.path.relpath(src,args.vgrp_root)
        dst=os.path.join(args.out_root,rel.replace(".json","_aligned.jsonl"))
        print("▶",rel); process(src,dst)

if __name__=="__main__":
    main()