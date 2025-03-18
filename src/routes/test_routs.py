"""Module for FastAPI requests infrastructure"""

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, File, UploadFile, Request, Response, HTTPException, status
from fastapi.templating import Jinja2Templates

import requests
import io
import asyncio
import aiofiles

from src.containers.containers import Container
from src.routes.routers import router
from src.services.pdf_process import ProcessPDF

import typing as tp


templates = Jinja2Templates(directory="templates")


@router.get("/demo")
def dynamic_file(
    request: Request
):
    return templates.TemplateResponse("dynamic.html", {"request": request})


@router.get("/")
@inject
def get_content() -> str:
    return "hello world"


@router.post("/process_pdf", status_code=status.HTTP_200_OK)
@inject
async def process_content(
    content_pdf: UploadFile = File(
        ...,
        title="Number of pages in the pdf",
        description="Pdf file for inference.",
    ),
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, str]:
    pdf_data = await content_pdf.read()
    content_pdf.file.close()
    page_num = pdf_processor.count_pdf_pages(
        pdf_name=content_pdf.filename,
        pdf_bytes=pdf_data
    )
    return {
        "code": "200",
        "data": str(page_num),
        "error": "No Errors",
    }


@router.post("/process_arxiv_url")
@inject
async def process_content_url(
    arxiv_url: str = 'https://arxiv.org/pdf/2101.08809',
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, tp.Any]:
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, arxiv_url)
    pages_data = pdf_processor.test_pdf_pages(
        pdf_name=f"{arxiv_url.split('/')[-1]}.pdf",
        pdf_bytes=io.BytesIO(response.content)
    )
    return {
        "code": "200",
        "data": pages_data,
        "error": "No Errors",
    }


@router.post("/process_simple")
@inject
async def process_rule_based(
    arxiv_url: str = 'https://arxiv.org/pdf/2101.08809',
    in_file: UploadFile = File(None),
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, tp.Any]:
    data_bytes = None
    pdf_name = f"{arxiv_url.split('/')[-1]}.pdf"
    if in_file is not None:
        pdf_name = in_file.filename
        data_bytes = await in_file.read()
        in_file.file.close()
    else:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, arxiv_url)
        data_bytes = io.BytesIO(response.content)
    classification_output = pdf_processor.simple_pdf_process(
        pdf_name = pdf_name,
        pdf_bytes = data_bytes
    )
    return {
        "code": "200",
        "data": classification_output,
        "error": "No Errors",
    }

@router.post("/process_tables")
@inject
async def process_tables(
    arxiv_url: str = 'https://arxiv.org/pdf/2101.08809',
    in_file: UploadFile = File(None),
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, tp.Any]:
    data_bytes = None
    pdf_name = f"{arxiv_url.split('/')[-1]}.pdf"
    if in_file is not None:
        pdf_name = in_file.filename
        data_bytes = await in_file.read()
        in_file.file.close()
    else:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, arxiv_url)
        data_bytes = io.BytesIO(response.content)
    tables_output = pdf_processor.table_pdf_process(
        pdf_name = pdf_name,
        pdf_bytes = data_bytes
    )
    return {
        "code": "200",
        "data": tables_output,
        "error": "No Errors",
    }

@router.post("/process_llm_rag")
@inject
async def process_llm_rag(
    arxiv_url: str = 'https://arxiv.org/pdf/2101.08809',
    in_file: UploadFile = File(None),
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, tp.Any]:
    pdf_url_or_filename = arxiv_url
    if in_file is not None:
        pdf_url_or_filename = in_file.filename
        async with aiofiles.open(pdf_url_or_filename, 'wb') as out_file:
            content = await in_file.read()
            await out_file.write(content)
    tables_output = await pdf_processor.pdf_llm_process(
        pdf_url_or_filename = pdf_url_or_filename,
    )
    # TODO: delete or save files to DB
    return {
        "code": "200",
        "data": tables_output,
        "error": "No Errors",
    }
