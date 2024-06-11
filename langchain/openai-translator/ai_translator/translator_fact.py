from typing import Tuple

from translator import PDFTranslator, TranslationConfig
from utils import ArgumentParser


def initialize_pdf_translator() -> Tuple[PDFTranslator, TranslationConfig]:
    # 解析命令行
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()

    # 初始化配置单例
    config = TranslationConfig()
    config.initialize(args)
    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    return PDFTranslator(config.model_name, config.ai_api_base_url), config
