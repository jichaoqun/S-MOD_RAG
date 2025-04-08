# 数据处理流程的总函数,包含数据处理的各个部分.将原始数据存储进关系型数据库中
import os, yaml, json
from tqdm import tqdm
from .read_data import DataReader
from .split_data import SentenceSplitter
from .text_dataset import DatabaseManager
from config.config import parameters


def mainDataHandle(data_path:str=None):
    """
    数据处理流程的总函数,包含数据处理的各个部分.将原始数据存储进关系型数据库中
    :param data_path: 数据文件路径
    :param config: 配置文件
    :return: 无
    """
    # 如果data_path为空，则使用配置文件中的data_path
    if data_path is None:
        data_path = parameters.source_data_path

    origin_data = []
    
    data_reader = DataReader()
    # 1.获取文件夹下的所有文件，并读取文件内容
    file_list = os.listdir(data_path)
    print(f"{data_path}路径下的文件有：", file_list)
    for file in file_list:
        input_format = file.split('.')[-1]
        file_path = os.path.join(data_path, file)
        try:
            origin_data.append(data_reader.read_data(file_path, input_format))
        except:
            print(f"{file}当前文件解析错误❌")

    # 2、对读取到的文本进行清洗，当前没有做

    # 3、对清洗后的数据进行分割
    ss_data = []
    SS = SentenceSplitter(language=parameters.split_language, 
                          mode=parameters.split_mode, 
                          chunk_size=parameters.split_chunk_size, 
                          chunk_overlap=parameters.split_chunk_overlap,)
    for i in tqdm(range(len(origin_data))):
        ss_data.extend(SS.process(origin_data[i]))
    if ss_data:
        print(f"共分割出{len(ss_data)}个句子")
        print("第一个句子", ss_data[0])
        print("分割完成✅")
        # print(ss_data)
        # return ss_data
    else:
        print("没有分割到句子")
        return

    # 4、将分割后的数据写入数据库
    db = DatabaseManager()
    db.create_table(parameters.sql_table_name, {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "content": "TEXT NOT NULL UNIQUE"})
    insert_data = [{"content": i} for i in ss_data]
    db.insert_many(parameters.sql_table_name, insert_data)
    print("写入数据库完成✅")

if __name__ == "__main__":
    mainDataHandle(data_path=None, config=None)
    