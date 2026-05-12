import numpy as np
import torch
import json
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Tuple, Set, Union, Optional
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from langchain_core.embeddings.embeddings import Embeddings
from FlagEmbedding import BGEM3FlagModel

def setup_gpu_info() -> None:
    print(f"Số lượng GPU khả dụng: {torch.cuda.device_count()}")
    print(f"GPU hiện tại: {torch.cuda.current_device()}")
    print(f"Tên GPU: {torch.cuda.get_device_name(0)}")

def load_model(model_name: str, use_fp16: bool = False) -> BGEM3FlagModel:
    return BGEM3FlagModel(model_name, use_fp16=use_fp16)

def load_json_file(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_jsonl_file(file_path: str) -> List[Dict]:
    corpus = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            data = json.loads(line.strip())
            corpus.append(data)
    return corpus

def extract_corpus_from_legal_documents(legal_data: dict) -> List[Dict]:
    corpus = []
    for document in legal_data:
        for article in document['articles']:
            chunk = {
                "law_id": document['law_id'],
                "article_id": article['article_id'],
                "title": article['title'],
                "text": article['title'] + '\n' + article['text'] 
            }
            corpus.append(chunk)
    return corpus

def convert_corpus_to_documents(corpus: List[Dict[str, str]]) -> List[Document]:
    documents = []
    for i in tqdm(range(len(corpus)), desc="Converting corpus to documents"):
        context = corpus[i]['text']
        metadata = {
            'law_id': corpus[i]['law_id'],
            'article_id': corpus[i]['article_id'],
            'title': corpus[i]['title']
        }
        documents.append(Document(page_content=context, metadata=metadata))
    return documents

class CustomEmbedding(Embeddings):
    """Custom embedding class that uses the BGEM3FlagModel."""
    
    def __init__(self, model: BGEM3FlagModel, batch_size: int = 1): 
        self.model = model
        self.batch_size = batch_size
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for i in tqdm(range(0, len(texts), self.batch_size), desc="Embedding documents"):
            batch_texts = texts[i:i+self.batch_size]  
            batch_embeddings = self._get_batch_embeddings(batch_texts)
            embeddings.extend(batch_embeddings)
            torch.cuda.empty_cache()
        return np.vstack(embeddings) 

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode(text, max_length=256)['dense_vecs']
        return embedding

    def _get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        with torch.no_grad():
            outputs = self.model.encode(texts, batch_size=self.batch_size, max_length=2048)['dense_vecs']
        batch_embeddings = outputs
        del outputs
        return batch_embeddings


class VectorDB:
    """Vector database for document retrieval."""
    
    def __init__(
        self,
        documents: List[Document],
        embedding: Embeddings,
        vector_db=FAISS,
        index_path: Optional[str] = None
    ) -> None:
        self.vector_db = vector_db
        self.embedding = embedding
        self.index_path = index_path
        self.db = self._build_db(documents)

    def _build_db(self, documents: List[Document]):
        if self.index_path:
            db = self.vector_db.load_local(
                self.index_path, 
                self.embedding, 
                allow_dangerous_deserialization=True
            )
        else:
            db = self.vector_db.from_documents(
                documents=documents, 
                embedding=self.embedding, 
                distance_strategy=DistanceStrategy.DOT_PRODUCT
            )
        return db
    
    def get_retriever(self, search_type: str = "similarity", search_kwargs: dict = {"k": 10}):
        retriever = self.db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
        return retriever
    
    def save_local(self, folder_path: str) -> None:
        self.db.save_local(folder_path)


def process_sample(sample: dict, retriever) -> List[int]:
    question = sample['question']
    docs = retriever.invoke(question)
    retrieved_article_full_ids = [
        docs[i].metadata['law_id'] + "#" + docs[i].metadata['article_id'] 
        for i in range(len(docs))
    ]
    indexes = []
    for article in sample['relevant_articles']:
        article_full_id = article['law_id'] + "#" + article['article_id']
        if article_full_id in retrieved_article_full_ids:
            idx = retrieved_article_full_ids.index(article_full_id) + 1
            indexes.append(idx)
        else:
            indexes.append(0)       
    return indexes

def calculate_metrics(all_indexes: List[List[int]], num_samples: int, selected_keys: Set[str]) -> Dict[str, float]:
    count = [len(indexes) for indexes in all_indexes]
    result = {}
    
    for thres in [1, 3, 5, 10, 100]:
        found = [[y for y in x if 0 < y <= thres] for x in all_indexes]
        found_count = [len(x) for x in found]
        acc = sum(1 for i in range(num_samples) if found_count[i] > 0) / num_samples
        rec = sum(found_count[i] / count[i] for i in range(num_samples)) / num_samples
        pre = sum(found_count[i] / thres for i in range(num_samples)) / num_samples
        mrr = sum(1 / min(x) if x else 0 for x in found) / num_samples

        if f"Accuracy@{thres}" in selected_keys:
            result[f"Accuracy@{thres}"] = acc
        if f"MRR@{thres}" in selected_keys:
            result[f"MRR@{thres}"] = mrr
            
    return result


def save_results(result: Dict[str, float], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"Results saved to {output_path}")


def main():
    setup_gpu_info()
    model = load_model('AITeamVN/Vietnamese_Embedding', use_fp16=False)
    samples = load_json_file('zalo_kaggle/train_question_answer.json')['items']
    legal_data = load_json_file('zalo_kaggle/legal_corpus.json')
    
    corpus = extract_corpus_from_legal_documents(legal_data)
    documents = convert_corpus_to_documents(corpus)
    embedding = CustomEmbedding(model, batch_size=1)  # Increased batch size for efficiency time
    vectordb = VectorDB(
        documents=documents,
        embedding=embedding,
        vector_db=FAISS,
        index_path=None
    )
    retriever = vectordb.get_retriever(search_type="similarity", search_kwargs={"k": 100})
    all_indexes = []
    for sample in tqdm(samples, desc="Processing samples"):
        all_indexes.append(process_sample(sample, retriever))
    selected_keys = {"Accuracy@1", "Accuracy@3", "Accuracy@5", "Accuracy@10", "MRR@10", "Accuracy@100"}
    result = calculate_metrics(all_indexes, len(samples), selected_keys)
    print(result)
    save_results(result, "zalo_kaggle/Vietnamese_Embedding.json")
if __name__ == "__main__":
    main()