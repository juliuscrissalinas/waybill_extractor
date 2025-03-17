import boto3
import json
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import ExtractionModel, WaybillImage, ExtractedData
from .serializers import (
    ExtractionModelSerializer,
    WaybillImageSerializer,
    ExtractedDataSerializer,
)
from openpyxl import Workbook
from django.http import HttpResponse
from datetime import datetime
import os
import base64
from mistralai import Mistral


# Simple view to test API
@api_view(["GET"])
def test_api(request):
    models = ExtractionModel.objects.all()
    serializer = ExtractionModelSerializer(models, many=True)
    return Response(serializer.data)


class ExtractionModelViewSet(viewsets.ModelViewSet):
    queryset = ExtractionModel.objects.all()
    serializer_class = ExtractionModelSerializer


class WaybillImageViewSet(viewsets.ModelViewSet):
    queryset = WaybillImage.objects.all()
    serializer_class = WaybillImageSerializer

    def extract_with_textract(self, image_path):
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            # Return dummy data for demo purposes
            return {
                "sender": {
                    "name": "AWS Textract Demo Sender",
                    "address": "123 AWS Street, AWS City, 12345",
                    "phone": "123-456-7890",
                },
                "recipient": {
                    "name": "AWS Textract Demo Recipient",
                    "address": "456 AWS Avenue, AWS City, 67890",
                    "phone": "987-654-3210",
                },
                "shipment": {
                    "tracking_number": "AWS123456789",
                    "date": "2025-03-17",
                    "weight": "2.5 kg",
                    "service_type": "Express",
                },
                "note": "This is demo data since AWS API keys are not configured.",
            }

        textract = boto3.client(
            "textract",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        with open(image_path, "rb") as document:
            response = textract.analyze_document(
                Document={"Bytes": document.read()}, FeatureTypes=["TABLES", "FORMS"]
            )

        return response

    def extract_with_mistral(self, image_path):
        if not settings.MISTRAL_API_KEY:
            # Return dummy data for demo purposes
            return {
                "sender": {
                    "name": "Mistral Demo Sender",
                    "address": "123 Mistral Street, Mistral City, 12345",
                    "phone": "123-456-7890",
                },
                "recipient": {
                    "name": "Mistral Demo Recipient",
                    "address": "456 Mistral Avenue, Mistral City, 67890",
                    "phone": "987-654-3210",
                },
                "shipment": {
                    "tracking_number": "MISTRAL123456789",
                    "date": "2025-03-17",
                    "weight": "2.5 kg",
                    "service_type": "Express",
                },
                "note": "This is demo data since Mistral API key is not configured.",
            }

        try:
            # Initialize Mistral client
            client = Mistral(api_key=settings.MISTRAL_API_KEY)

            # Read the image file and encode it to base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")

            # Process the image using Mistral OCR with the correct format
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_data}",
                },
            )

            # Extract the text from the OCR response
            extracted_text = ""
            for page in ocr_response.pages:
                extracted_text += page.markdown + "\n"

            # Now use the extracted text to structure the data
            # For simplicity, we'll return a structured object with the extracted text
            # In a real application, you might want to further process this text
            structured_data = {
                "raw_text": extracted_text,
                "sender": {},
                "recipient": {},
                "shipment": {},
            }

            # Parse the extracted text to populate structured data
            # This is a simplified example - in a real application, you would use
            # more sophisticated parsing logic or another API call to structure the data
            lines = extracted_text.split("\n")
            for line in lines:
                line = line.strip()
                if "sender" in line.lower() or "from" in line.lower():
                    structured_data["sender"]["info"] = line
                elif "recipient" in line.lower() or "to" in line.lower():
                    structured_data["recipient"]["info"] = line
                elif "tracking" in line.lower() or "waybill" in line.lower():
                    structured_data["shipment"]["tracking_number"] = line
                elif "date" in line.lower():
                    structured_data["shipment"]["date"] = line
                elif "weight" in line.lower():
                    structured_data["shipment"]["weight"] = line

            return structured_data

        except Exception as e:
            print(f"Error in Mistral OCR extraction: {str(e)}")
            # Return dummy data if there's an error with the API
            return {
                "sender": {
                    "name": "Mistral Error Fallback",
                    "address": "Error occurred during extraction",
                    "phone": "N/A",
                },
                "recipient": {
                    "name": "Mistral Error Fallback",
                    "address": "Error occurred during extraction",
                    "phone": "N/A",
                },
                "shipment": {
                    "tracking_number": "ERROR123",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "weight": "N/A",
                    "service_type": "N/A",
                },
                "error": str(e),
                "note": "This is fallback data due to an error with the Mistral API.",
            }

    @action(detail=False, methods=["post"])
    def bulk_upload(self, request):
        images = request.FILES.getlist("images")
        extraction_model_id = request.data.get("extraction_model")

        if not images:
            return Response(
                {"error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            extraction_model = ExtractionModel.objects.get(id=extraction_model_id)
        except ExtractionModel.DoesNotExist:
            return Response(
                {"error": "Invalid extraction model"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for required API keys based on the selected model
        if (
            extraction_model.name.lower() == "aws textract"
            and not settings.AWS_ACCESS_KEY_ID
        ):
            return Response(
                {
                    "error": "AWS credentials are not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if extraction_model.name.lower() == "mistral" and not settings.MISTRAL_API_KEY:
            return Response(
                {
                    "error": "Mistral API key is not configured. Please set MISTRAL_API_KEY environment variable."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        uploaded_images = []
        uploaded_ids = []  # Track the IDs of uploaded waybills

        for image in images:
            try:
                # Create the waybill image record
                waybill_image = WaybillImage.objects.create(
                    image=image, extraction_model_id=extraction_model_id
                )

                # Process the image based on the selected model
                try:
                    if extraction_model.name.lower() == "aws textract":
                        extracted_data = self.extract_with_textract(
                            waybill_image.image.path
                        )
                    elif extraction_model.name.lower() == "mistral":
                        extracted_data = self.extract_with_mistral(
                            waybill_image.image.path
                        )
                    else:
                        # Default to Mistral if model not recognized
                        extracted_data = self.extract_with_mistral(
                            waybill_image.image.path
                        )

                    # For demo purposes, if API keys are not set, use dummy data
                    if (
                        extraction_model.name.lower() == "aws textract"
                        and not settings.AWS_ACCESS_KEY_ID
                    ) or (
                        extraction_model.name.lower() == "mistral"
                        and not settings.MISTRAL_API_KEY
                    ):
                        extracted_data = {
                            "sender": {
                                "name": "Demo Sender",
                                "address": "123 Demo Street, Demo City, 12345",
                                "phone": "123-456-7890",
                            },
                            "recipient": {
                                "name": "Demo Recipient",
                                "address": "456 Test Avenue, Test City, 67890",
                                "phone": "987-654-3210",
                            },
                            "shipment": {
                                "tracking_number": "DEMO123456789",
                                "date": "2025-03-17",
                                "weight": "2.5 kg",
                                "service_type": "Express",
                            },
                            "note": "This is demo data since API keys are not configured.",
                        }

                    ExtractedData.objects.create(
                        waybill_image=waybill_image, extracted_data=extracted_data
                    )
                    waybill_image.processed = True
                    waybill_image.save()

                    uploaded_images.append(WaybillImageSerializer(waybill_image).data)
                    uploaded_ids.append(waybill_image.id)  # Add the ID to our list

                except Exception as e:
                    # Log the specific error
                    print(f"Error processing image: {str(e)}")

                    # Delete the waybill image if processing failed
                    waybill_image.delete()

                    # Return a more specific error
                    return Response(
                        {"error": f"Error processing image: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            except Exception as e:
                # Log the specific error
                print(f"Error creating waybill image: {str(e)}")

                return Response(
                    {"error": f"Error creating waybill image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Return both the serialized data and the IDs for download
        return Response(
            {
                "waybills": uploaded_images,
                "ids": uploaded_ids,
                "download_url": f"/waybill-images/download_excel/?ids={','.join(map(str, uploaded_ids))}",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def download_excel(self, request):
        # Get the waybill IDs from the query parameters
        waybill_ids = request.query_params.get("ids", "")

        wb = Workbook()
        default_sheet = wb.active
        default_sheet.title = "Summary"

        # Add a header to the default sheet
        default_sheet["A1"] = "Waybill Extraction Summary"
        default_sheet["A2"] = "Generated on"
        default_sheet["B2"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get only the specified waybill images or all if none specified
        if waybill_ids:
            ids_list = [
                int(id.strip()) for id in waybill_ids.split(",") if id.strip().isdigit()
            ]
            waybills = WaybillImage.objects.filter(id__in=ids_list, processed=True)
        else:
            # Fallback to all processed waybills if no IDs provided
            waybills = WaybillImage.objects.filter(processed=True)

        if not waybills.exists():
            default_sheet["A4"] = "No processed waybills found"
        else:
            # Add a summary of processed waybills
            default_sheet["A4"] = "Processed Waybills"
            default_sheet["A5"] = "ID"
            default_sheet["B5"] = "Upload Date"
            default_sheet["C5"] = "Extraction Model"

            row = 6
            for idx, waybill in enumerate(waybills):
                default_sheet[f"A{row}"] = waybill.id
                default_sheet[f"B{row}"] = waybill.uploaded_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                default_sheet[f"C{row}"] = (
                    waybill.extraction_model.name if waybill.extraction_model else "N/A"
                )
                row += 1

            # Create a sheet for each waybill
            for waybill in waybills:
                # Create a new sheet for each waybill
                ws = wb.create_sheet(title=f"Waybill_{waybill.id}")

                try:
                    extracted_data = waybill.extracteddata.extracted_data

                    # Add headers
                    ws["A1"] = "Field"
                    ws["B1"] = "Value"

                    # Add extracted data
                    row = 2

                    # Handle different formats of extracted data
                    if isinstance(extracted_data, dict):
                        # Flatten nested dictionaries for Excel output
                        def flatten_dict(d, parent_key=""):
                            items = []
                            for k, v in d.items():
                                new_key = f"{parent_key}.{k}" if parent_key else k
                                if isinstance(v, dict):
                                    items.extend(flatten_dict(v, new_key).items())
                                elif isinstance(v, list):
                                    for i, item in enumerate(v):
                                        if isinstance(item, dict):
                                            items.extend(
                                                flatten_dict(
                                                    item, f"{new_key}[{i}]"
                                                ).items()
                                            )
                                        else:
                                            items.append((f"{new_key}[{i}]", str(item)))
                                else:
                                    items.append((new_key, str(v)))
                            return dict(items)

                        flattened_data = flatten_dict(extracted_data)
                        for key, value in flattened_data.items():
                            ws[f"A{row}"] = key
                            ws[f"B{row}"] = value
                            row += 1
                    else:
                        # If not a dict, just add as raw text
                        ws[f"A{row}"] = "Raw Data"
                        ws[f"B{row}"] = str(extracted_data)

                except ExtractedData.DoesNotExist:
                    ws["A1"] = "No extracted data available"

        # Create response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename=waybills_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

        wb.save(response)
        return response
