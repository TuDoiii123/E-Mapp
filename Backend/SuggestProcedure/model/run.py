from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
# Load the fine-tuned model

df_root = pd.read_csv("C:/Users/ADMIN/E-Map/Backend/SuggestProcedure/data/dichvucong_QuangNinh - dichvucong_QuangNinh.csv")

model = SentenceTransformer("C:/Users/ADMIN/E-Map/Backend/SuggestProcedure/model/fine_tuned_model")

query = input("Nhập câu hỏi của bạn: ")
query_embedding = model.encode(query, convert_to_tensor=True)

procedure_names = df_root['NAME'].tolist()
procedure_embeddings = model.encode(procedure_names, convert_to_tensor=True)

similarity_scores = cos_sim(query_embedding, procedure_embeddings)[0]
results_df = pd.DataFrame({
    'procedure_internal_id': df_root['ID'],
    'procedure_name': df_root['NAME'],
    'similarity_score': similarity_scores.cpu().numpy()
})


filtered_results = results_df[results_df['similarity_score'] > 0.5]

sorted_results = filtered_results.sort_values(by='similarity_score', ascending=False)

top_4_procedure_ids = sorted_results.head(4)['procedure_internal_id'].tolist()
print("Top 4 procedure IDs with similarity score > 0.5:")
for idx, proc_id in enumerate(top_4_procedure_ids):
    print(f"  {idx+1}. ID: {proc_id}")

print("\nDetailed top results:")
display(sorted_results.head(4))