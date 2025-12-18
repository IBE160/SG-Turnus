# backend/tests/test_export_service.py

import unittest
from unittest.mock import patch
from io import BytesIO
from backend.app.services.export_service import ExportService

class TestExportService(unittest.TestCase):

    def setUp(self):
        self.export_service = ExportService()
        self.content = "This is a test content."

    @patch('backend.app.services.export_service.ExportService._export_to_pdf')
    def test_export_pdf(self, mock_export_to_pdf):
        mock_export_to_pdf.return_value = BytesIO(b"pdf content")
        result = self.export_service.export(self.content, "pdf")
        mock_export_to_pdf.assert_called_once_with(self.content)
        self.assertEqual(result.read(), b"pdf content")

    @patch('backend.app.services.export_service.ExportService._export_to_docx')
    def test_export_docx(self, mock_export_to_docx):
        mock_export_to_docx.return_value = BytesIO(b"docx content")
        result = self.export_service.export(self.content, "docx")
        mock_export_to_docx.assert_called_once_with(self.content)
        self.assertEqual(result.read(), b"docx content")

    @patch('backend.app.services.export_service.ExportService._export_to_csv')
    def test_export_csv(self, mock_export_to_csv):
        mock_export_to_csv.return_value = BytesIO(b"csv content")
        result = self.export_service.export(self.content, "csv")
        mock_export_to_csv.assert_called_once_with(self.content)
        self.assertEqual(result.read(), b"csv content")

    def test_export_unsupported_format(self):
        with self.assertRaises(ValueError):
            self.export_service.export(self.content, "unsupported")

    def test_export_to_pdf_content(self):
        # This is a basic test and does not check the actual PDF content
        result = self.export_service._export_to_pdf(self.content)
        self.assertIsInstance(result, BytesIO)
        self.assertGreater(len(result.read()), 0)

    def test_export_to_docx_content(self):
        # This is a basic test and does not check the actual DOCX content
        result = self.export_service._export_to_docx(self.content)
        self.assertIsInstance(result, BytesIO)
        self.assertGreater(len(result.read()), 0)

    def test_export_to_csv_content(self):
        result = self.export_service._export_to_csv(self.content)
        self.assertIsInstance(result, BytesIO)
        # A more specific test could be to parse the csv and check the content
        self.assertIn(b"content", result.read())

if __name__ == '__main__':
    unittest.main()
