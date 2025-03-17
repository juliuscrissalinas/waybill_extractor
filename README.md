# Waybill Extractor

A modern web application for extracting data from waybill images using AI technologies like AWS Textract and Mistral AI.

## Features

- Upload multiple waybill images at once
- Extract data using AWS Textract or Mistral AI
- Download extracted data as Excel files
- Modern React frontend with Material UI
- Django REST API backend

## Project Structure

- `frontend/`: React application with Material UI
- `backend/`: Django REST API application

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:

   ```
   cd backend
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

4. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

5. Run migrations:

   ```
   python manage.py migrate
   ```

6. Start the Django server:
   ```
   python manage.py runserver 8002
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```
   cd frontend
   ```

2. Install dependencies:

   ```
   npm install
   ```

3. Start the development server:

   ```
   npm start
   ```

4. The application will be available at `http://localhost:3000`

## Environment Variables

For full functionality, set the following environment variables:

### AWS Textract

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### Mistral AI

- `MISTRAL_API_KEY`

## API Endpoints

- `GET /api/extraction-models/`: List available extraction models
- `POST /api/waybills/bulk_upload/`: Upload and process waybill images
- `GET /api/waybill-images/download_excel/`: Download extracted data as Excel

## License

MIT
