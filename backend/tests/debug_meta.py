import pickle

with open("storage/vector_store/meta.pkl", "rb") as f:
    meta = pickle.load(f)

print("Nombre de chunks :", len(meta))
print("Exemple d'entrée :")
print(meta[0])
