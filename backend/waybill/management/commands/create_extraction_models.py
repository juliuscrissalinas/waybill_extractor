from django.core.management.base import BaseCommand
from waybill.models import ExtractionModel


class Command(BaseCommand):
    help = "Creates initial extraction models"

    def handle(self, *args, **kwargs):
        # Create Mistral model
        mistral_model, created = ExtractionModel.objects.get_or_create(
            name="Mistral",
            defaults={
                "description": "Extract data from waybills using Mistral AI's vision capabilities",
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created Mistral extraction model: {mistral_model}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Mistral extraction model already exists: {mistral_model}"
                )
            )

        # Create AWS Textract model
        textract_model, created = ExtractionModel.objects.get_or_create(
            name="AWS Textract",
            defaults={
                "description": "Extract data from waybills using AWS Textract",
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created AWS Textract extraction model: {textract_model}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"AWS Textract extraction model already exists: {textract_model}"
                )
            )
