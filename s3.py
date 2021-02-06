import asyncio
import traceback
from pathlib import Path

import boto3
from botocore.config import Config
from django.db.models import Model

from extractor.models import File
from finlogger.settings import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION_NAME, DEBUG, AWS_BUCKET_NAME, MINIO_HOST
from logger import LOGGER


class S3Gateway:
    s3 = boto3.resource('s3',
                        endpoint_url=f'http://{MINIO_HOST}',
                        aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY,
                        config=Config(signature_version='s3v4'),
                        region_name=AWS_REGION_NAME,
                        ).Bucket(AWS_BUCKET_NAME)

    @classmethod
    def send_file(cls, file_obj):
        created = False
        try:
            loop = asyncio.get_event_loop()
        except Exception:
            created = True
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.set_debug(DEBUG)
        try:
            if issubclass(type(file_obj), Model):
                loop.run_in_executor(None, cls.save_file, file_obj)
        except Exception as e:
            LOGGER.error(traceback.format_exc())
            if created:
                loop.close()

    bucket_name = AWS_BUCKET_NAME

    # using for save file to S3
    @classmethod
    def save_file(cls, file_model: File):
        try:
            with open(f'/tmp/{file_model.uid}', 'rb') as f:
                cls.s3.upload_fileobj(f, cls.bucket_name, file_model.uid)  # ExtraArgs={'ACL': 'public-read'})

            file_model.successfully = True
            file_model.save(update_fields=['successfully'])

            try:
                Path(f'/tmp/{file_model.uid}').unlink()
            except Exception:
                ...

        except Exception as e:
            LOGGER.error(traceback.format_exc())
            file_model.delete()
            raise

    # need for download file from S3
    @classmethod
    def download_file(cls, name, rm=False):
        file = File.objects.create(name=name)
        with open(f'/tmp/{file.uid}', 'wb') as f:
            cls.s3.download_fileobj(cls.bucket_name, name, f)
        if rm:
            obj = cls.s3.Object(AWS_BUCKET_NAME, f"{name}")
            obj.delete()
        cls.save_file(file)

    @classmethod
    def download_file_obj(cls, file):
        with open(f'/tmp/{file.uid}', 'wb') as f:
            cls.s3.download_fileobj(cls.bucket_name, file.uid, f)

    @classmethod
    def list_files(cls):
        files = []
        for file_name in cls.s3.objects.all():
            files.append(file_name)
        return files