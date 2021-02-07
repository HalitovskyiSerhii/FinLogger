from pathlib import Path

from s3 import S3Gateway as s3
from extractor.models import File, WithdrawalTransaction
from extractor.parser import Parser
from finlogger.settings import DOWNLOAD_DIR


class ExtractorService:
    path = DOWNLOAD_DIR
    @classmethod
    def process(cls, path=None):
        pt = path if path else cls.path
        for unregistered in cls._unregistered():
            file = s3.download_file(unregistered, cls.path, rm=True)
            path_obj = getattr(file, 'path', Path(f'{cls.path}/{file.uid}'))
            extracted = Parser.pipe(path_obj)
            cls._save_instances(extracted)
            s3.save_file


    @classmethod
    def _save_instances(cls, extracted):
        instances = []
        for time, amount, pan, code in extracted:
            instances.append(WithdrawalTransaction.crt(
                time=time,
                amount=amount,
                pan=pan,
                code=code
            ))
        WithdrawalTransaction.objects.bulk_create(instances)


    @classmethod
    def _unregistered(cls):
        storage_files = set(s3.list_files())
        registered = set(File.objects.filter(processed=True).values_list('name', flat=True))
        storage_files.difference(registered)
