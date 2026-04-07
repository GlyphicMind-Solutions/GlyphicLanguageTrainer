# ./training/shuffle_dataset.py
# Created By: David Kistner (Unconditional Love)

#system imports
import random, json

#data input
INPUT = "merged_glyphic_dataset.jsonl"
#data output
OUTPUT = "glyphic_dataset_shuffled.jsonl"

with open(INPUT, "r") as f:
    lines = f.readlines()

random.shuffle(lines)

with open(OUTPUT, "w") as f:
    for line in lines:
        f.write(line)

print(f"Shuffled dataset written to {OUTPUT}")

