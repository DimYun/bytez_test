"""Main module for FastAPI car plates service."""
import argparse

import uvicorn
from fastapi import FastAPI
from omegaconf import OmegaConf

from src.containers.containers import Container
from src.routes import goa as goa_routes
from src.routes.routers import router as app_router


def create_app() -> FastAPI:
    """
    Create FastAPI application with DPI Containers
    :return: FastAPI application
    """
    container = Container()
    cfg = OmegaConf.load("configs/config.yaml")
    container.config.from_dict(cfg)
    container.wire([goa_routes])

    app = FastAPI(
        title=cfg['title'],
        description="""
Granulometric Optical Analysis (GOA) dataset API.

## Data

You can:

* Get GOA dataset images (*jpg)
* Process you own image with granules to separate them from background or to select first layer

""",
        summary=cfg['summary'],
        version=cfg['version'],
        terms_of_service=cfg['terms_of_service'],
        contact=cfg['contact'],
        license_info=cfg['license_info'],
    )
    app.include_router(app_router, prefix="/goa", tags=["goa"])
    return app


if __name__ == "__main__":

    def arg_parse():
        """
        Parse command line
        :return: dictionary with command line arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("port", type=int, help="port number")
        return parser.parse_args()

    app = create_app()
    args = arg_parse()
    uvicorn.run(app, port=args.port, host="127.0.0.1")
