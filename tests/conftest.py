"""Module with test fixtures"""
import os.path  # noqa: WPS301
from pathlib import Path
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from omegaconf import OmegaConf
import typing as tp

from src.containers.containers import Container
from src.routes import test_routs as paper_routes
from src.routes.routers import router as app_router

TESTS_DIR = Path("tests")


@pytest.fixture(scope="session")
def sample_pdf_bytes() -> tp.Generator[bytes, None]:
    with open(TESTS_DIR / 'pdf_articles' / '92923' / 'paper.pdf', "rb") as pdf_file:
        yield pdf_file.read()


@pytest.fixture(scope="session")
def app_config():
    return OmegaConf.load(os.path.join(TESTS_DIR, "test_config.yml"))


@pytest.fixture
def app_container(app_config):
    container = Container()
    container.config.from_dict(app_config)
    return container


@pytest.fixture
def wired_app_container(app_config):
    container = Container()
    container.config.from_dict(app_config)
    container.wire([paper_routes])
    yield container
    container.unwire()


@pytest.fixture
def test_app(wired_app_container):
    app = FastAPI()
    app.include_router(app_router)
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)
