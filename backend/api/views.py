import io
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .models import EquipmentDataset
from .serializers import EquipmentDatasetSerializer
from .services import get_summary_and_records, parse_csv, compute_summary


class UploadCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.lower().endswith('.csv'):
            return Response(
                {'error': 'Please upload a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            summary, records = get_summary_and_records(csv_file)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        name = request.data.get('name', csv_file.name)
        dataset = EquipmentDataset.objects.create(
            name=name,
            row_count=len(records),
            summary_json=summary
        )
        self._trim_history()
        return Response({
            'dataset_id': dataset.id,
            'summary': summary,
            'records': records,
        }, status=status.HTTP_201_CREATED)

    def _trim_history(self):
        max_n = getattr(settings, 'MAX_HISTORY_DATASETS', 5)
        for ds in EquipmentDataset.objects.all()[max_n:]:
            ds.delete()


class SummaryView(APIView):
    """Return summary for a given dataset id (from history)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, dataset_id):
        try:
            ds = EquipmentDataset.objects.get(pk=dataset_id)
            return Response({
                'id': ds.id,
                'name': ds.name,
                'uploaded_at': ds.uploaded_at.isoformat(),
                'row_count': ds.row_count,
                'summary': ds.summary_json,
            })
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)


class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datasets = EquipmentDataset.objects.all()[:5]
        serializer = EquipmentDatasetSerializer(datasets, many=True)
        return Response(serializer.data)


class ReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, dataset_id):
        try:
            ds = EquipmentDataset.objects.get(pk=dataset_id)
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=16)
        story = []
        story.append(Paragraph('Chemical Equipment Parameter Report', title_style))
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph(f'Dataset: {ds.name}', styles['Normal']))
        story.append(Paragraph(f'Generated: {ds.uploaded_at.strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
        story.append(Spacer(1, 0.25 * inch))
        summary = ds.summary_json
        story.append(Paragraph('Summary', styles['Heading2']))
        story.append(Paragraph(f'Total equipment count: {summary.get("total_count", 0)}', styles['Normal']))
        av = summary.get('averages', {})
        story.append(Paragraph(f'Averages - Flowrate: {av.get("Flowrate", "-")}, Pressure: {av.get("Pressure", "-")}, Temperature: {av.get("Temperature", "-")}', styles['Normal']))
        dist = summary.get('equipment_type_distribution', {})
        dist_text = ', '.join(f'{k}: {v}' for k, v in dist.items())
        story.append(Paragraph(f'Type distribution: {dist_text}', styles['Normal']))
        story.append(Spacer(1, 0.25 * inch))
        doc.build(story)
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{ds.id}.pdf"'
        return response
