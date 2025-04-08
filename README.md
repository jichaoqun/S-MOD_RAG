# S-MOD_RAG
* 此开源项目的目的：从零开始，使用阶段模块化方式搭建一个RAG系统。
* 愿望：逐渐完善项目，单纯体验RAG各个部分的不同方法，给LLM提供更多的可能性。

# 介绍
>* 大语言模型（Large Language Model, LLM）当前在通用的文本理解和生成任务中都有很好的表现。然而，对于一些特定领域的问题，LLM可能需要更多的领域知识才能给出准确的答案；在最新的知识方面，LLM更是不可能回答。因此，开始出现使用LLM与领域知识相结合的方式，让LLM在特定的领域能够有较好的表现。
>* 当前LLM正在向外扩展的任务有两个，一个是RAG（提升LLM的检索能力）更多的还是用运用LLM的文本处理、归纳总结的能力；一个是agent（分析决策能力）理解人类意图，分解任务，作为一个中央处理器的角色。
>* 当前RAG的框架有很多，常规的[dify](https://github.com/langgenius/dify)、[ragflow](https://github.com/infiniflow/ragflow/tree/main)、[FlashRAG](https://github.com/RUC-NLPIR/FlashRAG)、[AutoRAG](https://github.com/Marker-Inc-Korea/AutoRAG)等；基于图搜索的[graphrag](https://github.com/microsoft/graphrag)、[LightRAG](https://github.com/HKUDS/LightRAG)等；还有一些RAG的工具[anything-llm](https://github.com/Mintplex-Labs/anything-llm)、[Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat)等。上述的工具基本都能实现RAG的功能，但是当前项目的冗余功能很多，并且对RAG的实现并不是很明确，[Modular RAG](https://arxiv.org/abs/2407.21059)是模块的方式，但是没有代码。本项目旨在实现一个模块化的RAG系统，对RAG的各个部分实现解耦。
>* 当下RAG的搜索已经不在局限于文本类之间的查询，依托于强大的特征提取模型，RAG正在向多模态领域扩展，提供文本与图像之间的相互查询，提升多模态模型的能力。

# 项目结构
在本项目中，将RAG的实现分为了四个部分：
* 1、[源数据处理](data_handle/说明.md)；
* 2、[知识库](knowledge/说明.md)；
* 3、[检索器](retrieval/说明.md)；
* 4、[生成器](generation/说明.md)。

## TODO
* [x] 基础流程走通
* [x] 解析文本：txt与pdf
* [x] 基于句子级别的文本分割
* [x] lancedb向量数据库
* [ ] 源数据处理,解析txt与pdf之外的其他格式
* [ ] 实体识别、段落切分
* [ ] 建立知识图谱类知识库
* [ ] 检索器：分层检索、基于图搜索的检索器
* [ ] 生成器
* [ ] web界面

## 目录结构
```
├── data
│   ├── all source data         #源数据
├── config
│   ├── config.py               #配置文件
├── data_handle
│   ├── dataset    
│   │   ├── split dataset       #切分后的数据，关系行数据库存储
│   ├── main_data.py            #数据处理的入口
│   ├── read_data.py            #读取数据
│   ├── split_data.py           #切分数据
│   ├── text_dataset.py         #数据存储控制
├── knowledge
│   ├── dataset
│   │   ├── vector dataset      #向量数据库位置
│   ├── model
│   │   ├── vembedding model    #向量化模型
│   ├── main_knowledge.py       #知识库处理的入口
│   ├── lancedb.py              #向量数据库
│   ├── embedding.py            #向量化
├── retrieval
│   ├── searce_similar_text.py  #检索相似文本
├── generation
│   ├── LLM.py                  #生成器
├── web-ui
│   ├── 打算做一个web界面
├── main.py                     #主程序
```

# 快速开始
## 1、环境说明
```
主要包：PyPDF2、pandas、langchain、bs4、lancedb、sentence_transformers、ollama
```
## 2、源数据
```
在data目录下边放置源数据，目前只尝试解析了txt与部分pdf
```
## 3、配置文件
```
在config中，配置文件config.py中，需要配置的参数有：
MiniLM_path = 'all-MiniLM-L6-v2'    # MiniLM模型路径
bge_m3_path = "model/bge-m3"        # bge-m3模型路径

当前使用ollama在本地运行大模型，需要配置ollama的host与port，
当前配置文件中为默认本地的地址与端口号
```
## 4、运行
```
直接在根目录下运行：python main.py
```



