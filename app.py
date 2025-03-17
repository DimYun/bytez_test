"""Main module for FastAPI car plates service."""
import argparse

import uvicorn
from fastapi import FastAPI
from omegaconf import OmegaConf

from src.containers.containers import Container
from src.routes import test_routs as test_routs
from src.routes.routers import router as app_router


def create_app() -> FastAPI:
    """
    Create FastAPI application with DPI Containers
    :return: FastAPI application
    """
    container = Container()
    cfg = OmegaConf.load("configs/config.yaml")
    container.config.from_dict(cfg)
    container.wire([test_routs])

    app = FastAPI(
        title=cfg['title'],
        description="""
Science article parser API.

## Data

You can:

* respond with "hello world" when the "/" endpoint is hit 
* accept a PDF file upload and return the number of pages in the document
* accept a link to an Arxiv research paper and return the text content of each page as a JSON array
* classify content blocks within each page of the PDF with rule-based engine
* extract tables from the PDF as both images and text
* classify content blocks within each page of the PDF with DNN, LLM, or any combo models
* process dataset of papers


""",
        summary=cfg['summary'],
        version=cfg['version'],
        terms_of_service=cfg['terms_of_service'],
        contact=cfg['contact'],
        license_info=cfg['license_info'],
    )
    app.include_router(app_router)  #, prefix="/", tags=["articles"])
    return app


if __name__ == "__main__":

    def arg_parse() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("port", type=int, help="port number")
        return parser.parse_args()

    app = create_app()
    args = arg_parse()
    uvicorn.run(app, port=args.port, host="127.0.0.1")
