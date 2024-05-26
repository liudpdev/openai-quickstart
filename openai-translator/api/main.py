import os
import sys
import uuid
from enum import Enum
from io import BufferedReader
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(f"{parent_dir}/ai_translator")
# sys.path.append(os.path.dirname(os.path.abspath(parent_dir)))
from ai_translator.model import OpenAIModel  # noqa: E402
from ai_translator.translator import PDFTranslator  # noqa: E402

app = FastAPI()
translator = PDFTranslator(OpenAIModel(base_url=os.getenv("OPENAI_BASE_URL")))


class FileFormat(str, Enum):
    pdf = "pdf"
    md = "markdown"


@app.post("/translate_pdf")
async def translate_pdf(
    file: Annotated[UploadFile, File(description="The PDF file to translate")],
    translated_file_format: Annotated[
        FileFormat, Query(description="The format of the translated file")
    ] = FileFormat.pdf,
):
    file_name_tokens = file.filename.rsplit(".", 1)
    file_ext = file_name_tokens[-1]
    if file_ext != "pdf":
        raise HTTPException(status_code=422, detail="Only PDF files are supported.")

    temp_dir = f"{current_dir}/tmp"

    output_file_path = f"{temp_dir}/{uuid.uuid4()}.{translated_file_format.name}"
    translator.translate_pdf(
        path_or_fp=BufferedReader(file.file),
        file_format=translated_file_format.value,
        output_file_path=output_file_path,
    )

    return FileResponse(
        path=output_file_path,
        filename=f"{file_name_tokens[0]}.{translated_file_format.name}",
    )


if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--reload", action="store_true", default=False)
    args = parser.parse_args()

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=args.reload)
