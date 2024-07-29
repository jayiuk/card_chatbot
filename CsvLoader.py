import langchain
import langchain_core
import langchain_text_splitters
from langchain_community.document_loaders.csv_loader import CSVLoader
import os

path = './consumer_data.csv'
encoding = 'utf-8'
source_column = '고객번호'

class csvload():
    def __init__(self, path, encoding, source_column):
        self.path = path
        self.encoding = encoding
        self.source_column = source_column

    def get_csv(self):
        loader = CSVLoader(file_path = self.path, encoding = self.encoding, source_column = self.source_column)
        data = loader.load()
        return data
