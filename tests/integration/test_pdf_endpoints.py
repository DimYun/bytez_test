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

