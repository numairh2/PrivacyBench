import json, os, torch
from transformers import (GPT2TokenizerFast, GPT2LMHeadModel,
                          Trainer, TrainingArguments)
from opacus import PrivacyEngine

def load_data(path):
    with open(path) as f:
        texts = json.load(f)
    return texts

def preprocess(tokenizer, texts):
    return tokenizer(texts, return_tensors="pt", 
                     truncation=True, padding=True)

def train(defense, data_path, output_dir):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    model     = GPT2LMHeadModel.from_pretrained("gpt2")

    texts = load_data(data_path)
    if defense == "scrub":
        # Simple regex to remove capitalized words (very rough)
        texts = [" ".join(w for w in s.split() if not w.istitle()) for s in texts]
    encodings = preprocess(tokenizer, texts)

    args = TrainingArguments(
        output_dir=os.path.join("outputs", defense),
        num_train_epochs=3,
        per_device_train_batch_size=8,
        logging_steps=10,
        save_strategy="epoch",
    )
    trainer = Trainer(model=model, args=args, 
                      train_dataset=encodings["input_ids"])

    if defense == "dp":
        privacy_engine = PrivacyEngine(
            model, 
            sample_rate=8/len(texts),
            alphas=[10, 100],
            noise_multiplier=1.0,
            max_grad_norm=1.0,
        )
        privacy_engine.attach(trainer)

    trainer.train()
    trainer.save_model()
    tokenizer.save_pretrained(os.path.join("outputs", defense))
    print(f"✓ Trained ({defense}) → outputs/{defense}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--defense",   choices=["none","scrub","dp"], required=True)
    p.add_argument("--data",      required=True)
    args = p.parse_args()
    train(args.defense, args.data, "outputs")
