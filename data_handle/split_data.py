import spacy
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

class SentenceSplitter:
    def __init__(self, language="en", mode="sentence", chunk_size=100, chunk_overlap=20):
        """
        文本分割类，支持中英文，并提供句子级和段落级的分割方式。

        :param language: 语言类型，支持 "en"（英文）或 "zh"（中文）。
        :param mode: 分割模式，支持 "sentence"（按句子分割）、"paragraph"（按段落分割）。
        :param chunk_size: 每个分割块的最大长度。
        :param chunk_overlap: 块之间的重叠部分长度，防止信息丢失。
        """
        self.language = language
        self.mode = mode
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 加载 spaCy 语言模型
        if self.language == "en":
            self.nlp = spacy.load("en_core_web_sm")
            self.sentence_separators = ["\n", ".", "?", "!"]
            self.paragraph_separator = "\n\n"
        elif self.language == "zh":
            self.nlp = spacy.load("zh_core_web_sm")
            self.sentence_separators = ["\n", "。", "？", "！"]
            self.paragraph_separator = "\n\n"
        else:
            raise ValueError("Unsupported language. Please choose 'en' or 'zh'.")

    def split_sentences(self, text):
        """
        按句子级别进行分割。
        :param text: 输入的文本
        :return: 句子列表
        """
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]

    def split_paragraphs(self, text):
        """
        按段落级别进行分割。
        :param text: 输入的文本
        :return: 段落列表
        """
        return [p.strip() for p in text.split(self.paragraph_separator) if p.strip()]

    def split_chunks(self, text):
        """
        先按模式（句子/段落）分割，再进行固定长度的分块。
        :param text: 输入的文本
        :return: 分割后的 chunk 列表
        """
        if self.mode == "sentence":
            segments = self.split_sentences(text)
        elif self.mode == "paragraph":
            segments = self.split_paragraphs(text)
        else:
            raise ValueError("Unsupported mode. Please choose 'sentence' or 'paragraph'.")

        text_for_splitting = "\n".join(segments)

        # 使用 LangChain 进行固定长度分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.sentence_separators if self.mode == "sentence" else [self.paragraph_separator]
        )
        return text_splitter.split_text(text_for_splitting)

    def process(self, text):
        """
        处理文本，返回分割后的 chunk 列表。
        :param text: 输入的文本
        :return: 分割后的 chunk
        """
        return self.split_chunks(text)


def split_sentences(text, chunk_size=100, chunk_overlap=20):
    """
    按句子级别进行分割。
    :param text: 输入的文本
    :return: 句子列表
    """
    text_len = min(200, len(text))
    chinese_chars = sum(1 for c in text[0:text_len] if '\u4e00' <= c <= '\u9fff')
    english_chars = sum(1 for c in text[0:text_len] if c.isascii() and c.isalpha())

    if chinese_chars > english_chars:
        pattern = r'(?<=[。！？. \n])'
        segments = [s.strip() for s in re.split(pattern, text) if s.strip()]
    else:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        segments = [sent.text.strip() for sent in doc.sents]

    text_for_splitting = "\n".join(segments)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n", ".", "?", "!"]
    )
    return text_splitter.split_text(text_for_splitting)


def split_paragraphs(text, chunk_size=512, chunk_overlap=30):
    """
    按段落级别进行分割。
    :param text: 输入的文本
    :return: 段落列表
    """
    segments = [p.strip() for p in text.split("\n\n") if p.strip()]
    text_for_splitting = "\n\n".join(segments)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n"]
    )
    return text_splitter.split_text(text_for_splitting)