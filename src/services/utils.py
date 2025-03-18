"""Model with preprocessing utilities"""

import typing as tp
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import base


class PDFSimplePredictor:
    def __init__(self):
        # Инициализировали один раз и сохранили в атрибут
        pass
    #
    # def read_pdf(self) ->:


class PDFDLPredictor:
    """Process each article page with embedding model, RAG and LLM to find answers"""
    def __init__(self):
        # Create the model and init it one time
        self.llm = Ollama(model='llama3')
        self.embeddings = OllamaEmbeddings(model='bge-m3')

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
        # Load the PDF file and create a retriever to be used for providing context
        store = DocArrayInMemorySearch.from_documents(
            [page], embedding=self.embeddings
        )
        retriever = store.as_retriever()

        # Create the prompt template
        template = """
        Answer the question based only on the context provided, each question separate with ";". 
        IT SHOULD BE 14 ANSWERS. PLACE * SYMBOL AT THE END OF EACH ANSWER.
        It is scientific article and you need to find specific text and image elements in it.

        For example:
        Question: "Is it any data?"
        Output: "Is it any data?; Yes *"
        
        Respond with ONLY questions, answers and * symbols, with no additional commentary.

        Context: {context}

        Question: {question}
        """
        prompt = PromptTemplate.from_template(template)

        # Build the chain of operations
        chain = (
            {
                'context': retriever | self.format_docs,
                'question': RunnablePassthrough(),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        # Start asking questions and getting answers in a loop
        question = ';'.join(questions_list)
        answers_list = str(chain.invoke({'question': question})).split('*')

        return answers_list