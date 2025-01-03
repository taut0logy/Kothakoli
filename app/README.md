# Kothakoli - AI-Powered Enhanced Chatbot Platform

An advanced chatbot platform that extends beyond traditional text-based interactions, featuring voice commands, image processing, and PDF generation capabilities.

## Features

- Text and Voice-based Chat Interface
- Bengali, English and Banglish Support
- File Upload Support (Images & Text)
- OCR for Image Text Extraction
- PDF Generation and Management
- Voice-to-Text and Text-to-Speech
- Google Gemini AI Integration
- PDF Sharing Platform
- User Management and Authentication
- Admin Dashboard
- Role-based Access Control

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React
- Database: SQLite
- AI: Google Gemini API
- Storage: Local File System
- OCR: EasyOCR
- PDF Generation: FPDF

## Required Software

- python, pip
- node, npm
- ffmpeg
- Tesseract OCR
- Poppler
- Google Gemini API

## Setup Instructions

1. Clone the repository
2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Add your Google Gemini API key, Database URL, secret key, and other necessary variables to .env
   ```

4. Generate a secret key for app encryption:

   ```bash
   python -c 'import secrets; print(secrets.token_urlsafe(32))'
   # Add the generated key to .env as ENCRYPTION_KEY

5. Generate prisma schema:

   ```bash
   prisma generate
   prisma db push
   ```

6. Run the backend:

   ```bash
   uvicorn app.main:app --reload
   ```

7. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   ```

8. Run the frontend:

   ```bash
   npm run dev
   ```

## Project Structure

```text
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── middleware/
│   ├── models/
│   └── services/
├── frontend/
│   ├── src/
│   └── public/
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── .env
├── storage/
├── requirements.txt
└── README.md
```