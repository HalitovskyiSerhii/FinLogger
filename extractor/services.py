from pathlib import Path

from s3 import S3Gateway as s3
from extractor.models import File, WithdrawalTransaction
from extractor.parser import Parser
from finlogger.settings import DOWNLOAD_DIR


class ExtractorService:
    path = DOWNLOAD_DIR

    @classmethod
    def process(cls, path=None):
        pt = Path(path if path else cls.path)
        for unregistered in cls._unregistered():
            file = s3.download_file(unregistered, pt)
            extracted = Parser.pipe(file.path)
            file.prosecure = Parser.prosecure
            file.save(update_fields=['prosecure'])
            cls._save_instances(extracted)
            s3.save_file(file, pt)
            s3.rm_file(unregistered)

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
        registered = set(File.objects.filter(processed=True).values_list('uid', flat=True))
        return storage_files.difference(registered)
