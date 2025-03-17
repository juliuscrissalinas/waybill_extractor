import os
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "waybill_project.settings")
django.setup()

from waybill.models import ExtractionModel


def create_extraction_models():
    # Create Mistral model
    mistral_model, created = ExtractionModel.objects.get_or_create(
        name="Mistral",
        defaults={
            "description": "Extract data from waybills using Mistral AI's vision capabilities",
            "is_active": True,
        },
    )

    if created:
        print(f"Created Mistral extraction model: {mistral_model}")
    else:
        print(f"Mistral extraction model already exists: {mistral_model}")

    # Create AWS Textract model
    textract_model, created = ExtractionModel.objects.get_or_create(
        name="AWS Textract",
        defaults={
            "description": "Extract data from waybills using AWS Textract",
            "is_active": True,
        },
    )

    if created:
        print(f"Created AWS Textract extraction model: {textract_model}")
    else:
        print(f"AWS Textract extraction model already exists: {textract_model}")


if __name__ == "__main__":
    create_extraction_models()
