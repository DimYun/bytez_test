from http import HTTPStatus
from fastapi.testclient import TestClient


def test_init(client: TestClient):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK

    response_string = response.text
    assert response_string == '"hello world"'


def test_process_pdf(client: TestClient, sample_pdf_bytes: bytes):
    files = {
        'content_pdf': sample_pdf_bytes,
    }
    response = client.post("/process_pdf", files=files)
    assert response.status_code == HTTPStatus.OK

    predicted_output = response.json()["data"]
    assert isinstance(predicted_output, str)
    assert int(predicted_output) == 32


def test_process_url(client: TestClient):
    response = client.post(
        "/process_arxiv_url?arxiv_url=https%3A%2F%2Farxiv.org%2Fpdf%2F2101.08809",
    )
    assert response.status_code == HTTPStatus.OK

    predicted_output = response.json()["data"][0]
    assert isinstance(predicted_output, str)
