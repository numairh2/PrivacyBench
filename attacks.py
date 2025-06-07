import re, json, argparse
from transformers import (GPT2TokenizerFast, GPT2LMHeadModel,
                          pipeline)

def extraction(model_dir, num_samples = 100):
    tok = GPT2TokenizerFast.from_pretrained(model_dir)
    m = GPT2LMHeadModel.from_pretrained(model_dir)
    gen = pipeline("text-generation", model = m, tokenizer = tok)

    hits = set()
    for _ in range(num_samples):
        out = gen("PII: ", model = m, tokenizer = tok)
        # crude regex for "Name Lives at ..."
        found = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", out)
        hits.update(found)
    print("Extracted PII:", hits)
    return hits

def recostruction(model_dir, masked_query):
    tok = GPT2TokenizerFast.from_pretrained(model_dir)
    m   = GPT2LMHeadModel.from_pretrained(model_dir)
    fill = pipeline("fill-mask", model=m, tokenizer=tok)

    preds = fill(masked_query.replace("[MASK]", tok.mask_token))
    print("Reconstruction: ", preds)
    return preds

def inference(model_dir, prompt, candidates):
     tok = GPT2TokenizerFast.from_pretrained(model_dir)
     m   = GPT2LMHeadModel.from_pretrained(model_dir)
     gen = pipeline("text-generation", model=m, tokenizer=tok)

     out = gen(prompt, return_fill_text = False, top_k = len(candidates))
     # pick most likely candidate appering in output
     chosen = max(candidates, key = lambda c: out[0]["generated_text"].count(c))
     print("Inferred:", chosen)
     return chosen

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--attack", choices=["extraction","reconstruction","inference"], required = True)
    p.add_argument("--query", type=str)
    p.add_argument("--candidates", nargs= "+")
    args = p.parse_args()

    if args.attack == "extraction":
        extraction(args.model)
    elif args.attack == "reconstruction":
        recostruction(args.model, args.query)
    else:
        inference(args.model, args.query, args.candidates)
   
