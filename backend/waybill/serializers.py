from rest_framework import serializers
from .models import ExtractionModel, WaybillImage, ExtractedData


class ExtractionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractionModel
        fields = ["id", "name", "description", "is_active"]


class WaybillImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaybillImage
        fields = ["id", "image", "uploaded_at", "processed", "extraction_model"]


class ExtractedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedData
        fields = ["id", "waybill_image", "extracted_data", "extracted_at"]
