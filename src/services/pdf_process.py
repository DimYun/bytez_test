"""Module for define APP plate process."""

import zipfile
import io
import base64

import os
import typing as tp
from pathlib import Path
import pymupdf


from src.services.utils import PDFSimplePredictor, PDFDLPredictor
from langchain_community.document_loaders import PyMuPDFLoader


class ProcessPDF:
    """Class for rule-based processed of PDF"""
    status = "Start process PDF first"

    def __init__(
        self,
        pdf_simple_predictor: PDFSimplePredictor,
        pdf_dl_predictor: PDFDLPredictor
    ):
        self.pdf_simple_predictor = pdf_simple_predictor
        self.pdf_dl_predictor = pdf_dl_predictor
        print("finish process plate init")

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
        # TODO: Use CV for detect Footnote, Sub, Reference, Standalone, Math, Divider, TOC and others

        for page_i, page in enumerate(doc):
            pages_data.append(
                {
                    "title": []
                }
            )

            pages_data[-1]["title"].append("Print Notice")
            if page_i > 0:
                pages_data[-1]["title"].append("Footer")

            page_blocks = page.get_text('blocks')
            if len(page_blocks) > 0:
                pages_data[-1]["title"].append("Paragraph")

            imgblocks = ['Fig' in i[-3] for i in page_blocks]
            if sum(imgblocks) > 0:
                pages_data[-1]["title"].append("Image")

            headerblocks = [i[-2] <= 2 for i in page_blocks]
            if sum(headerblocks) > 0:
                pages_data[-1]["title"].append("Heading")
                pages_data[-1]["title"].append("Header")

            # if len(page.objects['line']) == 1 or len(page.objects['line']) % 2 == 1:
            #     pages_data[-1]["title"].append("Footnote")

            # is_bold_char = 0
            # for i in page.objects['char']:
            #     if 'Bold' in i['fontname']:
            #         is_bold_char += 1
            # if is_bold_char:
            #     pages_data[-1]["title"].append("Heading")
            #     pages_data[-1]["title"].append("Header")

            page_text = page.get_text('text')
            if page_i == 0:
                pages_data[-1]["title"].append("Title")
            if '@' in page_text and page_i == 0:
                pages_data[-1]["title"].append("Authors")
            if 'Fig' in page_text or 'Pic' in page_text:
                pages_data[-1]["title"].append("Caption")

            if len(list(page.find_tables())) > 0:
                pages_data[-1]["title"].append("Tables")

        return pages_data

    def table_pdf_process(
        self,
        pdf_name: str,
        pdf_bytes: bytes,
    ) -> tp.List[tp.Dict[str, tp.List[tp.Any]]]:
        doc = self.process_pdf(pdf_name, pdf_bytes)
        tabels_data = []
        # TODO: Use CV for detect Sub, Reference, Standalone, Math, Divider, TOC and others

        for page_i, page in enumerate(doc):
            tabels_data.append(
                {
                    "table_text": [],
                    "table_images": [],
                }
            )
            tabs = page.find_tables()
            if len(list(tabs)) > 0:
                pix = page.get_pixmap().pil_image()
                for tab in tabs:
                    x_min, y_min, x_max, y_max = tab.bbox
                    # table_img =  pix[y_min:y_max, x_min:x_max, :]
                    table_img = pix.crop((x_min, y_min, x_max, y_max))
                    buffered = io.BytesIO()
                    table_img.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue())
                    tabels_data[-1]["table_text"].append(tab.extract())
                    tabels_data[-1]["table_images"].append(img_str)
        return tabels_data

    async def pdf_llm_process(
        self,
        pdf_url_or_filename: str,
    ) -> tp.List[tp.Dict[str, tp.List[tp.Any]]]:

        loader = PyMuPDFLoader(pdf_url_or_filename)
        doc = loader.load()

        pages_data = []
        # TODO: refactor pdf text to sentences?
        for page_i, page in enumerate(doc):
            pages_data.append(
                {
                    "title": []
                }
            )
            self.pdf_dl_predictor.answer_for_pdf_page(page)
            page_text = page.get_text('text')


