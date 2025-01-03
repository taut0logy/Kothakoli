# KUET Cosmic Cannonball

## 🚀 Overview
Welcome to the **KUET Cosmic Cannonball** project! This repository delivers an advanced, integrated application focused on Banglish to Bangla translation, real-time collaboration, chatbot interaction, and user analytics. Our goal is to simplify content management and language conversion with cutting-edge technology.

---

## 👥 Team Members
- [Add team member names here]

---

## 🔑 Features

### 1. **Banglish to Bangla Converter**
- Converts Banglish (Latin script) to Bangla (Bengali script) with precision.
- Uses machine learning models for enhanced translation accuracy.

### 2. **Content Management**
- Built-in text editor for writing and translating content.
- Export content as PDFs with options to set privacy as public or private.
- AI-generated titles and captions for exported PDFs.

### 3. **Search Functionality**
- App-wide search that supports queries in both Bangla and Banglish.
- Enables users to find user-uploaded PDFs and profiles efficiently.

### 4. **Chatbot Integration**
- Banglish chatbot capable of understanding and responding in Bangla.
- Integrates with exported PDFs to provide context-based responses.
- Includes a text-to-speech feature for hands-free interaction.

### 5. **Translation System Improvement**
- Supports user-generated training data with admin verification.
- Enhances translation models with continuous learning.

### 6. **User Interface (UI/UX)**
- Intuitive design providing access to all features with minimal effort.
- Responsive layouts optimized for various devices, including desktops, tablets, and mobiles.

### 7. **Backend**
- **Framework:** FastAPI for building high-performance APIs.
- **Database Integration:**
  - **Database:** MongoDB for scalable and flexible data storage.
  - **ORM:** Prisma for effective schema management and database querying.

### 8. **Frontend**
- **Framework:** Next.js for building interactive and modern web interfaces.
- Ensures high performance and server-side rendering for faster loading times.

### 9. **Voice Interaction**
- Voice-enabled editor for Bangla and English inputs, with automatic Bangla transcription.
- Chatbot supports voice responses, enhancing accessibility and user engagement.

### 10. **Smart Editor for Chatbot**
- Automatically detects and corrects common errors in Banglish inputs to ensure accurate chatbot responses.

### 11. **Real-Time Collaboration**
- Allows multiple users to edit content simultaneously.
- Ensures changes are synchronized in real time for seamless collaboration.

### 12. **Analytics Dashboard**
- Provides insights on user activities, such as:
  - Total word count translated.
  - Stories written.
  - Chatbot interactions.
- Encourages productivity by visualizing user engagement.

### 13. **Customizable Bangla Fonts for PDFs**
- Users can select from a variety of Bangla fonts to personalize the appearance of their PDFs.

### 14. **Dockerization**
- Application is containerized with Docker to ensure:
  - Consistency across development, testing, and production environments.
  - Simplified deployment and scaling.

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI for scalable and efficient API services.
- **Database:** MongoDB for robust data management.
- **ORM:** Prisma for smooth database operations.

### Frontend
- **Framework:** Next.js for building modern, responsive web interfaces.

### Additional Tools
- **Containerization:** Docker for deploying consistent environments.
- **Environment Management:** `.env` file for handling configuration settings securely.

---

## 🙏 Thank You
For inquiries, contributions, or suggestions, feel free to contact us or check our detailed documentation.

---

## 🚀 Instructions to Run

1. Clone the repository:
   ```bash
   git clone [repository-link]
   ```
2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```bash
   npm install
   ```
4. Start the application using Docker:
   ```bash
   docker-compose up
   ```
5. Access the application:
   - **Backend:** `http://localhost:8000`
   - **Frontend:** `http://localhost:3000`

---

## 📂 Virtual Environment Setup

To ensure a clean and isolated development environment, follow these steps to set up a virtual environment:

1. **Install `virtualenv`:**
   ```bash
   pip install virtualenv
   ```

2. **Create a virtual environment:**
   ```bash
   virtualenv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies inside the virtual environment:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Deactivate the virtual environment when done:**
   ```bash
   deactivate
   ```

---

## 📜 License
[Add license information here]
