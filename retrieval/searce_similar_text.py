from typing import List
from config.config import parameters
import os

from knowledge.lancedb import LanceDBManager


class SearchSimilarText:
    def __init__(self, LanceDB_path: str = parameters.LanceDB_path,
                       topk: int = parameters.search_topk):
        self.LanceDB_path = LanceDB_path
        self.topk = topk

        self.LanceDBManager = LanceDBManager(self.LanceDB_path)

    def simple_searce(self, query_vector: List[float], table_name: str, topk: int = None,  filter_expression: str = None):
        if topk is None:
            topk = self.topk
        return self.LanceDBManager.search_vectors(table_name=table_name,
                                           query_vector=query_vector,
                                           limit=topk,
                                           filter_expression=filter_expression)
