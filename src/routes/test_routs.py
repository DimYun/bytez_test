"""Module for FastAPI requests infrastructure"""
from os.path import split

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, File, UploadFile, Request, Response, HTTPException, status
from fastapi.templating import Jinja2Templates

import pymupdf
import requests
import io
import asyncio

# from src.containers.containers import Container
from src.routes.routers import router
# from src.services.goa_process import ProcessGranules, GetGOA

import typing as tp


templates = Jinja2Templates(directory="templates")

@router.get("/demo")
def dynamic_file(
    request: Request
):
    return templates.TemplateResponse("dynamic.html", {"request": request})


# @router.post("/dynamic")
# @inject
# def dynamic(
#     request: Request,
#     content_image: UploadFile = File(
#         # ...,
#         # title="PredictorInputImage",
#         # alias="image",
#         # description="Image for inference.",
#     ),
#     content_process: ProcessGranules = Depends(Provide[Container.content_process]),
# ):
#     image_data = content_image.file.read()
#     content_image.file.close()
#
#     image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
#     # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     prediction_data = content_process.process(
#         image,
#         str(content_image.filename),
#     )
#
#     return templates.TemplateResponse(
#         "dynamic.html",
#         {
#             "request": request,
#             "img": prediction_data['data'][0],
#             "mask": prediction_data['data'][1]
#         }
#     )
#
#
# @router.get("/show_goa")
# @inject
# def get_content(
#     request: Request,
#     goa_number: int,
#     goa_loader: GetGOA = Depends(Provide[Container.goa_loader]),
# ) -> tp.Any:
#     goa_code, goa_data, goa_error = goa_loader.get(str(goa_number))
#     return templates.TemplateResponse(
#         "dynamic.html",
#         {
#             "request": request,
#             "img": goa_data['data'][0],
#         }
#     )
#
#
# @router.get("/get_goa")
# @inject
# def get_content(
#     content_type: str,
#     goa_loader: GetGOA = Depends(Provide[Container.goa_loader]),
# ) -> tp.Any:
#     """
#     Define GET content
#     :param content_id: id of content
#     :param storage: container with storage functionality
#     :return: dict with content
#     """
#     goa_code, goa_data, goa_error = goa_loader.get(content_type)
#     raw_resp = {
#         "code": goa_code,
#         "data": goa_data,
#         "error": goa_error,
#     }
#     return {
#         "code": goa_code,
#         "data": goa_data,
#         "error": goa_error,
#     }


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
    )
) -> tp.Dict[str, str]:
    pdf_data = await content_pdf.read()
    content_pdf.file.close()
    doc = pymupdf.open(
        filename=content_pdf.filename,
        stream=pdf_data
    )
    page_num = doc.page_count
    return {
        "code": "200",
        "data": str(page_num),
        "error": "No Errors",
    }

@router.post("/process_arxiv_url")
@inject
async def process_content_url(
    arxiv_url: str = 'https://arxiv.org/pdf/2101.08809',
) -> tp.Dict[str, tp.Any]:
    # Process the PDF from URL or local file
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, arxiv_url)
    file = io.BytesIO(response.content)
    doc = pymupdf.open(
        filename=f"{arxiv_url.split('/')[-1]}.pdf",
        stream=file
    )
    pages_data = []
    for page in doc:
        pages_data.append(page.get_text('text'))

    return {
        "code": "200",
        "data": pages_data,
        "error": "No Errors",
    }

