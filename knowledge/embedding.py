# 使用预训练模型讲文本或者是其他的知识表达形式转换为向量
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from config.config import parameters

class EmbeddingSourceDate:
    def __init__(self, embedding_model=parameters.use_embedding_model):
        """
        :param embedding_model: "all-MiniLM-L6-v2" or "bge-m3"
        """
        if embedding_model == "all-MiniLM-L6-v2":
            self.model = SentenceTransformer(parameters.MiniLM_path)
        elif embedding_model == "bge-m3":
            self.model = SentenceTransformer(parameters.bge_m3_path)
        else:
            print("Have an error!!! Please input the correct embedding model")
    def embedding(self, sentences_list):
        """Return the embeddings of the sentences."""
        embedding_list = []
        print(len(sentences_list))
        print(len(sentences_list[0]))
        # for i in tqdm(range(len(sentences_list)),leave=False, desc="Embedding sentences"):
        #     embedding_list.append(self.model.encode(sentences_list[i], convert_to_numpy=True))
        for i in range(len(sentences_list)):
            embedding_list.append(self.model.encode(sentences_list[i], convert_to_numpy=True))
        print(len(embedding_list))
        print(embedding_list[0].shape)
        print(type(embedding_list[0]))
        return embedding_list
    def embedding_single(self, sentence):
        """Return the embedding of the sentence."""
        return self.model.encode(sentence)