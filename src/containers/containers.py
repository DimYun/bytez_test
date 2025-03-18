"""Module with DPI conteiners"""
from dependency_injector import containers, providers

from src.services.pdf_process import ProcessPDF
from src.services.utils import PDFSimplePredictor, PDFDLPredictor


class Container(containers.DeclarativeContainer):
    """Container for DPI plates"""
    config = providers.Configuration()

    pdf_simple_predictor =  providers.Singleton(PDFSimplePredictor)

    pdf_dl_predictor = providers.Singleton(PDFDLPredictor)

    pdf_processor = providers.Singleton(
        ProcessPDF,
        pdf_simple_predictor=pdf_simple_predictor.provider(),
        pdf_dl_predictor=pdf_dl_predictor.provider(),
    )

    #
    # content_process = providers.Singleton(
    #     ProcessGranules,
    #     storage=store.provider(),
    #     granules_mask_predictor=granules_mask_predictor.provider(),
    # )
    #
    # goa_loader = providers.Singleton(
    #     GetGOA,
    #     config=config.goa_uploader,
    # )
