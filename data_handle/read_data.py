# data_preprocessing/read_data.py

import json
import csv
import PyPDF2
from bs4 import BeautifulSoup  # 用于解析HTML
import pandas as pd  # 用于处理复杂格式（如Excel）
import logging  # 日志记录模块

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

class DataReader:
    def __init__(self):
        pass

    def read_txt(self, file_path):
        """
        读取纯文本文件。
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                logging.info(f"Successfully read TXT file: {file_path}")
                return f.read()
        except Exception as e:
            logging.error(f"Error reading TXT file {file_path}: {e}")
            return None

    def read_pdf(self, file_path):
        """
        读取PDF文件。
        """
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages])
            logging.info(f"Successfully read PDF file: {file_path}")
            return text
        except Exception as e:
            logging.error(f"Error reading PDF file {file_path}: {e}")
            return None

    def read_json(self, file_path, key="content"):
        """
        读取JSON文件，并提取指定字段的内容。
        默认提取"content"字段。
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logging.info(f"Successfully read JSON file: {file_path}")
                return data.get(key, "")  # 如果没有指定字段，则返回空字符串
        except Exception as e:
            logging.error(f"Error reading JSON file {file_path}: {e}")
            return None

    def read_csv(self, file_path, column="text"):
        """
        读取CSV文件，并提取指定列的内容。
        默认提取"text"列。
        """
        try:
            # 使用pandas读取CSV文件，避免内存占用问题
            df = pd.read_csv(file_path, usecols=[column], encoding="utf-8")
            texts = df[column].dropna().tolist()  # 去除空值并转换为列表
            logging.info(f"Successfully read CSV file: {file_path}")
            return "\n".join(texts)  # 将所有行合并为一个字符串
        except Exception as e:
            logging.error(f"Error reading CSV file {file_path}: {e}")
            return None

    def read_html(self, file_path):
        """
        读取HTML文件，并提取正文内容。
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                text = soup.get_text(separator="\n")  # 提取纯文本，保留换行符
            logging.info(f"Successfully read HTML file: {file_path}")
            return text
        except Exception as e:
            logging.error(f"Error reading HTML file {file_path}: {e}")
            return None

    def read_excel(self, file_path, sheet_name=0, column="text"):
        """
        读取Excel文件，并提取指定列的内容。
        :param file_path: 文件路径
        :param sheet_name: 工作表名称或索引（默认为第一个工作表）
        :param column: 指定列名
        :return: 提取的内容
        """
        try:
            # 使用pandas读取Excel文件，避免内存占用问题
            df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=[column])
            texts = df[column].dropna().tolist()  # 去除空值并转换为列表
            logging.info(f"Successfully read Excel file: {file_path}")
            return "\n".join(texts)  # 将所有行合并为一个字符串
        except Exception as e:
            logging.error(f"Error reading Excel file {file_path}: {e}")
            return None

    def read_data(self, file_path, input_format, **kwargs):
        """
        根据输入格式选择对应的读取方法。
        :param file_path: 文件路径
        :param input_format: 输入格式（txt, pdf, json, csv, html, excel）
        :param kwargs: 额外参数（如JSON字段名、CSV列名、Excel工作表等）
        :return: 读取的文本内容
        """
        if input_format == "txt":
            return self.read_txt(file_path)
        elif input_format == "pdf":
            return self.read_pdf(file_path)
        elif input_format == "json":
            key = kwargs.get("key", "content")  # 默认字段名为"content"
            return self.read_json(file_path, key=key)
        elif input_format == "csv":
            column = kwargs.get("column", "text")  # 默认列名为"text"
            return self.read_csv(file_path, column=column)
        elif input_format == "html":
            return self.read_html(file_path)
        elif input_format == "excel":
            sheet_name = kwargs.get("sheet_name", 0)  # 默认为第一个工作表
            column = kwargs.get("column", "text")  # 默认列名为"text"
            return self.read_excel(file_path, sheet_name=sheet_name, column=column)
        else:
            logging.error(f"Unsupported input format: {input_format}")
            return None