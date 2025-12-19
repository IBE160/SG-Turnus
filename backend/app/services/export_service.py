# backend/app/services/export_service.py

from io import BytesIO, StringIO
import csv
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class ExportService:
    def export(self, content: str, format: str) -> BytesIO:
        if format == "pdf":
            return self._export_to_pdf(content)
        elif format == "docx":
            return self._export_to_docx(content)
        elif format == "csv":
            return self._export_to_csv(content)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_to_pdf(self, content: str) -> BytesIO:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, content)
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    def _export_to_docx(self, content: str) -> BytesIO:
        document = Document()
        document.add_paragraph(content)
        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer

    def _export_to_csv(self, content: str) -> BytesIO:
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["content"])
        writer.writerow([content])
        return BytesIO(buffer.getvalue().encode('utf-8'))

export_service = ExportService()
