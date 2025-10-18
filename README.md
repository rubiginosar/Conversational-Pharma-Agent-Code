# conversational-pharma-agent-code
[![DOI](https://zenodo.org/badge/1078884269.svg)](https://doi.org/10.5281/zenodo.17386801)
Conversational pharmaceutical assistant using LLMs, RAG, and LangChain. Built as part of a Master’s thesis (Big Data Analytics, USTHB).

# 💊 Conversational Pharmaceutical Assistant using LLMs and RAG

This project is a conversational assistant developed as part of a Master's thesis in **Big Data Analytics** at **USTHB**. The assistant automates customer service tasks for pharmaceutical use cases using **Large Language Models (LLMs)** and **Retrieval-Augmented Generation (RAG)**.

## 🧠 Overview

The assistant is designed to handle real-world pharmacy-related queries such as:
- Product search
- Order tracking
- Proposing medication alternatives
- Registering and classifying customer claims

It integrates an LLM with a retrieval system that fetches relevant context from structured data (CSV) to provide accurate, real-time answers.

## 🔧 Technologies Used

- **Python**
- **LangChain**
- **OpenAI API / GPT-4**
- **HuggingFace Embeddings**
- **ChromaDB** (Vector Store)
- **Pandas, NumPy**
- **JSON / CSV**
- **FastAPI** (optional, for deployment)
- **Git / GitHub**

## 🧩 Architecture

- 🧠 LLM Agent (LangChain + OpenAI)
- 📁 Contextual Retrieval (RAG using HuggingFace + ChromaDB)
- 📊 Pharmacy Dataset (CSV-based)
- ⚙️ Custom tools and prompts for domain-specific tasks

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/rubiginosar/conversational-pharma-agent.git
cd conversational-pharma-agent

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the assistant (example script or notebook)
