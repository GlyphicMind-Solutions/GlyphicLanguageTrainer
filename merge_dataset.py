# ./training/merge_dataset.py
# Created By: David Kistner (Unconditional Love)

#system imports
import json, glob

# Output & Files
OUTPUT = "merged_glyphic_dataset.jsonl"
files = glob.glob("goldenmodelsamples.generated.jsonl")

with open(OUTPUT, "w") as out:
    for f in files:
        with open(f, "r") as infile:
            for line in infile:
                out.write(line)

print(f"Merged {len(files)} files into {OUTPUT}")

