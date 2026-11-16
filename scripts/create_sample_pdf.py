import fitz
from pathlib import Path

Path("sample_documents").mkdir(exist_ok=True)
pdf_path = Path("sample_documents/AI_Concepts.pdf")

doc = fitz.open()

pages_data = [
    ("DocuMind AI: Artificial Intelligence & GenAI Concepts", [
        "Course Reference Manual - Edition 2026",
        "Author: AI Research & Engineering Group",
        "Overview: A comprehensive introduction to Artificial Intelligence, Machine Learning,",
        "Large Language Models, and Retrieval-Augmented Generation (RAG) systems."
    ]),
    ("Chapter 1: Foundations of Artificial Intelligence", [
        "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines",
        "programmed to think, learn, and solve problems like human beings.",
        "Core subfields of AI include:",
        "- Machine Learning (Supervised, Unsupervised, and Reinforcement Learning)",
        "- Natural Language Processing (NLP)",
        "- Computer Vision and Pattern Recognition",
        "- Robotics and Autonomous Systems"
    ]),
    ("Chapter 2: Deep Learning & Neural Architectures", [
        "Deep learning utilizes multi-layered artificial neural networks to model high-level abstractions.",
        "Key architectures include:",
        "- Convolutional Neural Networks (CNNs) for spatial and image processing.",
        "- Recurrent Neural Networks (RNNs) and LSTMs for sequential data.",
        "- Transformer Architecture based on self-attention mechanisms, which serves as the backbone",
        "  for modern Large Language Models."
    ]),
    ("Chapter 3: Generative AI & Large Language Models", [
        "Generative AI models create new, original content including text, images, code, and audio.",
        "Large Language Models (LLMs) are trained on vast corpora of internet text using self-supervised",
        "masked language modeling and causal next-token prediction objectives.",
        "Key limitations of raw LLMs:",
        "- Hallucinations: Generating plausible-sounding but factually false claims.",
        "- Static Knowledge: LLMs cannot know information past their training cutoff date.",
        "- Lack of Access to Private Enterprise Data: General LLMs cannot read proprietary PDFs."
    ]),
    ("Chapter 4: Retrieval-Augmented Generation (RAG)", [
        "Retrieval-Augmented Generation (RAG) is an architectural framework that bridges",
        "the gap between external knowledge stores and generative language models.",
        "How RAG Works:",
        "1. Ingestion: Documents are parsed and partitioned into manageable text chunks.",
        "2. Vector Embedding: Chunks are converted into dense vector embeddings using embedding models.",
        "3. Vector Storage: Chunks and embeddings are indexed in a vector database like ChromaDB.",
        "4. Retrieval: When a user asks a question, the vector DB performs semantic cosine similarity search.",
        "5. Grounded Generation: Top-k chunks are passed to the LLM as strict context with prompt guardrails."
    ]),
    ("Chapter 5: Semantic Chunking and Vector Databases", [
        "Effective chunking is critical for high retrieval recall and precision.",
        "A chunk size between 300-800 tokens with 10-20% overlap balances context richness with specificity.",
        "Vector databases store dense mathematical representations (e.g. 384 dimensions from all-MiniLM-L6-v2).",
        "ChromaDB provides fast local persistence using SQLite and HNSW indexing for nearest neighbor queries."
    ]),
    ("Chapter 6: Hallucination Mitigation & Citations", [
        "RAG drastically reduces hallucinations by instructing the LLM to refuse answering if the context",
        "does not contain the required facts (e.g. responding 'I could not find this information in your uploaded documents').",
        "Ground truth citations include source filename and exact page references, ensuring auditability",
        "and enterprise reliability in production deployments."
    ])
]

for title, paragraphs in pages_data:
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 60), title, fontsize=15, fontname="helv", color=(0.1, 0.2, 0.5))
    y = 110
    for p in paragraphs:
        page.insert_text((50, y), p, fontsize=11, fontname="helv", color=(0.2, 0.2, 0.2))
        y += 26

doc.save(str(pdf_path))
doc.close()
print(f"Generated {pdf_path}")
