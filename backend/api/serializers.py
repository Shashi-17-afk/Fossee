from rest_framework import serializers
from .models import EquipmentDataset


class EquipmentDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentDataset
        fields = ['id', 'name', 'uploaded_at', 'row_count', 'summary_json']
