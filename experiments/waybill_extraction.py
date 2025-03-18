import boto3
import pandas as pd
import numpy as np
from pathlib import Path
import json
import os
from dotenv import load_dotenv
from PIL import Image

# Get the absolute path to the backend/.env file
current_dir = Path(__file__).resolve().parent
backend_env_path = current_dir.parent / "backend" / ".env"
print(f"Loading .env from: {backend_env_path}")
load_dotenv(backend_env_path)


def get_text_for_cell(cell, blocks):
    """Get text for a cell by finding overlapping word blocks"""
    if "Text" in cell:
        return cell["Text"]

    cell_box = cell["Geometry"]["BoundingBox"]
    cell_text = []

    # Calculate cell boundaries with a small margin
    margin = 0.005  # Add a small margin to account for slight misalignments
    cell_left = cell_box["Left"] - margin
    cell_right = cell_box["Left"] + cell_box["Width"] + margin
    cell_top = cell_box["Top"] - margin
    cell_bottom = cell_box["Top"] + cell_box["Height"] + margin

    for block in blocks:
        if block["BlockType"] == "WORD":
            word_box = block["Geometry"]["BoundingBox"]
            word_left = word_box["Left"]
            word_right = word_box["Left"] + word_box["Width"]
            word_top = word_box["Top"]
            word_bottom = word_box["Top"] + word_box["Height"]

            # Check if word significantly overlaps with cell
            horizontal_overlap = word_right > cell_left and word_left < cell_right
            vertical_overlap = word_bottom > cell_top and word_top < cell_bottom

            if horizontal_overlap and vertical_overlap:
                # Calculate overlap percentage
                overlap_width = min(word_right, cell_right) - max(word_left, cell_left)
                overlap_height = min(word_bottom, cell_bottom) - max(word_top, cell_top)
                word_area = word_box["Width"] * word_box["Height"]
                overlap_area = max(0, overlap_width) * max(0, overlap_height)

                # If word overlaps significantly with the cell (>30% of word area)
                if overlap_area > 0.3 * word_area:
                    cell_text.append(block["Text"])

    return " ".join(cell_text)


def get_table_cells(table_block, blocks):
    """Get all cells belonging to a specific table"""
    if "Relationships" not in table_block:
        return []

    cell_ids = []
    for relationship in table_block["Relationships"]:
        if relationship["Type"] == "CHILD":
            cell_ids.extend(relationship["Ids"])

    cells = []
    for block in blocks:
        if block["Id"] in cell_ids and block["BlockType"] == "CELL":
            # Get the text for this cell by looking at overlapping word blocks
            block["Text"] = get_text_for_cell(block, blocks)
            cells.append(block)

    return cells


def extract_table_data(table_block, blocks):
    """Extract table data and confidence scores from Textract blocks for a specific table"""
    cells = {}
    confidence_scores = {}

    # Get cells for this specific table
    table_cells = get_table_cells(table_block, blocks)

    # Process cells
    for cell in table_cells:
        row_idx = cell["RowIndex"]
        col_idx = cell["ColumnIndex"]

        # Store cell text with single quote prefix for non-empty text
        text = cell.get("Text", "").strip()
        if text:
            # Handle special characters and formatting
            text = text.replace('"', '""')  # Escape double quotes
            text = f"'{text}"

        # Store cell data
        cells[(row_idx, col_idx)] = text

        # Store confidence score
        confidence_scores[(row_idx, col_idx)] = cell.get("Confidence", 0)

    if not cells:
        return pd.DataFrame(), pd.DataFrame()

    # Find dimensions of the table
    max_row = max(pos[0] for pos in cells.keys())
    max_col = max(pos[1] for pos in cells.keys())

    # Create DataFrames for data and confidence scores
    data_df = pd.DataFrame(index=range(1, max_row + 1), columns=range(1, max_col + 1))
    confidence_df = pd.DataFrame(
        index=range(1, max_row + 1), columns=range(1, max_col + 1)
    )

    # Fill DataFrames
    for (row_idx, col_idx), text in cells.items():
        data_df.iloc[row_idx - 1, col_idx - 1] = text
        confidence_df.iloc[row_idx - 1, col_idx - 1] = confidence_scores.get(
            (row_idx, col_idx), 0
        )

    return data_df, confidence_df


def main():
    # Print AWS credentials for debugging
    print("AWS Credentials:")
    print("Access Key:", os.getenv("AWS_ACCESS_KEY_ID"))
    print(
        "Secret Key:", "*" * len(os.getenv("AWS_SECRET_ACCESS_KEY", ""))
    )  # Hide the actual key
    print("Region:", os.getenv("AWS_REGION"))

    # Initialize AWS Textract client
    textract = boto3.client(
        "textract",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )

    # Path to the waybill image
    image_path = current_dir.parent / "backend/media/waybills/Picture10.png"

    # Check if image exists
    if not image_path.exists():
        print(f"Error: Image not found at {image_path}")
        print("Current working directory:", os.getcwd())
        print("Available files in media/waybills:")
        waybills_dir = current_dir.parent / "backend/media/waybills"
        if waybills_dir.exists():
            for file in waybills_dir.glob("*"):
                print(f"  - {file.name}")
        else:
            print("  waybills directory not found")
        return

    # Display image dimensions and format
    with Image.open(image_path) as img:
        print(f"Image size: {img.size}")
        print(f"Image format: {img.format}")

    # Read the image file
    with open(image_path, "rb") as image:
        image_bytes = image.read()

    try:
        # Call Textract API
        print("\nCalling AWS Textract API...")
        response = textract.analyze_document(
            Document={"Bytes": image_bytes}, FeatureTypes=["TABLES"]
        )

        # Save the full Textract response to JSON for reference
        output_path = Path(current_dir) / "analyzeDocResponse.json"
        with open(output_path, "w") as f:
            json.dump(response, f, indent=2)
        print(f"\nSaved full Textract response to {output_path}")

        # Extract tables from the response
        blocks = response["Blocks"]
        table_blocks = [block for block in blocks if block["BlockType"] == "TABLE"]

        print(f"\nFound {len(table_blocks)} tables in the document")

        # Process each table
        for i, table_block in enumerate(table_blocks, 1):
            print(f"\nProcessing Table {i}:")

            # Extract table data and confidence scores
            data_df, confidence_df = extract_table_data(table_block, blocks)

            if data_df.empty:
                print(f"No data found in table {i}")
                continue

            print("\nExtracted table data:")
            print(data_df)
            print("\nConfidence scores:")
            print(confidence_df)

            # Format confidence scores as percentages with 8 decimal places
            confidence_df = confidence_df.applymap(
                lambda x: f"'{x:.8f}" if pd.notnull(x) else ""
            )

            # Save table data and confidence scores to CSV
            output_csv = current_dir / f"table-{i}.csv"

            # Create empty row and confidence header with correct number of columns
            empty_row = pd.DataFrame(columns=data_df.columns)
            confidence_header = pd.DataFrame(
                [
                    ["'Confidence Scores % (Table Cell)"]
                    + [""] * (len(data_df.columns) - 1)
                ],
                columns=data_df.columns,
            )

            # Combine data and confidence scores with a separator
            combined_df = pd.concat(
                [data_df, empty_row, confidence_header, confidence_df],
                ignore_index=True,
            )

            # Save with proper quoting and without index
            combined_df.to_csv(
                output_csv, index=False, quoting=1
            )  # quoting=1 means quote all non-numeric fields
            print(f"Saved table to {output_csv}")

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
