"""
Script để download các file tokenizer còn thiếu cho Vietnamese_Embedding.
Model này được fine-tune từ BAAI/bge-m3, dùng chung tokenizer.
Chạy 1 lần: python Backend/RAG/models/download_tokenizer.py
"""
from pathlib import Path
from huggingface_hub import hf_hub_download

TARGET = Path(__file__).parent / "Vietnamese_Embedding"
TOKENIZER_FILES = [
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "sentencepiece.bpe.model",
]

print("Downloading tokenizer files from BAAI/bge-m3 ...")
for fname in TOKENIZER_FILES:
    dest = TARGET / fname
    if dest.exists():
        print(f"  [skip] {fname} already exists")
        continue
    print(f"  Downloading {fname} ...")
    hf_hub_download(
        repo_id="BAAI/bge-m3",
        filename=fname,
        local_dir=str(TARGET),
        local_dir_use_symlinks=False,
    )
    print(f"  [ok] {fname}")

print("Done. Tokenizer files are ready.")
