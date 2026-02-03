from django.db import models


class EquipmentDataset(models.Model):
    """Stores metadata for each uploaded CSV dataset (last 5 kept)."""
    name = models.CharField(max_length=255, default='Untitled')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    summary_json = models.JSONField(default=dict)

    class Meta:
        ordering = ['-uploaded_at']
