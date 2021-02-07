from celery import shared_task

from extractor.services import ExtractorService


@shared_task
def scan_storage():
    ExtractorService.process()
