import typing as tp
import pymupdf
from langchain_core.documents import base
from src.containers.containers import Container


class FakePDFSimplePredictor:
    """Fake Plate response for tests"""
    def parse_pdf(
            self,
            page_number: int,
            page_content: base.Document,
    ) -> tp.List[str]:
        return ["Title", "Authors", "Tables"]

    def parse_tables(
            self,
            page_content: base.Document,
    ) -> tp.Dict[str, tp.List[tp.Any]]:
        return {
            "table_text": ['testtesttest'],
            "table_images": ["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"],
        }


class FakePDFDLPredictor:
    """Fake Plate response for tests"""
    def answer_for_pdf_page(
            self,
            questions_list: tp.List[str],
            page: base.Document,
    ) -> tp.List[str]:
        answers = []
        for question in questions_list:
            answers.append(f"{question}; Yes")
        return answers


def test_simple_parce_not_fail(
    app_container: Container,
    sample_pdf_page: pymupdf.Page,
) -> None:
    with app_container.reset_singletons():
        with app_container.pdf_simple_predictor.override(FakePDFSimplePredictor()):
            pdf_simple_predictor = app_container.pdf_simple_predictor()
            pdf_simple_predictor.parse_pdf(1, sample_pdf_page)
            pdf_simple_predictor.parse_tables(sample_pdf_page)


def test_llm_parce_not_fail(
    app_container: Container,
    sample_pdf_page_llm: base.Document,
) -> None:
    with app_container.reset_singletons():
        with app_container.pdf_dl_predictor.override(FakePDFDLPredictor()):
            pdf_dl_predictor = app_container.pdf_dl_predictor()
            pdf_dl_predictor.answer_for_pdf_page(
                questions_list=["test?"],
                page=sample_pdf_page_llm
            )


def test_process_pdf_not_fail(
    app_container: Container,
    sample_pdf_bytes: bytes,
) -> None:
    pdf_load = app_container.pdf_processor()
    doc = pdf_load.process_pdf(
        pdf_name='test.pdf',
        pdf_bytes=sample_pdf_bytes,
    )
    assert len(doc) == 32


def test_count_pdf_pages_not_fail(
    app_container: Container,
    sample_pdf_bytes: bytes,
) -> None:
    pdf_count_pages = app_container.pdf_processor()
    pdf_pages = pdf_count_pages.count_pdf_pages(
        pdf_name='test.pdf',
        pdf_bytes=sample_pdf_bytes,
    )
    assert pdf_pages == 32


def test_test_pdf_pages_not_fail(
    app_container: Container,
    sample_pdf_bytes: bytes,
) -> None:
    pdf_load_pages = app_container.pdf_processor()
    pdf_pages_texts = pdf_load_pages.test_pdf_pages(
        pdf_name='test.pdf',
        pdf_bytes=sample_pdf_bytes,
    )
    assert isinstance(pdf_pages_texts[0], str)
