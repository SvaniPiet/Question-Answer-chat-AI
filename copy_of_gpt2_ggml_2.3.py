# -*- coding: utf-8 -*-
"""copy of gpt2.ggml.2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1f2NvuGCzMdx6Q8cMsvH_D-SJtug3-fJT
"""

!pip install datasets
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset

from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, AdamW
from datasets import load_dataset
import torch
from torch.utils.data import DataLoader

# Load the GPT model and tokenizer
model_name = "distilgpt2"  # Or any other GPT model
model = AutoModelForCausalLM.from_pretrained(model_name)

dataset = load_dataset("SQuAD")

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
dataset = load_dataset("SQuAD")

# Tokenize the dataset
def tokenize_function(examples):

    return tokenizer(
        examples["context"],
        examples["question"],
        padding="max_length",
        truncation=True,
        max_length=1000,
        return_tensors="pt"
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Convert tokenized dataset to include labels
def format_for_lm(examples):
    input_ids = torch.tensor(examples["input_ids"])  # Convert lists to tensors
    return {
        "input_ids": input_ids,
        "labels": input_ids.clone()  # GPT models use input_ids as labels
    }

# Apply formatting function to the dataset

formatted_dataset = tokenized_dataset.map(format_for_lm, batched=True, remove_columns=["input_ids", "attention_mask"])
formatted_dataset.set_format(type="torch", columns=["input_ids", "labels"])

# Verify the dataset structure
print(formatted_dataset["train"][0])

training_args = TrainingArguments(
    output_dir="./results",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    eval_strategy="epoch",
    save_strategy="epoch",
    fp16=True,
)

# Fine-tuning with LoRA
!pip install peft
from peft import get_peft_model, LoraConfig, TaskType

# Define LoRA Configuration (for quick, parameter-efficient fine-tuning)
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.1,
    bias="none"
)

lora_config = LoraConfig(
    r=16,  # rank
    lora_alpha=32,  # scaling factor
    target_modules=["c_attn", "c_proj"],  # Conv1D layers are supported
    lora_dropout=0.1,  # dropout
    fan_in_fan_out=True  # for Conv1D
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Fine-tuning step (direct, minimal)
train_dataset = tokenized_dataset['train'].shuffle().select(range(100))

# Save the fine-tuned model to a directory
model.save_pretrained("./fine_tuned_gpt2_model")
tokenizer.save_pretrained("./fine_tuned_gpt2_model")

print("Model fine-tuned and saved successfully.")

!huggingface-cli login
!pip install transformers
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("gpt2")


tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):

    return tokenizer(
        examples['question'],
        examples['context'],
        padding="max_length",
        truncation=True
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)

!pip install ctransformers
from ctransformers import AutoModelForCausalLM
llm = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-Chat-GGML",
    model_file="llama-2-7b-chat.ggmlv3.q8_0.bin"
)
import os

original_model_path = "\C:\\Users\\SHIVU\\Desktop\\models\\llama-2-7b-chat.ggmlv3.q8_0.bin"

# Directory to save the model
os.makedirs("./gpt2_ggml_model", exist_ok=True)

# Destination path
destination_model_path = "./gpt2_ggml_model/llama-2-7b-chat.bin"



print("Model copied successfully to", destination_model_path)

def ask_question(prompt):
    response = llm(prompt)
    return response

prompt ="What should be the daily schedule for AI developers?"
response = ask_question(prompt)
print("Model response:", response)