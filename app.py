import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from train import train
from attacks import extraction, reconstruction, inference


st.title("PIILeakDemo Dashboard")

def load_metrics():
    # Load saved perplexities and leak rates (you'll collect these in train/atack scripts)
    return pd.read_json("metrics.json")

df = load_metrics()

def plot_bar(x,y,title):
    fig, ax = plt.subplot()
    ax.bar(x,y)
    ax.set_title(title)
    st.pyplot(fig)

# Sidebar controls
defense = st.sidebar.selectbox("Defense", ["none", "scrub", "dp"])
attack = st.sidebar.selectbox("Attack", ["extraction","reconstruction","inference"])

if st.sidebar.button("Run Training"):
    st.info("Running attack...")
    if attack == "extraction":
        hits = extraction(f"outputs/{defense}")
        st.write("Extracted PII:", hits)
    elif attack == "reconstruction":
        q = st.text_input("Masked Query", "John Doe lives in [MASK], London")
        preds = reconstruction(f"outputs/{defense}", q)
        st.write(preds)
    else:
        q = st.text_input("Prompt", "John Doe lives in ")
        cand = st.text_input("Candidates (comma-sep)", "London,Bristol,Oxford").split(",")
        res = inference(f"outputs/{defense}", q, cand)
        st.write("Inferred:", res)

# Metric visualization
st.header("Utility vs. Privacy")
plot_bar(df["model"], df["perplexity"], "Perplexity")

st.header("PII Leakage Rates")
plot_bar(df["defense"], df["leak_rate"], "Leak Rate (%)")