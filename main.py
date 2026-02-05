import io

import fitz
import magic
from docx import Document
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from poligrapher.components.extractor import Extractor
from poligrapher.llms.openai import OpenAILLM
from poligrapher.utils import read_docx_text

load_dotenv()
llm = OpenAILLM()
extractor = Extractor(llm)

app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


ALLOWED_TYPES = {
    # 'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/msword'  # .doc (less common, but included for completeness)
}


@app.post("/policy_extraction/")
async def process_upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        await file.close()  # Ensure the file is closed
        mime_type = magic.from_buffer(contents, mime=True)

        if mime_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_TYPES)}"
            )

        if mime_type == 'application/pdf':
            doc = fitz.open(stream=contents, filetype="pdf")

            text = []
            for page in doc:
                text.append(page.get_text())
            input_text = "\n".join(text)
        else:
            doc = Document(io.BytesIO(contents))
            input_text = read_docx_text(doc)
        if len(input_text) >= 36000:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Too many characters. "
            )
        extracted = extractor.extract(input_text)
        return extracted
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500)


@app.get("/policy_extraction/")
async def process_upload_file(input_text: str):
    try:
        if len(input_text) >= 36000:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Too many characters. "
            )
        extracted = extractor.extract(input_text)
        return extracted
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500)
