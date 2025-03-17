import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "waybill_project.settings")
django.setup()

from waybill.models import ExtractionModel

# Create Mistral extraction model
mistral_model = ExtractionModel.objects.create(
    name="Mistral",
    description="Mistral AI OCR model for waybill extraction",
    is_active=True,
)

print(f"Created extraction model: {mistral_model.name}")

# Create AWS Textract extraction model
textract_model = ExtractionModel.objects.create(
    name="AWS Textract",
    description="AWS Textract OCR model for waybill extraction",
    is_active=True,
)

print(f"Created extraction model: {textract_model.name}")
