import importlib


def test_imports():
    modules = [
        "open_encroachment",
        "open_encroachment.cli",
        "open_encroachment.pipeline",
        "open_encroachment.utils.geo",
        "open_encroachment.ingestion.satellite",
        "open_encroachment.ingestion.ground_sensors",
        "open_encroachment.ingestion.aerial",
        "open_encroachment.ingestion.social_media",
        "open_encroachment.nlp.nlp_engine",
        "open_encroachment.models.threat_classifier",
        "open_encroachment.models.severity",
        "open_encroachment.comms.dispatcher",
        "open_encroachment.evidence.chain_of_custody",
        "open_encroachment.analytics.predictive",
        "open_encroachment.case_management.case_manager",
    ]
    for m in modules:
        importlib.import_module(m)
