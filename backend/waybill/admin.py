from django.contrib import admin
from .models import ExtractionModel, WaybillImage, ExtractedData


@admin.register(ExtractionModel)
class ExtractionModelAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active")
    search_fields = ("name", "description")
    list_filter = ("is_active",)


@admin.register(WaybillImage)
class WaybillImageAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_at", "processed", "extraction_model")
    list_filter = ("processed", "extraction_model")
    date_hierarchy = "uploaded_at"


@admin.register(ExtractedData)
class ExtractedDataAdmin(admin.ModelAdmin):
    list_display = ("id", "waybill_image", "extracted_at")
    date_hierarchy = "extracted_at"
