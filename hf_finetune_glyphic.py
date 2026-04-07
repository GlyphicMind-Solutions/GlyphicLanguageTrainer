# ./training/hf_finetune_glyphic.py
# Created By: David Kistner (Unconditional Love)

#system imports
import os, torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model

#GPU Variables
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["ACCELERATE_DISABLE_GPU"] = "1"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"

# Paths
MODEL_PATH = "MODEL PATH GOES HERE" ## MODIFY BEFORE RUNNING
DATASET_PATH = "./glyphic_dataset_shuffled.jsonl"
OUTPUT_DIR = "./glyphic-llm-v1"

# Basic setup
os.makedirs(OUTPUT_DIR, exist_ok=True)

#load tokenizer
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)

#load dataset
print("Loading dataset...")
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

# Train/validation split (e.g., 95% train, 5% val)
print("Splitting dataset into train/validation...")
dataset = dataset.train_test_split(test_size=0.05, shuffle=True, seed=42)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]

# -------------
# Tokenize
# -------------
def tokenize(example):
    # Extract the input envelope
    inp = example["input_envelope"]

    # Extract the output object (glyphic + realized)
    out = example["output"]

    # Build the output text cleanly
    out_text = ""
    if isinstance(out, dict):
        if "glyphic" in out and out["glyphic"] is not None:
            out_text += str(out["glyphic"]) + "\n"
        if "realized" in out and out["realized"] is not None:
            out_text += str(out["realized"])
    else:
        out_text = str(out)

    # Final combined training example
    text = inp + "\n### GLYPHIC.MODEL_OUTPUT\n" + out_text

    # Tokenize for training
    tokens = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=2048
    )

    # Labels = input_ids (standard causal LM training)
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

print("Tokenizing train dataset...")
train_dataset = train_dataset.map(tokenize, batched=False)
print("Tokenizing eval dataset...")
eval_dataset = eval_dataset.map(tokenize, batched=False)

# Remove original columns to keep memory lean
train_dataset = train_dataset.remove_columns(
    [col for col in train_dataset.column_names if col not in ["input_ids", "attention_mask", "labels"]]
)
eval_dataset = eval_dataset.remove_columns(
    [col for col in eval_dataset.column_names if col not in ["input_ids", "attention_mask", "labels"]]
)

print("Loading base model with 4-bit support (QLoRA style)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    dtype=torch.float16,
    low_cpu_mem_usage=True,
    device_map={"": "cpu"}
)


print("Applying LoRA adapters...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=[
        "qkv_proj",
        "o_proj",
        "fc1",
        "fc2"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
# Enable gradient checkpointing to save memory


# Training arguments tuned for CPU + small RAM
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=16,
    eval_strategy="steps",
    eval_steps=200,
    save_steps=200,
    save_total_limit=3,
    learning_rate=2e-5,
    num_train_epochs=3,
    logging_steps=10,
    report_to="none",
    fp16=False,
    bf16=False,
    optim="adamw_torch",
    remove_unused_columns=False,
    load_best_model_at_end=True,
    metric_for_best_model="loss",
    use_cpu=True,
)

# --------------------
# Comput Metrics
# --------------------
def compute_metrics(eval_pred):
    # Simple loss-based metric (Trainer already logs loss)
    # Placeholder for future perplexity or custom metrics
    return {}

print("Starting training...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics
)

trainer.train()

print("Training complete. Saving LoRA adapter...")
trainer.model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Done. LoRA adapter and tokenizer saved to:", OUTPUT_DIR)

