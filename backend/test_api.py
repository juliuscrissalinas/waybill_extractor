import os
import django
import json

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "waybill_project.settings")
django.setup()

from waybill.models import ExtractionModel
from waybill.serializers import ExtractionModelSerializer


def test_extraction_models():
    # Get all extraction models
    models = ExtractionModel.objects.all()
    print(f"Found {len(models)} extraction models:")

    # Serialize the models
    serializer = ExtractionModelSerializer(models, many=True)
    data = serializer.data

    # Print the serialized data
    print(json.dumps(data, indent=2))

    return data


if __name__ == "__main__":
    test_extraction_models()
