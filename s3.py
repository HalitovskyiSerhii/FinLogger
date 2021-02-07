import asyncio
import traceback
from pathlib import Path

import boto3
from botocore.config import Config

from extractor.models import File
from finlogger.settings import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION_NAME, DEBUG, AWS_BUCKET_NAME, MINIO_HOST, \
    MINIO_PORT
from logger import LOGGER


class S3Gateway:
    s3 = boto3.resource('s3',
                        endpoint_url=f'http://{MINIO_HOST}:{MINIO_PORT}',
                        aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY,
                        config=Config(signature_version='s3v4'),
                        region_name=AWS_REGION_NAME,
                        ).Bucket(AWS_BUCKET_NAME)

    bucket_name = AWS_BUCKET_NAME

    @classmethod
    def save_file(cls, file_model: File, path: Path = Path('/tmp')):
        try:
            pt = getattr(file_model, 'path', path / file_model.name)
            with pt.open('rb') as f:
                cls.s3.upload_fileobj(f, file_model.uid)  # ExtraArgs={'ACL': 'public-read'})

            file_model.successfully = True
            file_model.processed = True
            file_model.save(update_fields=['successfully', 'processed'])

            try:
                pt.unlink()
            except Exception:
                ...

        except Exception as e:
            LOGGER.error(traceback.format_exc())
            file_model.delete()
            raise

    @classmethod
    def download_file(cls, name, path):
        file = File.objects.create(name=name)
        file.path = path/file.name
        with file.path.open('wb') as f:
            cls.s3.download_fileobj(name, f)
        return file

    @classmethod
    def rm_file(cls, name):
        obj = cls.s3.Object(f"{name}")
        obj.delete()

    @classmethod
    def list_files(cls):
        files = []
        for file_name in cls.s3.objects.all():
            files.append(file_name.key)
        return files
