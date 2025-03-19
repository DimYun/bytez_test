import typing as tp
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import base
import io
import base64


class PDFSimplePredictor:
    def __init__(self):
        pass

    def parse_pdf(
        self,
        page_number: int,
        page_content: base.Document,
    ) -> tp.List[str]:
        # TODO: Use CV for detect Sub, Reference, Standalone, Math, Divider, TOC and others
        page_data = []
        page_data.append("Print Notice")
        if page_number > 0:
            page_data.append("Footer")

        page_blocks = page_content.get_text('blocks')
        if len(page_blocks) > 0:
            page_data.append("Paragraph")

        imgblocks = ['Fig' in i[-3] for i in page_blocks]
        if sum(imgblocks) > 0:
            page_data.append("Image")

        headerblocks = [i[-2] <= 2 for i in page_blocks]
        if sum(headerblocks) > 0:
            page_data.append("Heading")
            page_data.append("Header")

        page_text = page_content.get_text('text')
        if page_number == 0:
            page_data.append("Title")
        if '@' in page_text and page_number == 0:
            page_data.append("Authors")
        if 'Fig' in page_text or 'Pic' in page_text:
            page_data.append("Caption")

        if len(list(page_content.find_tables())) > 0:
            page_data.append("Tables")
        return page_data

    def parse_tables(
        self,
        page_content: base.Document,
    ) -> tp.Dict[str, tp.List[tp.Any]]:

        table_data = {
            "table_text": [],
            "table_images": [],
        }
        tabs = page_content.find_tables()
        if len(list(tabs)) > 0:
            pix = page_content.get_pixmap().pil_image()
            for tab in tabs:
                x_min, y_min, x_max, y_max = tab.bbox
                table_img = pix.crop((x_min, y_min, x_max, y_max))
                buffered = io.BytesIO()
                table_img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue())
                table_data["table_text"].append(tab.extract())
                table_data["table_images"].append(img_str)
        return table_data


class PDFDLPredictor:
    """Process each article page with embedding model, RAG and LLM to find answers"""
    def __init__(self, config: dict):
        self.config = config
        self.llm = Ollama(model=config['llm_model'])
        self.embeddings = OllamaEmbeddings(model=config['embedding_model'])

    def format_docs(
        self,
        docs: tp.List[base.Document]
    ) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    def answer_for_pdf_page(
        self,
        page: base.Document,
        questions_list: tp.List[str],
    ) -> tp.List[str]:
        store = DocArrayInMemorySearch.from_documents(
            [page], embedding=self.embeddings
        )
        retriever = store.as_retriever()

        prompt = PromptTemplate.from_template(self.config['llm_template'])

        chain = (
            {
                'context': retriever | self.format_docs,
                'question': RunnablePassthrough(),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        question = ';'.join(questions_list)
        answers_list = str(chain.invoke({'question': question})).split('*')

        return answers_list
