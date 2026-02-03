from django.contrib import admin
from .models import EquipmentDataset


@admin.register(EquipmentDataset)
class EquipmentDatasetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'uploaded_at', 'row_count']
