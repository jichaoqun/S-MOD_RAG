# 通过将知识数据库中的文本进行行量化，完成向量数据局的建立，第一个版本使用的faiss数据库，感觉不是很好，这个版本使用lancedb
# lancedb也可以实现GPU的加速搜索，并且lancedb可以在同一行中存储文本、图片、向量等多种数据类型，非常方便，最主要的是开源
import lancedb
import pandas as pd
from typing import List, Dict
import numpy as np
from config.config import parameters

class LanceDBManager:
    def __init__(self, db_path: str=parameters.LanceDB_path):
        """
        初始化 LanceDBManager。
        :param db_path: 数据库存储路径。
        """
        self.db_path = db_path
        self.db = lancedb.connect(db_path)

    def create_table(self, table_name: str, data, vector_column: str = "vector"):
        """
        创建一个新的表并插入初始数据。
        :param table_name: 表名。
        :param data: 包含数据的列表，每个元素是一个字典。
        :param vector_column: 存储向量的列名，默认为 "vector"。
        """
        # 检查表是否已经存在
        if table_name in self.db.table_names():
            print(f"表 '{table_name}' 已经存在，跳过创建。")
            return True
        
        # 将数据转换为 Pandas DataFrame
        if not isinstance(data, pd.DataFrame):
            df = pd.DataFrame(data)
        else:
            df = data
        
        # 检查是否包含向量列
        if vector_column not in df.columns:
            raise ValueError(f"数据中缺少向量列：{vector_column}")
        
        # 创建表
        self.db.create_table(table_name, data=df)
        return False

    def insert_data(self, table_name: str, data: List[Dict], unique_key: str = None):
        """
        向现有表中插入新数据，并确保数据不重复。
        :param table_name: 表名。
        :param data: 包含数据的列表，每个元素是一个字典。
        :param unique_key: 唯一标识符字段名（如 'id'）。如果为 None，则基于所有字段去重。
        """
        # 打开表
        table = self.db.open_table(table_name)
        
        # 获取当前表中的所有数据
        existing_data = table.to_pandas()
        
        # 转换为 Pandas DataFrame
        new_df = pd.DataFrame(data)
        
        # 根据 unique_key 去重
        if unique_key:
            # 确保 unique_key 存在于新数据中
            if unique_key not in new_df.columns:
                raise ValueError(f"新数据中缺少唯一标识符字段：{unique_key}")
            
            # 过滤掉已经存在的数据
            existing_keys = existing_data[unique_key].tolist()
            filtered_data = new_df[~new_df[unique_key].isin(existing_keys)]
        else:
            # 如果没有 unique_key，则基于所有字段去重
            # 1. 排除不可哈希列（如向量列）
            hashable_columns = [col for col in new_df.columns if not isinstance(new_df[col].iloc[0], (list, np.ndarray))]
            
            # 2. 标准化数据（去除空格、统一大小写等）
            def standardize_value(value):
                if isinstance(value, str):
                    return value.strip().lower()  # 统一大小写并去除空格
                return value
            
            existing_data[hashable_columns] = existing_data[hashable_columns].applymap(standardize_value)
            new_df[hashable_columns] = new_df[hashable_columns].applymap(standardize_value)
            
            # 3. 使用 merge 判断重复数据
            merged_data = pd.merge(
                existing_data[hashable_columns],
                new_df[hashable_columns],
                how="outer",
                indicator=True
            )
            filtered_data = new_df[merged_data["_merge"] == "right_only"]
        
        # 如果过滤后的数据为空，则无需插入
        if filtered_data.empty:
            print("没有新增数据，跳过插入。")
            return
        
        # 插入过滤后的数据
        table.add(filtered_data)
        print(f"成功插入 {len(filtered_data)} 条新数据。")

    # def search_vectors(self, table_name: str, query_vector: List[float], limit: int = 5) -> pd.DataFrame:
    #     """
    #     在表中执行向量相似性搜索。
    #     :param table_name: 表名。
    #     :param query_vector: 查询向量。
    #     :param limit: 返回结果的数量限制。
    #     :return: 包含搜索结果的 Pandas DataFrame。
    #     """
    #     # 打开表
    #     table = self.db.open_table(table_name)
        
    #     # 执行相似性搜索
    #     results = table.search(query_vector).limit(limit).to_pandas()
        
    #     return results
    def search_vectors(
        self,
        table_name: str,
        query_vector: List[float],
        limit: int = 5,
        filter_expression: str = None,
        metric: str = "L2",
        include_metadata: bool = True,
        offset: int = 0
    ) -> pd.DataFrame:
        """
        在表中执行向量搜索。
        :param table_name: 表名。
        :param query_vector: 查询向量。
        :param limit: 返回结果的数量限制。
        :param filter_expression: 过滤条件（SQL-like 表达式），例如 "category = 'A'" 或 "price > 100"。
        :param metric: 搜索使用的距离度量方法，默认为 "cosine"（余弦相似度）。其他选项包括 "l2"（欧氏距离）。Valid values are "L2", "cosine", or "dot".
        :param include_metadata: 是否包含元数据（非向量字段）在结果中，默认为 True。
        :param offset: 分页偏移量，用于跳过前 N 条结果。
        :return: 包含搜索结果的 Pandas DataFrame。
        """
        # 打开表
        table = self.db.open_table(table_name)
        # table.create_index(metric=metric, num_partitions=2, num_sub_vectors=2)
        # table.create_index(metric=metric)
        
        # 构建搜索查询
        search_query = table.search(query_vector, vector_column_name="vector").limit(limit).offset(offset)
        
        # 如果有过滤条件，添加到查询中
        if filter_expression:
            search_query = search_query.where(filter_expression)
        
        # 执行搜索并获取结果
        results = search_query.to_pandas()
        
        # 如果不包含元数据，则只保留向量列
        if not include_metadata:
            results = results[["vector"]]
        
        return results

    def get_all_data(self, table_name: str) -> pd.DataFrame:
        """
        获取表中的所有数据。
        :param table_name: 表名。
        :return: 包含所有数据的 Pandas DataFrame。
        """
        # 打开表
        table = self.db.open_table(table_name)
        
        # 获取所有数据
        return table.to_pandas()
    def delete_data(self, table_name: str, condition: str):
        """
        根据条件删除表中的数据。
        :param table_name: 表名。
        :param condition: 删除条件（SQL-like 表达式）。
        """
        # 打开表
        table = self.db.open_table(table_name)
        
        # 执行删除操作
        deleted_count = table.delete(condition)
        
        if deleted_count > 0:
            print(f"成功删除 {deleted_count} 条数据。")
        else:
            print("没有符合条件的数据可删除。")

    def delete_table(self, table_name: str):
        """
        删除指定的表。
        :param table_name: 表名。
        """
        # 删除表
        self.db.drop_table(table_name)

# 示例用法
if __name__ == "__main__":
    # 初始化数据库管理器
    db_manager = LanceDBManager("./data/sample-lancedb")

    # 示例数据
    sample_data = [
        {"id": 1, "text": "母猪产仔后，其生殖器官往往会发生了很大的变化，同时机体的抵抗力也会明显下降，此阶段若护理不当，将会影响到母猪产后机能的恢复。", "vector": [0.1, 0.2, 0.3, 0.9]},
        {"id": 2, "text": "LanceDB is awesome", "vector": [0.4, 0.5, 0.6, 0.9]},
        {"id": 3, "text": "Vector search is fast", "vector": [0.7, 0.8, 0.9, 0.9]}
    ]

    # 创建表并插入数据
    db_manager.create_table("example_table", sample_data)

    # 插入更多数据
    new_data = [
        {"id": 4, "text": "Another example", "vector": [0.2, 0.3, 0.4, 0.9]}
    ]
    db_manager.insert_data("example_table", new_data)

    # 执行向量搜索
    query_vector = [0.1, 0.2, 0.3, 0.4]
    # results = db_manager.search_vectors("example_table", query_vector, limit=2)
    # print("搜索结果：")
    # print(results)
    # 带过滤条件的搜索
    filtered_results = db_manager.search_vectors(
        "example_table",
        query_vector,
        limit=2
    )
    print("带过滤条件的搜索结果：")
    print(filtered_results)

    # 使用欧氏距离搜索
    l2_results = db_manager.search_vectors(
        "example_table",
        query_vector,
        limit=2,
        metric="l2"
    )
    print("使用欧氏距离的搜索结果：")
    print(l2_results)

    # 分页搜索
    paginated_results = db_manager.search_vectors(
        "example_table",
        query_vector,
        limit=1,
        offset=1
    )
    print("分页搜索结果：")
    print(paginated_results)

    # 获取所有数据
    all_data = db_manager.get_all_data("example_table")
    print("所有数据：")
    print(all_data)

    # # 删除表（可选）
    # db_manager.delete_table("example_table")