import os
import json
import sys
class parameters:
    # 1\原始数据
    source_data_path = os.path.join(os.path.abspath(os.getcwd()), "data")    # 原始数据路径
    sql_db_path = os.path.join(os.path.abspath(os.getcwd()), "data_handle", "dataset") # 数据库路径
    sql_table_name = "data1"    # 数据表名称

    split_language = "zh"    # 分割语言：zh or en
    split_mode = "sentence"  # 分割方法：sentence or paragraph
    split_chunk_size = 100   # 句子长度
    split_chunk_overlap = 20  # 句子重叠长度


    # 2\知识库
    MiniLM_path = 'D:/DL/rag/RAG-ppline/model/all-MiniLM-L6-v2'
    bge_m3_path = "D:/DL/rag/RAG-ppline/model/bge-m3"
    use_embedding_model = "bge-m3"   # embedding_model: "all-MiniLM-L6-v2" or "bge-m3"
    LanceDB_path = os.path.join(os.path.abspath(os.getcwd()), "knowledge", "dataset", "lancedb")
    LanceDB_table_name = "data1"


    # 3\检索器
    seach_type = "simple" #搜索方法：simple or layering
    search_topk = 10
    search_table = "data1"

    # 4\生成器
    use_type= "ollama"
    host_port = "http://0.0.0.0:11434"
    llm_model= "qwen2.5:0.5b"
    temperature= 0.95


    # 5\输出
    output_path= "./output"
    