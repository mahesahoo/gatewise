from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# test documetns
sentences = [
"Dogs are allowed in the office on Fridays",
"Pets can come to work on Furry Fridays",
"Remote work policy allows 3 days from home" ]

embeddings = model.encode(sentences)

# similarity between first and second sentence
sim_1_2 = np.dot(embeddings[0], embeddings[1])
sim_1_3 = np.dot(embeddings[0], embeddings[2])
sim_2_3 = np.dot(embeddings[1], embeddings[2])

print(f"Similarity (1 & 2): {sim_1_2*100:.1f}")
print(f"Similarity (1 & 3): {sim_1_3*100:.1f}")
print(f"Similarity (2 & 3): {sim_2_3*100:.1f}")
