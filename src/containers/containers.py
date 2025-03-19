from dependency_injector import containers, providers
from src.services.pdf_process import ProcessPDF
from src.services.utils import PDFSimplePredictor, PDFDLPredictor


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    pdf_simple_predictor =  providers.Singleton(
        PDFSimplePredictor
    )

    pdf_dl_predictor = providers.Singleton(
        PDFDLPredictor,
        config=config,
    )

    pdf_processor = providers.Singleton(
        ProcessPDF,
        pdf_simple_predictor=pdf_simple_predictor.provider(),
        pdf_dl_predictor=pdf_dl_predictor.provider(),
        config=config,
    )
