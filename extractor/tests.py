from datetime import datetime
from pathlib import Path

from django.test import TestCase

# Create your tests here.
from extractor.models import WithdrawalTransaction, File
from extractor.parser import Parser


class TransactionTestCase(TestCase):
    def setUp(self) -> None:
        self.valid_obj = {
            "pan": '706064XXXXXX8931',
            "time": '06:58:42',
            "amount": '1,650.00',
            "code": '649456',
        }
        self.invalid_obj = {
            "pan": '706064XXXXXX8931',
            "amount": '1,650.00',
            "code": 'UTRNNO',
        }

    def test_transaction_creation(self):
        valid_obj = WithdrawalTransaction.crt(**self.valid_obj)
        valid_obj.save()
        self.assertEqual(WithdrawalTransaction.objects.count(), 1)
        self.assertEqual(valid_obj.time, datetime.strptime(self.valid_obj['time'], '%H:%M:%S'))
        self.assertEqual(valid_obj.amount, float(self.valid_obj['amount'].replace(',', '')))
        self.assertEqual(valid_obj.pan, self.valid_obj['pan'])
        self.assertEqual(valid_obj.code, int(self.valid_obj['code']))

    def test_invalid_params(self):
        try:
            inv = WithdrawalTransaction.crt(**self.invalid_obj)
        except TypeError as ex:
            self.assertTrue(True)

    def test_invalid_fields(self):
        try:
            self.invalid_obj.update({"time": '06:58:42'})
            inv = WithdrawalTransaction.crt(**self.invalid_obj)
        except ValueError as ex:
            self.assertTrue(True)

    def tearDown(self) -> None:
        WithdrawalTransaction.objects.all().delete()


class ParserCase(TestCase):
    def setUp(self) -> None:
        self.first_page = \
            """----------------------- Page 1-----------------------

ProSecure                                                       8464-20161125-065747-231211-TOP.ENC 

RESP_CODE: 
 06:58:46 TRANSACTION REQUEST BI  AADA 
 06:58:47 TRANSACTION REPLY NEXT 267 FUNCTION Z000Z0005025 
 ---------- 
 4018 25/11/16 ATM: Z1234567 
 06:58:38     0.00  UAH 
 0 -    0 -    0 -    0 
 706064XXXXXX8931 0 
AUTH. CODE: 649432 UTRNNO: 3093649432 RESP_CODE: 
 06:58:58 TRANSACTION REQUEST AD  AACA 
 06:58:59 TRANSACTION REPLY NEXT 128 FUNCTION Z000Z000E065B067C067H061 
 06:59:03 CARD(70606431********) TAKEN 
 06:59:11 CASH REQUEST: 01010501 

                                                                                               1 / 217 

----------------------- Page 2-----------------------

ProSecure                                                       8464-20161125-065747-231211-TOP.ENC 
"""
        self.first_page_result = \
            """RESP_CODE: 
 06:58:46 TRANSACTION REQUEST BI  AADA 
 06:58:47 TRANSACTION REPLY NEXT 267 FUNCTION Z000Z0005025 
 ---------- 
 4018 25/11/16 ATM: Z1234567 
 06:58:38     0.00  UAH 
 0 -    0 -    0 -    0 
 706064XXXXXX8931 0 
AUTH. CODE: 649432 UTRNNO: 3093649432 RESP_CODE: 
 06:58:58 TRANSACTION REQUEST AD  AACA 
 06:58:59 TRANSACTION REPLY NEXT 128 FUNCTION Z000Z000E065B067C067H061 
 06:59:03 CARD(70606431********) TAKEN 
 06:59:11 CASH REQUEST: 01010501 
"""
        self.inner_pages = \
            """----------------------- Page 3-----------------------

ProSecure                                                       8464-20161125-065747-231211-TOP.ENC 

 07:15:36 TRANSACTION REQUEST CG  BHGA 
 07:15:37 TRANSACTION REPLY NEXT 036 FUNCTION Z000Z0005025 
 07:15:39 TRANSACTION REQUEST AF  B  A 
 07:15:40 TRANSACTION REPLY NEXT 295 FUNCTION Z000Z0005025 
 ---------- 
 4028 25/11/16 ATM: Z1234567 
 07:15:41 CASH WITHDRAWAL  1,200.00  UAH 
 2 -    1 -    0 -    2 
 706064XXXXXX3921 0 
AUTH. CODE: 656185 UTRNNO: 3093656185 RESP_CODE: 00 
 07:16:19 GO OUT OF SERVICE COMMAND 
 07:16:22 <- TRANSACTION END 
 07:16:24 GO IN SERVICE COMMAND 
 07:16:28 GO IN SERVICE COMMAND 
 07:16:57 -> TRANSACTION START 

                                                                                               3 / 217 

----------------------- Page 4-----------------------

ProSecure                                                       8464-20161125-065747-231211-TOP.ENC 

 07:16:57 TRACK 2 DATA: 80603048******** 
 07:17:01 PIN ENTERED 
 07:17:02 TRANSACTION REQUEST BB  B DA 
 07:17:02 TRANSACTION REPLY NEXT 607 FUNCTION Z000Z000Z0005025 
 ---------- 
 4034 25/11/16 ATM: Z1234567 
 07:16:57     0.00  UAH 
 0 -    0 -    0 -    0 
 806030XXXXXX6451 0 
AUTH. CODE: 656802 UTRNNO: 3093656802 RESP_CODE: 
 07:17:21 CARD(80603048********) TAKEN 
 07:17:23 <- TRANSACTION END 
 07:17:28 -> TRANSACTION START 
 07:17:28 TRACK 2 DATA: 80603048******** 
 07:17:33 PIN ENTERED 
 07:17:33 TRANSACTION REQUEST BB  B DA 
 07:17:34 TRANSACTION REPLY NEXT 607 FUNCTION Z000Z000Z0005025 
 ---------- 

                                                                                               4 / 217 

----------------------- Page 5-----------------------

ProSecure                                                       8464-20161125-065747-231211-TOP.ENC 
"""
        self.inner_pages_result = \
            [""" 07:15:36 TRANSACTION REQUEST CG  BHGA 
 07:15:37 TRANSACTION REPLY NEXT 036 FUNCTION Z000Z0005025 
 07:15:39 TRANSACTION REQUEST AF  B  A 
 07:15:40 TRANSACTION REPLY NEXT 295 FUNCTION Z000Z0005025 
 ---------- 
 4028 25/11/16 ATM: Z1234567 
 07:15:41 CASH WITHDRAWAL  1,200.00  UAH 
 2 -    1 -    0 -    2 
 706064XXXXXX3921 0 
AUTH. CODE: 656185 UTRNNO: 3093656185 RESP_CODE: 00 
 07:16:19 GO OUT OF SERVICE COMMAND 
 07:16:22 <- TRANSACTION END 
 07:16:24 GO IN SERVICE COMMAND 
 07:16:28 GO IN SERVICE COMMAND 
 07:16:57 -> TRANSACTION START 
""",
             """ 07:16:57 TRACK 2 DATA: 80603048******** 
 07:17:01 PIN ENTERED 
 07:17:02 TRANSACTION REQUEST BB  B DA 
 07:17:02 TRANSACTION REPLY NEXT 607 FUNCTION Z000Z000Z0005025 
 ---------- 
 4034 25/11/16 ATM: Z1234567 
 07:16:57     0.00  UAH 
 0 -    0 -    0 -    0 
 806030XXXXXX6451 0 
AUTH. CODE: 656802 UTRNNO: 3093656802 RESP_CODE: 
 07:17:21 CARD(80603048********) TAKEN 
 07:17:23 <- TRANSACTION END 
 07:17:28 -> TRANSACTION START 
 07:17:28 TRACK 2 DATA: 80603048******** 
 07:17:33 PIN ENTERED 
 07:17:33 TRANSACTION REQUEST BB  B DA 
 07:17:34 TRANSACTION REPLY NEXT 607 FUNCTION Z000Z000Z0005025 
 ---------- 
"""]
        self.last_page = \
            """ 

                                                                                               216 / 217 

----------------------- Page 217-----------------------

ProSecure                                                       8464-20161125-065747-231211-TOP.ENC 

 23:11:55 TRANSACTION REQUEST CG  BHGA 
 23:11:56 TRANSACTION REPLY NEXT 036 FUNCTION Z000Z0005025 
 23:11:57 TRANSACTION REQUEST AF  B  A 
 23:11:58 TRANSACTION REPLY NEXT 295 FUNCTION Z000Z0005025 
 ---------- 
 827 25/11/16 ATM: Z1234567 
 23:11:56 CASH WITHDRAWAL 0.00 
 INSUFFICIENT FUNDS 
 806030XXXXXX7254 0 
AUTH. CODE:  UTRNNO: 3095239401 RESP_CODE: 20 
 23:12:10 CARD(80603048********) TAKEN 
 23:12:11 <- TRANSACTION END 

 !!!BROKEN BLOCKS!!! 

                                                                                                217 / 217 """
        self.last_page_results = \
            """ 23:11:55 TRANSACTION REQUEST CG  BHGA 
 23:11:56 TRANSACTION REPLY NEXT 036 FUNCTION Z000Z0005025 
 23:11:57 TRANSACTION REQUEST AF  B  A 
 23:11:58 TRANSACTION REPLY NEXT 295 FUNCTION Z000Z0005025 
 ---------- 
 827 25/11/16 ATM: Z1234567 
 23:11:56 CASH WITHDRAWAL 0.00 
 INSUFFICIENT FUNDS 
 806030XXXXXX7254 0 
AUTH. CODE:  UTRNNO: 3095239401 RESP_CODE: 20 
 23:12:10 CARD(80603048********) TAKEN 
 23:12:11 <- TRANSACTION END 
 !!!BROKEN BLOCKS!!! 
                                                                                                217 / 217 """
        self.file_obj = File.objects.create(name='8464-20161125-065747-231211-TOP.ENC.txt')
        self.file = Path('123 8464-20161125-065747-231211-TOP.ENC.txt')
        self.file.touch()
        self.file_obj.path = self.file

        self.pipe_results = [('07:15:41', '1,200.00', '706064XXXXXX3921', '656185')]

    def test_first_page_extraction(self):
        with self.file.open('wt') as f:
            f.write(self.first_page)
        pages, _, broken = Parser.read_pages(self.file)
        self.assertEqual(pages[1], self.first_page_result)
        self.assertEqual(Parser.prosecure, '8464-20161125-065747-231211-TOP.ENC')

    def test_inner_page_extraction(self):
        with self.file.open('wt') as f:
            f.write(self.inner_pages)
        pages, _, broken = Parser.read_pages(self.file)
        self.assertEqual(pages[1:3], self.inner_pages_result)
        self.assertEqual(Parser.prosecure, '8464-20161125-065747-231211-TOP.ENC')

    def test_last_page_extraction(self):
        with self.file.open('wt') as f:
            f.write(self.last_page)
        pages, _, broken = Parser.read_pages(self.file)
        self.assertEqual(broken, self.last_page_results)
        self.assertEqual(Parser.prosecure, '8464-20161125-065747-231211-TOP.ENC')

    def test_pipe(self):
        with self.file.open('wt') as f:
            f.write(self.inner_pages)
        res = Parser.pipe(self.file)
        self.assertEqual(res, self.pipe_results)
        self.assertEqual(Parser.prosecure, '8464-20161125-065747-231211-TOP.ENC')

    def tearDown(self) -> None:
        self.file_obj.delete()
        self.file.unlink()
