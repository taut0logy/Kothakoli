# KothaKoli

## 🚀 Overview
Welcome to the **Kothakoli** project! This repository delivers an advanced, integrated application focused on Banglish to Bangla translation, real-time collaboration, chatbot interaction, and user analytics. Our goal is to simplify content management and language conversion with cutting-edge technology.

---
## Team Name : KUET_COSMIC_CANNONBALL



## 👥 Team Members
- Raufun Ahsan  
- Mohammad Abir Rahman  
- Md. Sakibur Rahman  

All team members are students from the Department of CSE, KUET.

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

## Project Flow Diagram 
`![Flow Diagram](_photos/flow.png)`

## Database ER Diagram 
`![ER Diagram](_photos/erdiagram.png)`



## 🔗 API Endpoints

## 1. **Chat Endpoints**
#### `/api/chat/text`
- **Description:** Process text input and return AI response.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "message": "string",
    "model_name": "string"
  }
  ```
- **Response:**
  ```json
  {
    "response": "string"
  }
  ```

#### `/api/chat/voice`
- **Description:** Process voice input and return AI response.
- **Method:** POST
- **Request Body:**
  - **audio:** Binary (multipart/form-data)
  - **model_name:** String (query)
- **Response:**
  ```json
  {
    "response": "string"
  }
  ```

#### `/api/chat/text-to-speech`
- **Description:** Convert text to speech.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "text": "string"
  }
  ```
- **Response:**
  - Audio binary data.

## 2. **File Endpoints**
#### `/api/files/upload`
- **Description:** Upload and process a file (image or text).
- **Method:** POST
- **Request Body:**
  - **file:** Binary (multipart/form-data)
- **Response:**
  ```json
  {
    "file_id": "string",
    "status": "uploaded"
  }
  ```

#### `/api/files/process-file`
- **Description:** Process an uploaded file.
- **Method:** POST
- **Request Body:**
  - **file:** Binary (multipart/form-data)
- **Response:**
  ```json
  {
    "result": "Processed successfully"
  }
  ```

## 3. **PDF Endpoints**
#### `/api/pdf/generate-story`
- **Description:** Generate a story PDF from a prompt.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "prompt": "string",
    "is_public": true
  }
  ```
- **Response:**
  ```json
  {
    "file_url": "string"
  }
  ```

#### `/api/pdf/download/{file_id}`
- **Description:** Download a generated PDF file.
- **Method:** GET
- **Parameters:**
  - **file_id:** String (path)
- **Response:**
  - Binary PDF file.

#### `/api/pdf/generate-custom`
- **Description:** Generate a custom PDF.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "custom_data": "string"
  }
  ```
- **Response:**
  ```json
  {
    "file_url": "string"
  }
  ```

## 4. **User Endpoints**
#### `/api/users/search`
- **Description:** Search users by name with pagination.
- **Method:** GET
- **Parameters:**
  - **query:** String (query)
  - **page:** Integer (default: 1)
  - **limit:** Integer (default: 10)
- **Response:**
  ```json
  [
    {
      "name": "string",
      "email": "string",
      "createdAt": "string"
    }
  ]
  ```

#### `/api/users/{user_id}/contents`
- **Description:** Get user-generated contents.
- **Method:** GET
- **Parameters:**
  - **user_id:** String (path)
- **Response:**
  ```json
  [
    {
      "title": "string",
      "content": "string",
      "fileUrl": "string"
    }
  ]
  ```

## 5. **Content Endpoints**

### 1. `/api/content/all`
- **Description:** Retrieve all content.
- **Method:** GET
- **Parameters:** None
- **Response:**
  ```json
  [
    {
      "id": "string",
      "type": "string",
      "content": "string"
    }
  ]
  ```

### 2. `/api/content/`
- **Description:** Get user's generated content with optional filtering.
- **Method:** GET
- **Parameters:**
  - **content_type:** String (query, optional; CHAT, PDF, VOICE, FILE)
  - **limit:** Integer (query, default: 50, maximum: 100, minimum: 1)
  - **offset:** Integer (query, default: 0, minimum: 0)
- **Response:**
  ```json
  [
    {
      "id": "string",
      "type": "string",
      "title": "string",
      "content": "string",
      "filename": "string",
      "fileUrl": "string",
      "metadata": {},
      "createdAt": "2025-01-04T01:30:52.692Z",
      "updatedAt": "2025-01-04T01:30:52.692Z"
    }
  ]
  ```

### 3. `/api/content/{user_id}`
- **Description:** Get user's generated content with optional filtering.
- **Method:** GET
- **Parameters:**
  - **user_id:** String (path, required)
  - **content_type:** String (query, optional; CHAT, PDF, VOICE, FILE)
  - **limit:** Integer (query, default: 50, maximum: 100, minimum: 1)
  - **offset:** Integer (query, default: 0, minimum: 0)
- **Response:**
  ```json
  [
    {
      "id": "string",
      "type": "string",
      "title": "string",
      "content": "string",
      "filename": "string",
      "fileUrl": "string",
      "metadata": {},
      "createdAt": "2025-01-04T01:30:52.694Z",
      "updatedAt": "2025-01-04T01:30:52.694Z"
    }
  ]
  ```

### 4. `/api/content/{user_id}/pdfs`
- **Description:** Get a user's PDF content with optional filtering.
- **Method:** GET
- **Parameters:**
  - **user_id:** String (path, required)
  - **limit:** Integer (query, default: 50, maximum: 100, minimum: 1)
  - **offset:** Integer (query, default: 0, minimum: 0)
- **Response:**
  ```json
  [
    {
      "id": "string",
      "type": "string",
      "title": "string",
      "content": "string",
      "filename": "string",
      "fileUrl": "string",
      "metadata": {},
      "createdAt": "2025-01-04T01:30:52.696Z",
      "updatedAt": "2025-01-04T01:30:52.696Z"
    }
  ]
  ```

### 5. `/api/content/get/{content_id}`
- **Description:** Get specific content by ID.
- **Method:** GET
- **Parameters:**
  - **content_id:** String (path, required)
- **Response:**
  ```json
  {
    "id": "string",
    "type": "string",
    "title": "string",
    "content": "string",
    "filename": "string",
    "fileUrl": "string",
    "metadata": {},
    "createdAt": "2025-01-04T01:30:52.698Z",
    "updatedAt": "2025-01-04T01:30:52.698Z"
  }
  ```

### 6. `/api/content/{content_id}`
- **Description:** Delete specific content.
- **Method:** DELETE
- **Parameters:**
  - **content_id:** String (path, required)
- **Response:**
  ```json
  {
    "id": "string",
    "type": "string",
    "title": "string",
    "content": "string",
    "filename": "string",
    "fileUrl": "string",
    "metadata": {},
    "createdAt": "2025-01-04T01:30:52.700Z",
    "updatedAt": "2025-01-04T01:30:52.700Z"
  }
  ```

### 7. `/api/content/{content_id}/toggle-public`
- **Description:** Toggle the public status of a content.
- **Method:** POST
- **Parameters:**
  - **content_id:** String (path, required)
- **Response:**
  ```json
  {
    "id": "string",
    "type": "string",
    "title": "string",
    "content": "string",
    "filename": "string",
    "fileUrl": "string",
    "metadata": {},
    "createdAt": "2025-01-04T01:30:52.700Z",
    "updatedAt": "2025-01-04T01:30:52.700Z"
  }
  ```

### 8. `/api/content/search`
- **Description:** Search for public PDFs.
- **Method:** GET
- **Parameters:**
  - **query:** String (query, required)
  - **page:** Integer (query, default: 1, minimum: 1)
  - **limit:** Integer (query, default: 10, maximum: 100, minimum: 1)
- **Response:**
  ```json
  {
    "items": [
      {
        "id": "string",
        "title": "string",
        "content": "string",
        "filename": "string",
        "fileUrl": "string",
        "metadata": {},
        "createdAt": "2025-01-04T01:30:52.700Z",
        "updatedAt": "2025-01-04T01:30:52.700Z"
      }
    ],
    "total": 0,
    "page": 0,
    "limit": 0,
    "total_pages": 0
  }
  ```
## 6. **Admin Endpoints**


### 1. `/api/admin/users`
- **Description:** Get all users with their content counts.
- **Method:** GET
- **Parameters:**
  - **page:** Integer (query, default: 1, minimum: 1)
  - **limit:** Integer (query, default: 10, maximum: 50, minimum: 1)
- **Response:**
  ```json
  [
    {
      "_id": "string",
      "name": "string",
      "email": "string",
      "contentCount": {
        "pdf": 10,
        "chat": 5
      }
    }
  ]
  ```

### 2. `/api/admin/contents`
- **Description:** Get all generated contents across all users.
- **Method:** GET
- **Parameters:**
  - **page:** Integer (query, default: 1, minimum: 1)
  - **limit:** Integer (query, default: 10, maximum: 50, minimum: 1)
- **Response:**
  ```json
  [
    {
      "id": "string",
      "type": "string",
      "content": "string",
      "user": {
        "_id": "string",
        "name": "string"
      }
    }
  ]
  ```

### 3. `/api/admin/create`
- **Description:** Create a new admin user with a generated password.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "name": "string",
    "email": "user@example.com"
  }
  ```
- **Response:**
  ```json
  {
    "id": "string",
    "name": "string",
    "email": "string",
    "password": "string"
  }
  ```

### 4. `/api/search/users`
- **Description:** Search for users by name or email. Available to both regular users and admins.
- **Method:** GET
- **Parameters:**
  - **query:** String (query, minimum length: 1, required)
  - **page:** Integer (query, default: 1, minimum: 1)
  - **limit:** Integer (query, default: 10, maximum: 100, minimum: 1)
- **Response:**
  ```json
  {
    "items": [
      {
        "_id": "string",
        "email": "string",
        "name": "string",
        "createdAt": "2025-01-04T01:30:52.709Z",
        "updatedAt": "2025-01-04T01:30:52.709Z",
        "role": "USER"
      }
    ],
    "total": 0,
    "page": 0,
    "limit": 0,
    "total_pages": 0
  }
  ```

### 5. `/api/search/pdfs`
- **Description:** Search for PDFs by title or content. Available to both regular users and admins.
- **Method:** GET
- **Parameters:**
  - **query:** String (query, minimum length: 1, required)
  - **page:** Integer (query, default: 1, minimum: 1)
  - **limit:** Integer (query, default: 10, maximum: 100, minimum: 1)
- **Response:**
  ```json
  {
    "items": [
      {
        "id": "string",
        "title": "string",
        "content": "string",
        "createdAt": "2025-01-04T01:30:52.711Z",
        "user": {
          "_id": "string",
          "name": "string"
        }
      }
    ],
    "total": 0,
    "page": 0,
    "limit": 0,
    "total_pages": 0
  }
  ```

---
## 7. **Search Endpoints**
### 1. `/api/search/users`
- **Description:** Search for users by name or email. Available to both regular users and admins.
- **Method:** GET
- **Parameters:**
  - **query:** String (query, minimum length: 1, required)
  - **page:** Integer (query, default: 1, minimum: 1)
  - **limit:** Integer (query, default: 10, maximum: 100, minimum: 1)
- **Response:**
  ```json
  {
    "items": [
      {
        "_id": "string",
        "email": "string",
        "name": "string",
        "createdAt": "2025-01-04T01:30:52.709Z",
        "updatedAt": "2025-01-04T01:30:52.709Z",
        "role": "USER"
      }
    ],
    "total": 0,
    "page": 0,
    "limit": 0,
    "total_pages": 0
  }
  ```

### 2. `/api/search/pdfs`
- **Description:** Search for PDFs by title or content. Available to both regular users and admins.
- **Method:** GET
- **Parameters:**
  - **query:** String (query, minimum length: 1, required)
  - **page:** Integer (query, default: 1, minimum: 1)
  - **limit:** Integer (query, default: 10, maximum: 100, minimum: 1)
- **Response:**
  ```json
  {
    "items": [
      {
        "id": "string",
        "title": "string",
        "content": "string",
        "createdAt": "2025-01-04T01:30:52.711Z",
        "user": {
          "_id": "string",
          "name": "string"
        }
      }
    ],
    "total": 0,
    "page": 0,
    "limit": 0,
    "total_pages": 0
  }
  ```

### 3. `/api/convert/`
- **Description:** Convert Banglish text to Bengali.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "text": "string"
  }
  ```
- **Response:**
  ```json
  {
    "bengali_text": "string"
  }
  ```

---

## 8. **Convert Endpoints**



### 1. `/api/convert/`
- **Description:** Convert Banglish text to Bengali.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "_id": "string",
    "type": "CHAT",
    "title": "string",
    "filename": "string",
    "prompt": "string",
    "content": "string",
    "fileUrl": "string",
    "metadata": {},
    "userId": "string",
    "user": {
      "_id": "string",
      "name": "string",
      "email": "string"
    },
    "createdAt": "2025-01-04T01:30:52.711Z",
    "updatedAt": "2025-01-04T01:30:52.711Z"
  }
  ```
- **Response:**
  ```json
  {
    "bengali_text": "string"
  }
  ```
- **Error Response:**
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### 2. `/api/convert/generate-title-caption`
- **Description:** Generate a creative title and caption in Bengali.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "text": "string"
  }
  ```
- **Response:**
  ```json
  {
    "title": "string",
    "caption": "string"
  }
  ```
- **Error Response:**
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### 3. `/api/chatbot/chat`
- **Description:** Process chatbot queries.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "message": "string",
    "model_name": "string"
  }
  ```
- **Response:**
  ```json
  "string"
  ```
- **Error Response:**
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### 4. `/api/chatbot/chat/history`
- **Description:** Retrieve chat history.
- **Method:** GET
- **Response:**
  ```json
  [
    {
      "conversation_id": "string",
      "messages": ["string"]
    }
  ]
  ```

### 5. `/api/chatbot/check-spelling`
- **Description:** Check spelling for text.
- **Method:** POST
- **Parameters:**
  - **message:** String (query, required)
- **Response:**
  ```json
  {
    "corrected_text": "string"
  }
  ```
- **Error Response:**
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### 6. `/api/chatbot/health`
- **Description:** Health check endpoint.
- **Method:** GET
- **Response:**
  ```json
  "Service is healthy."
  ```

### 7. `/api/chatbot/cached-conversations`
- **Description:** Retrieve all cached conversations.
- **Method:** GET
- **Response:**
  ```json
  [
    {
      "conversation_id": "string",
      "messages": ["string"]
    }
  ]
  ```

### 8. `/api/chatbot/cache-conversation`
- **Description:** Cache a specific conversation for training.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "conversation_id": "string",
    "messages": ["string"]
  }
  ```
- **Response:**
  ```json
  "Conversation cached successfully."
  ```

## 8. **Chatbot Endpoints**

### 1. `/api/chatbot/chat`
- **Description:** Process chatbot queries.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "message": "string",
    "model_name": "string"
  }
  ```
- **Response:**
  ```json
  "string"
  ```
- **Error Response:**
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### 2. `/api/chatbot/chat/history`
- **Description:** Retrieve chat history.
- **Method:** GET
- **Response:**
  ```json
  [
    {
      "conversation_id": "string",
      "messages": ["string"]
    }
  ]
  ```

### 3. `/api/chatbot/check-spelling`
- **Description:** Check spelling for a given text.
- **Method:** POST
- **Parameters:**
  - **message:** String (query, required)
- **Response:**
  ```json
  {
    "corrected_text": "string"
  }
  ```
- **Error Response:**
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```

### 4. `/api/chatbot/health`
- **Description:** Health check endpoint to verify the service status.
- **Method:** GET
- **Response:**
  ```json
  "Service is healthy."
  ```

### 5. `/api/chatbot/cached-conversations`
- **Description:** Retrieve all cached conversations.
- **Method:** GET
- **Response:**
  ```json
  [
    {
      "conversation_id": "string",
      "messages": ["string"]
    }
  ]
  ```

### 6. `/api/chatbot/cache-conversation`
- **Description:** Cache a specific conversation for training purposes.
- **Method:** POST
- **Request Body:**
  ```json
  {
    "conversation_id": "string",
    "messages": ["string"]
  }
  ```
- **Response:**
  ```json
  "Conversation cached successfully."

## 8. **Default Endpoints**
### 1. `/health`
- **Description:** Health check endpoint to verify the service status.
- **Method:** GET
- **Request Body:** None
- **Response:**
  ```json
  "Service is operational."
  ```
- **Example Value:**
  ```json
  {
    "conversation_id": "string"
  }
  ```
- **Error Response:**
  ```json
  {
    "detail": [
      {
        "loc": ["string", 0],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
  





---

## 🙏 Thank You
For inquiries, contributions, or suggestions, feel free to contact us or check our detailed documentation.


