import sqlite3
import os
from config.config import parameters
class DatabaseManager:
    def __init__(self, db_path:str=parameters.sql_db_path):
        """
        数据库管理类，支持动态创建表、插入数据、查询数据等基本功能。
        """
        if not os.path.exists(db_path):  # 仅创建目录
            os.makedirs(db_path)
        print("db_path",db_path)
        db_path = os.path.join(db_path, "source_data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, schema):
        """
        创建表（如果不存在）。
        
        :param table_name: 表名
        :param schema: 字典形式的表结构，例如：{"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "content": "TEXT NOT NULL UNIQUE"}
        """
        columns = ", ".join([f"{col} {dtype}" for col, dtype in schema.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.cursor.execute(query)
        self.conn.commit()

    def exists(self, table_name, column_name, value):
        """
        检查某个值是否已存在于表的指定列中。
        
        :param table_name: 表名
        :param column_name: 要检查的列名
        :param value: 需要检查的值
        :return: 存在返回 True，不存在返回 False
        """
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column_name} = ? LIMIT 1)"
        self.cursor.execute(query, (value,))
        return self.cursor.fetchone()[0] == 1

    def insert(self, table_name, data):
        """
        插入单条数据（如果不存在）。
        
        :param table_name: 表名
        :param data: 字典格式的行数据
        :return: True（成功插入），False（数据已存在）
        """
        if self.exists(table_name, list(data.keys())[0], list(data.values())[0]):
            return False  # 数据已存在，插入失败

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()
        return True  # 插入成功

    def insert_many(self, table_name, data_list):
        """
        批量插入数据（自动去重）。
        
        :param table_name: 表名
        :param data_list: 字典列表，每个字典是一行数据
        :return: 插入的条数
        """
        if not data_list:
            return 0

        inserted_count = 0
        for data in data_list:
            if self.insert(table_name, data):  # 逐条插入，避免重复
                inserted_count += 1

        return inserted_count

    def insert_any(self, table_name, data, ignore_duplicate=True):
        """
        插入数据（支持单行和多行）。
        
        :param table_name: 表名
        :param data: 字典（单行）或列表（多行，每行是一个字典）
        :param ignore_duplicate: 是否忽略重复数据（默认 True）
        """
        if isinstance(data, dict):  # 单行插入
            data = [data]

        if not data:
            return

        columns = ", ".join(data[0].keys())
        placeholders = ", ".join(["?" for _ in data[0]])
        insert_clause = "INSERT OR IGNORE" if ignore_duplicate else "INSERT"

        query = f"{insert_clause} INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = [tuple(d.values()) for d in data]
        self.cursor.executemany(query, values)
        self.conn.commit()

    def fetch_all(self, table_name, columns="*"):
        """
        查询表的所有数据。
        
        :param table_name: 表名
        :param columns: 需要查询的列（默认 '*' 查询所有列）
        :return: 结果列表
        """
        query = f"SELECT {columns} FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetch_by_id(self, table_name, ids, id_column="id", columns="*"):
        """
        根据 ID 查询数据。
        
        :param table_name: 表名
        :param ids: 单个 ID 或 ID 列表
        :param id_column: ID 列的名称（默认 "id"）
        :param columns: 查询的列（默认 "*"）
        :return: 结果列表
        """
        if isinstance(ids, int):
            ids = [ids]

        placeholders = ", ".join(["?"] * len(ids))
        query = f"SELECT {columns} FROM {table_name} WHERE {id_column} IN ({placeholders})"
        self.cursor.execute(query, ids)
        return self.cursor.fetchall()

    def fetch_column(self, table_name, column_name):
        """
        查询表的特定列数据。
        
        :param table_name: 表名
        :param column_name: 需要查询的列名
        :return: 该列的所有数据
        """
        query = f"SELECT {column_name} FROM {table_name}"
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def count_rows(self, table_name):
        """
        获取表的行数。
        
        :param table_name: 表名
        :return: 该表的行数
        """
        query = f"SELECT COUNT(*) FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def delete_by_id(self, table_name, record_id, id_column="id"):
        """
        根据 ID 删除数据。
        
        :param table_name: 表名
        :param record_id: 需要删除的记录 ID
        :param id_column: ID 列的名称（默认 "id"）
        """
        query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
        self.cursor.execute(query, (record_id,))
        self.conn.commit()

    def close(self):
        """关闭数据库连接。"""
        self.conn.close()

# 示例用法
if __name__ == "__main__":
    # 初始化数据库
    db = DatabaseManager()

    # 创建表（如知识库）
    db.create_table("knowledge", {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "content": "TEXT NOT NULL UNIQUE"})

    # 插入数据（单条）
    db.insert("knowledge", {"content": "这是第一条知识"})
    db.insert("knowledge", {"content": "这是第一4条知识"})

    # 插入数据（多条）
    db.insert_many("knowledge", [{"content": "第二条知识"}, {"content": "第三条知识"}, {"content": "第三条知识"}])

    db.insert_many("knowledge", [{"content":"one"}, {"content":"two"}, {"content":"three"}])

    # 查询所有数据
    print(db.fetch_all("knowledge"))

    # 查询特定列
    print(db.fetch_column("knowledge", "content"))

    # 按 ID 查询
    print(db.fetch_by_id("knowledge", [1, 2]))

    # 统计表中数据条数
    print(db.count_rows("knowledge"))

    # 删除某条数据
    db.delete_by_id("knowledge", 1)

    # 关闭数据库
    db.close()

