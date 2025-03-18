"""Module for FastAPI requests infrastructure"""
from os.path import split

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, File, UploadFile, Request, Response, HTTPException, status
from fastapi.templating import Jinja2Templates

import pymupdf
import requests
import io
import asyncio

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
    # file: tp.Optional[bytes] = File(None),
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, tp.Any]:
    # Process the PDF from URL or local file
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, arxiv_url)
    classification_output = pdf_processor.simple_pdf_process(
        pdf_name = f"{arxiv_url.split('/')[-1]}.pdf",
        pdf_bytes = io.BytesIO(response.content)
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
    # file: tp.Optional[bytes] = File(None),
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, tp.Any]:
    # Process the PDF from URL or local file
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, arxiv_url)
    tables_output = pdf_processor.table_pdf_process(
        pdf_name = f"{arxiv_url.split('/')[-1]}.pdf",
        pdf_bytes = io.BytesIO(response.content)
    )
    return {
        "code": "200",
        "data": tables_output,
        "error": "No Errors",
    }

@router.post("/process_llm_rag")
@inject
async def process_tables(
    arxiv_url: str = 'https://arxiv.org/pdf/2101.08809',
    # file: tp.Optional[bytes] = File(None),
    pdf_processor: ProcessPDF = Depends(Provide[Container.pdf_processor]),
) -> tp.Dict[str, tp.Any]:
    # Process the PDF from URL or local file
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, arxiv_url)
    tables_output = pdf_processor.table_pdf_process(
        pdf_name = f"{arxiv_url.split('/')[-1]}.pdf",
        pdf_bytes = io.BytesIO(response.content)
    )
    return {
        "code": "200",
        "data": tables_output,
        "error": "No Errors",
    }