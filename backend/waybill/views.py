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

        # Initialize the structured response
        structured_data = {
            "tables": [],
            "forms": {},
            "raw_text": "",
            "confidence_scores": {},
        }

        # Helper function to get cell text by block ID
        def get_text_by_block_id(block_id, blocks_map):
            block = blocks_map.get(block_id, {})
            if block.get("BlockType") == "WORD":
                return block.get("Text", "")
            elif block.get("BlockType") in ["CELL", "LINE"]:
                words = []
                for relationship in block.get("Relationships", []):
                    if relationship["Type"] == "CHILD":
                        for child_id in relationship["Ids"]:
                            if blocks_map[child_id]["BlockType"] == "WORD":
                                words.append(blocks_map[child_id]["Text"])
                return " ".join(words)
            return ""

        # Create a map of block IDs to blocks
        blocks_map = {block["Id"]: block for block in response["Blocks"]}

        # Process tables
        for block in response["Blocks"]:
            if block["BlockType"] == "TABLE":
                table_data = {"rows": [], "confidence_scores": []}

                # Get all cells for this table
                cells = []
                for relationship in block.get("Relationships", []):
                    if relationship["Type"] == "CHILD":
                        for cell_id in relationship["Ids"]:
                            cell_block = blocks_map[cell_id]
                            if cell_block["BlockType"] == "CELL":
                                cells.append(cell_block)

                # Sort cells by row and column
                cells.sort(key=lambda c: (c["RowIndex"], c["ColumnIndex"]))

                # Group cells by row
                current_row = []
                current_row_index = 1
                confidence_row = []

                for cell in cells:
                    if cell["RowIndex"] > current_row_index:
                        if current_row:
                            table_data["rows"].append(current_row)
                            table_data["confidence_scores"].append(confidence_row)
                        current_row = []
                        confidence_row = []
                        current_row_index = cell["RowIndex"]

                    cell_text = get_text_by_block_id(cell["Id"], blocks_map)
                    current_row.append(cell_text)
                    confidence_row.append(cell.get("Confidence", 0))

                # Add the last row
                if current_row:
                    table_data["rows"].append(current_row)
                    table_data["confidence_scores"].append(confidence_row)

                structured_data["tables"].append(table_data)

            # Process form fields (key-value pairs)
            elif block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block["EntityTypes"]:
                    key = get_text_by_block_id(block["Id"], blocks_map)
                    value = ""
                    confidence = block.get("Confidence", 0)

                    # Find the corresponding value
                    for relationship in block.get("Relationships", []):
                        if relationship["Type"] == "VALUE":
                            for value_id in relationship["Ids"]:
                                value_block = blocks_map[value_id]
                                value = get_text_by_block_id(value_id, blocks_map)
                                confidence = value_block.get("Confidence", confidence)

                    if key and value:
                        structured_data["forms"][key] = {
                            "value": value,
                            "confidence": confidence,
                        }

            # Collect raw text
            elif block["BlockType"] == "LINE":
                structured_data["raw_text"] += (
                    get_text_by_block_id(block["Id"], blocks_map) + "\n"
                )

        return structured_data

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

            # Convert the OCR response to a dictionary
            response_dict = json.loads(ocr_response.model_dump_json())

            # Structure the data to include all OCR information
            structured_data = {
                "ocr_info": {
                    "model": response_dict.get("model", ""),
                    "usage_info": response_dict.get("usage_info", {}),
                },
                "pages": [],
            }

            # Process each page
            for page in response_dict.get("pages", []):
                page_data = {
                    "index": page.get("index", 0),
                    "dimensions": page.get("dimensions", {}),
                    "images": page.get("images", []),
                    "markdown": page.get("markdown", ""),
                }
                structured_data["pages"].append(page_data)

            # Add extracted text analysis
            extracted_text = ""
            for page in ocr_response.pages:
                extracted_text += page.markdown + "\n"

            structured_data["extracted_text"] = {
                "raw_text": extracted_text,
                "analysis": {
                    "sender": {},
                    "recipient": {},
                    "shipment": {},
                },
            }

            # Parse the extracted text to populate structured data
            lines = extracted_text.split("\n")
            for line in lines:
                line = line.strip()
                if "sender" in line.lower() or "from" in line.lower():
                    structured_data["extracted_text"]["analysis"]["sender"]["info"] = (
                        line
                    )
                elif "recipient" in line.lower() or "to" in line.lower():
                    structured_data["extracted_text"]["analysis"]["recipient"][
                        "info"
                    ] = line
                elif "tracking" in line.lower() or "waybill" in line.lower():
                    structured_data["extracted_text"]["analysis"]["shipment"][
                        "tracking_number"
                    ] = line
                elif "date" in line.lower():
                    structured_data["extracted_text"]["analysis"]["shipment"][
                        "date"
                    ] = line
                elif "weight" in line.lower():
                    structured_data["extracted_text"]["analysis"]["shipment"][
                        "weight"
                    ] = line

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

        # Ensure media directory exists
        media_root = os.path.join(settings.BASE_DIR, "media")
        os.makedirs(media_root, exist_ok=True)

        uploaded_images = []
        uploaded_ids = []  # Track the IDs of uploaded waybills

        for image in images:
            try:
                # Create the waybill image record
                waybill_image = WaybillImage.objects.create(
                    image=image, extraction_model_id=extraction_model_id
                )

                # Store the ID for the download URL
                uploaded_ids.append(waybill_image.id)

                # Process the image based on the selected model
                try:
                    print(f"Processing image with {extraction_model.name} model...")
                    if extraction_model.name.lower() == "aws textract":
                        extracted_data = self.extract_with_textract(
                            waybill_image.image.path
                        )
                    elif extraction_model.name.lower() == "mistral":
                        print("Calling Mistral API for extraction...")
                        extracted_data = self.extract_with_mistral(
                            waybill_image.image.path
                        )
                        print("Mistral API extraction completed")
                    else:
                        # Default to Mistral if model not recognized
                        print("Using default Mistral model for extraction...")
                        extracted_data = self.extract_with_mistral(
                            waybill_image.image.path
                        )

                    # Create ExtractedData record
                    ExtractedData.objects.create(
                        waybill_image=waybill_image,
                        extracted_data=extracted_data,
                    )

                    # Mark the waybill as processed
                    waybill_image.processed = True
                    waybill_image.save()

                    uploaded_images.append(waybill_image)

                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    # Delete the waybill image if processing failed
                    waybill_image.delete()
                    return Response(
                        {"error": f"Error processing image: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            except Exception as e:
                print(f"Error uploading image: {str(e)}")
                return Response(
                    {"error": f"Error uploading image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        if uploaded_images:
            # Construct the download URL with the correct endpoint
            download_url = (
                f"waybills/download_excel/?ids={','.join(map(str, uploaded_ids))}"
            )

            return Response(
                {
                    "message": f"Successfully uploaded {len(uploaded_images)} images",
                    "ids": uploaded_ids,
                    "download_url": download_url,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": "Failed to upload any images"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def download_excel(self, request):
        # Get the waybill IDs from the query parameters
        waybill_ids = request.query_params.get("ids", "")
        print(f"Downloading Excel for waybill IDs: {waybill_ids}")

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
            waybills = WaybillImage.objects.filter(id__in=ids_list)
            print(f"Found {waybills.count()} waybills")
        else:
            # Fallback to all waybills if no IDs provided
            waybills = WaybillImage.objects.all()
            print(f"No IDs provided, using all waybills: {waybills.count()}")

        if not waybills.exists():
            print("No waybills found")
            default_sheet["A4"] = "No waybills found"
        else:
            # Add a summary of waybills
            default_sheet["A4"] = "Waybills"
            default_sheet["A5"] = "ID"
            default_sheet["B5"] = "Upload Date"
            default_sheet["C5"] = "Extraction Model"
            default_sheet["D5"] = "Processed"

            row = 6
            for idx, waybill in enumerate(waybills):
                default_sheet[f"A{row}"] = waybill.id
                default_sheet[f"B{row}"] = waybill.uploaded_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                default_sheet[f"C{row}"] = (
                    waybill.extraction_model.name if waybill.extraction_model else "N/A"
                )
                default_sheet[f"D{row}"] = "Yes" if waybill.processed else "No"
                row += 1

            # Create a sheet for each waybill
            for waybill in waybills:
                print(f"Processing waybill {waybill.id} for Excel export")
                # Create a new sheet for each waybill
                ws = wb.create_sheet(title=f"Waybill_{waybill.id}")

                try:
                    extracted_data = waybill.extracteddata.extracted_data
                    print(f"Found extracted data for waybill {waybill.id}")

                    # Add headers
                    ws["A1"] = "Field"
                    ws["B1"] = "Value"

                    # Add extracted data
                    row = 2

                    # Handle different formats of extracted data
                    if isinstance(extracted_data, dict):
                        # Special handling for AWS Textract data
                        if "tables" in extracted_data:
                            # Create a new sheet for each table
                            for table_idx, table in enumerate(extracted_data["tables"]):
                                table_sheet = wb.create_sheet(
                                    title=f"Waybill_{waybill.id}_Table_{table_idx + 1}"
                                )

                                # Add table data
                                for row_idx, (row_data, confidence_scores) in enumerate(
                                    zip(table["rows"], table["confidence_scores"])
                                ):
                                    # Write data
                                    for col_idx, cell_value in enumerate(row_data):
                                        cell = table_sheet.cell(
                                            row=row_idx + 1, column=col_idx + 1
                                        )
                                        cell.value = cell_value

                                # Add confidence scores in the next rows
                                confidence_row = row_idx + 3  # Leave a blank row
                                table_sheet.cell(
                                    row=confidence_row,
                                    column=1,
                                    value="Confidence Scores (%)",
                                )
                                for col_idx, scores in enumerate(
                                    zip(*table["confidence_scores"])
                                ):
                                    for score_idx, score in enumerate(scores):
                                        cell = table_sheet.cell(
                                            row=confidence_row + score_idx + 1,
                                            column=col_idx + 1,
                                        )
                                        cell.value = f"{score:.2f}%"

                            # Add form fields to the main sheet
                            ws["A2"] = "Form Fields"
                            ws["A3"] = "Field"
                            ws["B3"] = "Value"
                            ws["C3"] = "Confidence"

                            form_row = 4
                            for key, data in extracted_data.get("forms", {}).items():
                                ws[f"A{form_row}"] = key
                                ws[f"B{form_row}"] = data["value"]
                                ws[f"C{form_row}"] = f"{data['confidence']:.2f}%"
                                form_row += 1

                            # Add raw text
                            ws[f"A{form_row + 2}"] = "Raw Text"
                            ws[f"A{form_row + 3}"] = extracted_data.get("raw_text", "")

                        else:
                            # Handle regular dictionary data
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
                                                items.append(
                                                    (f"{new_key}[{i}]", str(item))
                                                )
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
                    print(f"No extracted data found for waybill {waybill.id}")
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
