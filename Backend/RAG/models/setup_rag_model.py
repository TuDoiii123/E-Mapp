"""
Setup script: download Vietnamese_Embedding model + tokenizer về thư mục local.

Chạy 1 lần trước khi khởi động server:
  python Backend/RAG/models/setup_rag_model.py

Yêu cầu:
  pip install huggingface_hub sentence-transformers
"""
from pathlib import Path
from huggingface_hub import hf_hub_download
import inspect

TARGET = Path(__file__).parent / "Vietnamese_Embedding"
TARGET.mkdir(parents=True, exist_ok=True)

_HF_SIG = inspect.signature(hf_hub_download).parameters

def _dl(repo_id: str, filename: str) -> None:
    dest = TARGET / filename
    if dest.exists():
        print(f"  [skip] {filename}")
        return
    print(f"  Downloading {filename} from {repo_id} ...")
    kwargs = {"repo_id": repo_id, "filename": filename, "local_dir": str(TARGET)}
    if "local_dir_use_symlinks" in _HF_SIG:
        kwargs["local_dir_use_symlinks"] = False
    hf_hub_download(**kwargs)
    print(f"  [ok]   {filename} ({dest.stat().st_size // 1024:,} KB)")


MODEL_REPO     = "AITeamVN/Vietnamese_Embedding"
TOKENIZER_REPO = "BAAI/bge-m3"

# Model weights + config (từ AITeamVN/Vietnamese_Embedding)
MODEL_FILES = [
    "config.json",
    "model.safetensors",
    "modules.json",
    "sentence_bert_config.json",
    "config_sentence_transformers.json",
    "1_Pooling/config.json",
]

# Tokenizer (từ BAAI/bge-m3 — dùng chung tokenizer)
TOKENIZER_FILES = [
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "sentencepiece.bpe.model",
]

if __name__ == "__main__":
    print(f"Target: {TARGET}\n")

    print("=== Model weights (AITeamVN/Vietnamese_Embedding) ===")
    for f in MODEL_FILES:
        try:
            _dl(MODEL_REPO, f)
        except Exception as e:
            print(f"  [warn] {f}: {e}")

    print("\n=== Tokenizer (BAAI/bge-m3) ===")
    for f in TOKENIZER_FILES:
        try:
            _dl(TOKENIZER_REPO, f)
        except Exception as e:
            print(f"  [warn] {f}: {e}")

    # Verify
    required = {"config.json", "model.safetensors", "modules.json",
                "tokenizer.json", "sentencepiece.bpe.model"}
    existing = {p.name for p in TARGET.rglob("*") if p.is_file()}
    missing  = required - existing
    if missing:
        print(f"\n[WARN] Còn thiếu files: {missing}")
        print("Kiểm tra kết nối mạng hoặc HuggingFace token nếu model private.")
    else:
        print("\n[OK] Vietnamese_Embedding model đã sẵn sàng.")
