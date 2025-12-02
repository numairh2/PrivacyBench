# PrivacyBench

An interactive demonstration of Personally Identifiable Information (PII) leakage attacks on fine-tuned GPT-2 models. This project reproduces and visualizes the threat models and defense strategies described in the paper [“Analyzing Leakage of Personally Identifiable Information in Language Models”](https://gangw.cs.illinois.edu/class/cs562/papers/llm-leak-sp23.pdf).

---

## Table of Contents

1. [Introduction](#introduction)
2. [Paper Overview](#paper-overview)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Setup & Installation](#setup--installation)
7. [Data Generation](#data-generation)
8. [Model Training](#model-training)
9. [Attack Implementations](#attack-implementations)
10. [Metrics & Evaluation](#metrics--evaluation)
11. [Dashboard (Streamlit)](#dashboard-streamlit)
12. [Usage Examples](#usage-examples)
13. [Configuration](#configuration)
14. [Contributing](#contributing)
15. [License](#license)
16. [References](#references)

---

## Introduction

Language models are known to memorize and occasionally regurgitate sensitive data from their training sets. **PIILeakDemo** is a hands-on side project that:

* Fine-tunes GPT-2 on synthetic “private” text containing dummy PII.
* Applies three threat models—Extraction, Reconstruction, and Inference—to quantify leakage.
* Compares three defense strategies: no defense, PII scrubbing, and Differential Privacy training.
* Visualizes the trade‑off between model utility (perplexity) and privacy (leak rate) via a Streamlit dashboard.

This demo illustrates how modern privacy attacks work in practice and how simple defenses can mitigate PII leak risks.

## Paper Overview

This project is based on the Spring 2023 paper *Analyzing Leakage of Personally Identifiable Information in Language Models*, which:

* Defines three levels of PII leakage attacks:

  1. **Extraction** – sampling model outputs and parsing out explicit PII sequences.
  2. **Reconstruction** – using fill‑mask queries to reconstruct missing entities.
  3. **Inference** – narrowing down candidates and letting the model choose the correct one.
* Evaluates defense strategies including data scrubbing and Differential Privacy (DP‑SGD).
* Quantifies the privacy–utility tradeoff by measuring perplexity vs. PII recovery rates.

Read the full paper [here](https://gangw.cs.illinois.edu/class/cs562/papers/llm-leak-sp23.pdf).

## Features

* **Synthetic PII Data** – automatically generate dummy names, addresses, and dates.
* **Fine‑Tuning Options**:

  * **None** (raw data)
  * **Scrubbed** (remove capitalized tokens via regex/NER)
  * **DP** (DP‑SGD via Opacus with configurable ε)
* **Attack Suites**:

  1. **Extraction** via text‑generation + regex/NER.
  2. **Reconstruction** via masked‑language modeling.
  3. **Inference** via candidate selection.
* **Visualization** – Streamlit app with live plots of perplexity and leak rates.

## Tech Stack

* **Model & Training**: [HuggingFace Transformers](https://huggingface.co/transformers/) GPT-2, [Opacus](https://github.com/pytorch/opacus) for DP.
* **Data Generation**: [Faker](https://github.com/joke2k/faker) for synthetic PII.
* **PII Scrubbing**: spaCy or simple regex patterns.
* **Attack Implementations**: HuggingFace `pipeline` APIs.
* **Visualization & UI**: [Streamlit](https://streamlit.io/) + Matplotlib.

## Project Structure

```bash
PIILeakDemo/
├── data/
│   └── generate_synthetic_data.py   # Script to create dummy PII samples
├── train.py                         # Fine-tune GPT-2 under various defenses
├── attacks.py                       # Extraction, Reconstruction, and Inference attacks
├── app.py                           # Streamlit dashboard
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Setup & Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/PIILeakDemo.git
   cd PIILeakDemo
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Download or link to the paper**
   Place the PDF in a `/docs` folder or ensure you have the URL for reference.

## Data Generation

Generate a synthetic dataset with dummy PII:

```bash
python data/generate_synthetic_data.py \
  --num 100 \
  --output data/synth.json
```

* **--num**: Number of samples (default 50).
* **--output**: Path to save the JSON list of sentences.

Each sample looks like:

```
"John Doe lives at 123 Maple St, Springfield. Last checkup was on 2021-07-15."
```

## Model Training

Fine-tune GPT-2 under three defense settings:

```bash
# 1. No defense (raw data)
python train.py --defense none --data data/synth.json

# 2. PII scrubbing (remove capitalized tokens)
python train.py --defense scrub --data data/synth.json

# 3. Differential Privacy (DP‑SGD, ε≈8)
python train.py --defense dp --data data/synth.json
```

Models and tokenizers will be saved under `outputs/{defense}/`.

## Attack Implementations

Run individual attack scripts against a trained model:

```bash
# Extraction attack
python attacks.py --model outputs/none --attack extraction

# Reconstruction attack
python attacks.py --model outputs/scrub \
  --attack reconstruction \
  --query "Jane Smith lives in [MASK], London"

# Inference attack
python attacks.py --model outputs/dp \
  --attack inference \
  --query "Alice Brown lives at " \
  --candidates "Paris" "Berlin" "Madrid"
```

* Extraction prints a set of recovered name tokens.
* Reconstruction returns top fill‑mask predictions.
* Inference selects the most likely candidate city.

## Metrics & Evaluation

After each training and attack run, collect and save metrics (for example in a `metrics.json`):

```json
[
  {
    "model": "none",
    "perplexity": 12.34,
    "leak_rate": 0.42
  },
  {
    "model": "scrub",
    "perplexity": 14.56,
    "leak_rate": 0.21
  },
  {
    "model": "dp",
    "perplexity": 20.78,
    "leak_rate": 0.05
  }
]
```

* **perplexity**: Lower indicates better utility.
* **leak\_rate**: Fraction or percentage of PII tokens recovered.

## Dashboard (Streamlit)

Launch the interactive dashboard to compare defenses and threat models:

```bash
streamlit run app.py
```

Features:

* Select defense type (none, scrub, dp).
* Run training or attack live.
* Visualize Perplexity vs. Leak Rate bar charts.
* Display actual PII examples recovered.

## Usage Examples

```bash
# Generate 200 samples
python data/generate_synthetic_data.py --num 200 --output data/synth.json

# Train DP model
python train.py --defense dp --data data/synth.json

# Run extraction attack with 200 samples
python attacks.py --model outputs/dp --attack extraction --num_samples 200

# View dashboard
streamlit run app.py
```

## Configuration

* *Batch size, epochs, DP ε, noise multiplier,* etc., can be tuned via `TrainingArguments` in `train.py`.
* Attack sample count and regex patterns can be adjusted in `attacks.py`.

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to branch (`git push origin feature/my-feature`).
5. Open a Pull Request.

Please follow the existing code style and include tests or examples for new features.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## References

* Wu, Gang, et al. *Analyzing Leakage of Personally Identifiable Information in Language Models*, CS 562 Spring 2023.
  PDF: [https://gangw.cs.illinois.edu/class/cs562/papers/llm-leak-sp23.pdf](https://gangw.cs.illinois.edu/class/cs562/papers/llm-leak-sp23.pdf)
