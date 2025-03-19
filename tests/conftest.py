"""Module with test fixtures"""
from pathlib import Path
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from omegaconf import OmegaConf
import pymupdf
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import base

from src.containers.containers import Container
from src.routes import test_routs
from src.routes.routers import router as app_router

TESTS_DIR = Path("tests")


@pytest.fixture(scope="session")
def sample_pdf_bytes() -> bytes:
    with open(TESTS_DIR / 'pdf_articles' / '92923' / 'paper.pdf', "rb") as pdf_file:
        yield pdf_file.read()


@pytest.fixture(scope="session")
def sample_pdf_page() -> pymupdf.Page:
    doc = pymupdf.open(filename=TESTS_DIR / 'pdf_articles' / '92923' / 'paper.pdf')
    yield doc[0]


@pytest.fixture(scope="session")
def sample_pdf_page_llm() -> base.Document:
    loader = PyMuPDFLoader(TESTS_DIR / 'pdf_articles' / '92923' / 'paper.pdf')
    doc = loader.load()
    yield doc[0]


@pytest.fixture(scope="session")
def app_config():
    return OmegaConf.load(TESTS_DIR / "test_config.yml")


@pytest.fixture
def app_container(app_config):
    container = Container()
    container.config.from_dict(app_config)
    return container


@pytest.fixture
def wired_app_container(app_config):
    container = Container()
    container.config.from_dict(app_config)
    container.wire([test_routs])
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
