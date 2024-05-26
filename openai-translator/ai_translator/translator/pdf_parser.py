from io import BufferedReader, BytesIO
from typing import Optional

import pdfplumber
from book import Book, Content, ContentType, Page, TableContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG


class PDFParser:
    def __init__(self):
        pass

    def parse_pdf(
        self, path_or_fp: str | BufferedReader | BytesIO, pages: Optional[int] = None
    ) -> Book:
        bookPath = ""
        if isinstance(path_or_fp, str):
            bookPath = path_or_fp
        book = Book(bookPath)

        with pdfplumber.open(path_or_fp) as pdf:
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()

                # Store the original text content
                raw_text = pdf_page.extract_text()
                tables = pdf_page.extract_tables()

                # Remove each cell's content from the original text
                for table_data in tables:
                    for row in table_data:
                        for cell in row:
                            raw_text = raw_text.replace(cell, "", 1)

                # Handling text
                if raw_text:
                    # Remove empty lines and leading/trailing whitespaces
                    raw_text_lines = raw_text.splitlines()
                    cleaned_raw_text_lines = [
                        line.strip() for line in raw_text_lines if line.strip()
                    ]
                    cleaned_raw_text = "\n".join(cleaned_raw_text_lines)

                    text_content = Content(
                        content_type=ContentType.TEXT, original=cleaned_raw_text
                    )
                    page.add_content(text_content)
                    LOG.debug(f"[raw_text]\n {cleaned_raw_text}")

                # Handling tables
                if tables:
                    table = TableContent(tables)
                    page.add_content(table)
                    LOG.debug(f"[table]\n{table}")

                book.add_page(page)

        return book
