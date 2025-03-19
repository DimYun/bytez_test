import typing as tp
import pymupdf
from tqdm import tqdm
from src.services.utils import PDFSimplePredictor, PDFDLPredictor
from langchain_community.document_loaders import PyMuPDFLoader


class ProcessPDF:
    """Class for rule-based processed of PDF"""
    status = "Start process PDF first"

    def __init__(
        self,
        pdf_simple_predictor: PDFSimplePredictor,
        pdf_dl_predictor: PDFDLPredictor,
        config: dict,
    ):
        self.pdf_simple_predictor = pdf_simple_predictor
        self.pdf_dl_predictor = pdf_dl_predictor
        self.config = config

    def process_pdf(
        self,
        pdf_name: str,
        pdf_bytes: bytes,
    ) -> pymupdf.Document:
        doc = pymupdf.open(
            filename=pdf_name,
            stream=pdf_bytes
        )
        return doc

    def count_pdf_pages(
        self,
        pdf_name: str,
        pdf_bytes: bytes,
    ) -> int:
        doc = self.process_pdf(pdf_name, pdf_bytes)
        return doc.page_count

    def test_pdf_pages(
        self,
        pdf_name: str,
        pdf_bytes: bytes,
    ) -> tp.List[str]:
        doc = self.process_pdf(pdf_name, pdf_bytes)
        pages_data = []
        for page in doc:
            pages_data.append(page.get_text('text'))
        return pages_data

    def simple_pdf_process(
        self,
        pdf_name: str,
        pdf_bytes: bytes,
    ) -> tp.List[tp.Dict[str, tp.List[str]]]:
        doc = self.process_pdf(pdf_name, pdf_bytes)
        pages_data = []
        for page_i, page in enumerate(doc):
            pages_data.append(
                {
                    "title": self.pdf_simple_predictor.parse_pdf(page_i, page)
                }
            )
        return pages_data

    def table_pdf_process(
        self,
        pdf_name: str,
        pdf_bytes: bytes,
    ) -> tp.List[tp.Dict[str, tp.List[tp.Any]]]:
        doc = self.process_pdf(pdf_name, pdf_bytes)
        tables_data = []
        for page in doc:
            tables_data.append(self.pdf_simple_predictor.parse_tables(page))
        return tables_data

    async def pdf_llm_process(
        self,
        pdf_url_or_filename: str,
    ) -> tp.List[tp.Dict[str, tp.List[str]]]:
        loader = PyMuPDFLoader(pdf_url_or_filename)
        doc = await loader.aload()
        pages_data = []
        for page_i, page in enumerate(tqdm(doc)):
            pages_data.append(
                {
                    "title": []
                }
            )
            llm_answers_page = self.pdf_dl_predictor.answer_for_pdf_page(
                page, self.config['questions']
            )
            print(llm_answers_page)
            for answer_i, answer in enumerate(llm_answers_page):
                if answer_i < len(self.config['data_mask']):
                    if not 'No' in answer:
                        pages_data[-1]["title"].append(self.config['data_mask'][answer_i])
        return pages_data
