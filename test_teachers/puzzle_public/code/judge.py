import os
import json
import jsonlines
import numpy as np
import re
import random
data=[]
#with open("../output/dev.jsonl", 'r', encoding='utf-8') as f:
with open("/inspire/hdd/project/foundationmodel/xialingying133-summer-133/CoTdata/CoTData_7B.jsonl", 'r', encoding='utf-8') as f:
    for line in jsonlines.Reader(f):
        data.append(line)

def extract_answer_letter(pred_str):
    pred_str = pred_str.replace("\u043a\u0438", "")
    pred = ""
    if "boxed" in pred_str:
        ans = pred_str.split("boxed")[-1]
        
        if len(ans) == 0:
            return ""
        elif ans[0] == "{":
            stack = 1
            a = ""
            for c in ans[1:]:
                if c == "{":
                    stack += 1
                    a += c
                elif c == "}":
                    stack -= 1
                    if stack == 0:
                        break
                    a += c
                else:
                    a += c
        else:
            a = ans.split("$")[0].strip()
        pred = a
    else:
        print("No boxed!!!!!!!!!!")
    # multiple line
    # pred = pred.split("\n")[0]
    pred = re.sub(r"\n\s*", "", pred)
    if pred != "" and pred[0] == ":":
        pred = pred[1:]
    if pred != "" and pred[-1] == ".":
        pred = pred[:-1]
    if pred != "" and pred[-1] == "/":
        pred = pred[:-1]
    return pred

results=[]
from collections import defaultdict
type_results=defaultdict(list)

for line in data:
    line['answer']=extract_answer_letter(line['response'])
    res=line['ground_truth'].lower()== line['answer'].lower()
    if res is False:
        print(line['answer'], line['ground_truth'])
    results.append(res)
    task=line['question_id'].split('_')[0]
    type_results[task].append(res)
print(type_results)
print(sum(results)/len(results))
for task in type_results:
    results=type_results[task]
    print(f"{task}: {sum(results)/len(results)}")
