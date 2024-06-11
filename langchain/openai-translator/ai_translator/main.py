import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from translator_fact import initialize_pdf_translator

if __name__ == "__main__":
    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator, config = initialize_pdf_translator()
    translator.translate_pdf(config.input_file, config.output_file_format, pages=None)
