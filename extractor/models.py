import uuid
from datetime import datetime

from django.db import models
from django.utils import timezone


def gen_uuid():
    return str(uuid.uuid4().hex)[:20]


class File(models.Model):
    uid = models.CharField(max_length=20, default=gen_uuid, unique=True)
    prosecure = models.CharField(max_length=40, default='Unknown', unique=False, null=True)
    name = models.CharField(max_length=5000, verbose_name="Name")
    upload_date = models.DateTimeField(default=timezone.now)
    successfully = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)

    class Meta:
        app_label = 'extractor'

    def __str__(self):
        return f'File - {self.name}'


class WithdrawalTransaction(models.Model):
    pan = models.CharField(max_length=16, verbose_name="PAN")
    code = models.CharField(max_length=7, verbose_name="Code", default='None')
    time = models.TimeField()
    amount = models.FloatField(default=0.0)

    class Meta:
        app_label = 'extractor'

    def __str__(self):
        return f'WTransaction - {self.pan[:3] + str(self.time)}'

    @classmethod
    def crt(cls, time, *args, **kwargs):
        inst = cls(time=datetime.strptime(time, '%H:%M:%S'), *args, **kwargs)
        return inst

    def save(self, *args, **kwargs):
        if not self.pk:
            if t := kwargs.get('time'):
                self.set_time(t)
        super(WithdrawalTransaction, self).save(*args, **kwargs)

    def set_time(self, t):
        self.time = datetime.strptime(t, '%H:%M:%S')
