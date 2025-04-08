# 通过将知识数据库中的文本进行行量化，完成向量数据局的建立，第一个版本使用的faiss数据库，感觉不是很好，这个版本使用lancedb
# lancedb也可以实现GPU的加速搜索，并且lancedb可以在同一行中存储文本、图片、向量等多种数据类型，非常方便，最主要的是开源
# 这里主要实现：从关系型数据库中读出知识库中的文本，然后进行行量化，最后存储到lancedb中
from .lancedb import LanceDBManager
from data_handle.text_dataset import DatabaseManager
from .embedding import EmbeddingSourceDate
from config.config import parameters
import pandas as pd

def mainKnowledge():
    # 读取数据库中的文本
    textDB = DatabaseManager()
    # all_texts = textDB.fetch_all(table_name=parameters.sql_table_name)
    all_texts = textDB.fetch_column(table_name=parameters.sql_table_name, column_name="content")
    textDB.close()

    # 将文本进行行量化
    emManager = EmbeddingSourceDate(embedding_model=parameters.use_embedding_model)
    embedding_list = emManager.embedding_single(all_texts)

    # 将行量化后的向量存储到lancedb中
    db_manager = LanceDBManager(parameters.LanceDB_path)
    id_list = [i for i in range(len(all_texts))]
    print("text的长度：", len(all_texts))
    print("embedding的长度：", len(embedding_list))
    print("id的长度：", len(id_list))
    # 数据存储{"id": 1, "text": "Hello world", "vector": [0.1, 0.2, 0.3, 0.9]},
    data = pd.DataFrame({"id": id_list, "text": all_texts, "vector": embedding_list.tolist()})
    print(data)
    if db_manager.create_table(parameters.LanceDB_table_name, data):
        db_manager.insert_data(parameters.LanceDB_table_name, data)




