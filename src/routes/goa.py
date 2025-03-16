"""Module for FastAPI requests infrastructure"""

import cv2
import numpy as np
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, File, UploadFile, Request
from fastapi.templating import Jinja2Templates

from src.containers.containers import Container
from src.routes.routers import router
from src.services.goa_process import ProcessGranules, GetGOA

import typing as tp


templates = Jinja2Templates(directory="templates")

@router.get("/")
def dynamic_file(
    request: Request
):
    return templates.TemplateResponse("dynamic.html", {"request": request})


@router.post("/dynamic")
@inject
def dynamic(
    request: Request,
    content_image: UploadFile = File(
        # ...,
        # title="PredictorInputImage",
        # alias="image",
        # description="Image for inference.",
    ),
    content_process: ProcessGranules = Depends(Provide[Container.content_process]),
):
    image_data = content_image.file.read()
    content_image.file.close()

    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    prediction_data = content_process.process(
        image,
        str(content_image.filename),
    )

    return templates.TemplateResponse(
        "dynamic.html",
        {
            "request": request,
            "img": prediction_data['data'][0],
            "mask": prediction_data['data'][1]
        }
    )


@router.get("/show_goa")
@inject
def get_content(
    request: Request,
    goa_number: int,
    goa_loader: GetGOA = Depends(Provide[Container.goa_loader]),
) -> tp.Any:
    goa_code, goa_data, goa_error = goa_loader.get(str(goa_number))
    return templates.TemplateResponse(
        "dynamic.html",
        {
            "request": request,
            "img": goa_data['data'][0],
        }
    )


@router.get("/get_goa")
@inject
def get_content(
    content_type: str,
    goa_loader: GetGOA = Depends(Provide[Container.goa_loader]),
) -> tp.Any:
    """
    Define GET content
    :param content_id: id of content
    :param storage: container with storage functionality
    :return: dict with content
    """
    goa_code, goa_data, goa_error = goa_loader.get(content_type)
    raw_resp = {
        "code": goa_code,
        "data": goa_data,
        "error": goa_error,
    }
    return {
        "code": goa_code,
        "data": goa_data,
        "error": goa_error,
    }


@router.post("/process_content")
@inject
def process_content(
    content_image: UploadFile = File(
        ...,
        title="PredictorInputImage",
        alias="image",
        description="Image for inference.",
    ),
    content_process: ProcessGranules = Depends(Provide[Container.content_process]),
) -> dict:
    """
    Define POST
    :param content_image: input image
    :param content_process: container with process functionality
    :return: dictionary with results in json format
    """
    image_data = content_image.file.read()
    content_image.file.close()

    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    prediction_data = content_process.process(
        image,
        str(content_image.filename),
    )
    return {
        "code": 200,
        "data": prediction_data,
        "error": 'No errors',
    }
