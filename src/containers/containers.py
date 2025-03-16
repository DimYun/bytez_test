"""Module with DPI conteiners"""
from dependency_injector import containers, providers

from src.services.goa_process import ProcessGranules, Storage, GetGOA
from src.services.preprocess_utils import GranulesPredictor


class Container(containers.DeclarativeContainer):
    """Container for DPI plates"""
    config = providers.Configuration()

    store = providers.Singleton(
        Storage,
        config=config.content_process,
    )

    granules_mask_predictor = providers.Singleton(
        GranulesPredictor,
        config=config.background_model_parameters,
    )

    content_process = providers.Singleton(
        ProcessGranules,
        storage=store.provider(),
        granules_mask_predictor=granules_mask_predictor.provider(),
    )

    goa_loader = providers.Singleton(
        GetGOA,
        config=config.goa_uploader,
    )
