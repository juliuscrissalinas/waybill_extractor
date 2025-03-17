from django.db import models
from django.utils import timezone


class ExtractionModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Extraction Model"
        verbose_name_plural = "Extraction Models"

    def __str__(self):
        return self.name


class WaybillImage(models.Model):
    image = models.ImageField(upload_to="waybills/")
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed = models.BooleanField(default=False)
    extraction_model = models.ForeignKey(
        ExtractionModel, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = "Waybill Image"
        verbose_name_plural = "Waybill Images"

    def __str__(self):
        return f"Waybill {self.id} - {self.uploaded_at}"


class ExtractedData(models.Model):
    waybill_image = models.OneToOneField(WaybillImage, on_delete=models.CASCADE)
    extracted_data = models.JSONField()
    extracted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Extracted Data"
        verbose_name_plural = "Extracted Data"

    def __str__(self):
        return f"Data for Waybill {self.waybill_image.id}"
