import os
import time

from config.config import parameters
from data_handle.main_data import mainDataHandle
from knowledge.main_knowledge import mainKnowledge
from retrieval.searce_similar_text import SearchSimilarText
from generation.LLM import generate_ollama

from knowledge.embedding import EmbeddingSourceDate

if __name__ == '__main__':
    # 1\读取数据，对数据处理，进行分割、或是其他可能的处理
    mainDataHandle()

    # 2\知识库处理，将分割好的数据进行数据向量化，并存储在lanceDB数据库中
    mainKnowledge()

    embedding = EmbeddingSourceDate()   #可以使用第二步已经定义好的，为了解耦可使用不同的编码器选择新的定义

    # 3\检索相似文本创建检索器
    search_similar_text = SearchSimilarText()
    while True:
        # 获取用户输入
        question = input("\n你：")
        
        # 退出条件
        if question.lower() in ['exit', 'quit', 'q', '结束']:
            print("退出对话。")
            break

        # 生成查询向量
        start_time = time.time()
        question_v = embedding.embedding_single(question)
        embedding_time = time.time()
        print("embedding time: ", embedding_time - start_time)

        # 从知识库搜索相关内容
        find_text = search_similar_text.simple_searce(query_vector=question_v, table_name=parameters.search_table)

        search_time = time.time()
        print("search time: ", search_time - embedding_time)
        # 生成回答
        answer = generate_ollama(question, find_text)
        generate_time = time.time()
        print("generate time: ", generate_time - search_time)

        # 输出答案
        print("\nAI：" + answer)


