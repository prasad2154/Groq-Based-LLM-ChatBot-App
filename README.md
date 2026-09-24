# 🚀 Groq-Powered LLM ChatBot Web Application

A modern Python Flask-based web application that provides an interactive chat interface powered by Groq's Language Model APIs, utilizing LlamaIndex for streamlined LLM interaction. Features real-time streaming responses, session-based chat history management, and configurable model parameters.

## 📋 Badges

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![LLM Provider](https://img.shields.io/badge/LLM-Groq-green.svg)](https://groq.com/)
[![LlamaIndex](https://img.shields.io/badge/Integration-LlamaIndex-purple.svg)](https://www.llamaindex.ai/)

## ✨ Features

- **🔄 Real-time Streaming Chat**: Responses from the LLM are streamed to the client for a more interactive experience
- **⚡ Groq LLM Integration**: Leverages Groq's fast inference capabilities via the `llama-index-llms-groq` library
- **💾 Session-based Chat History**: Maintains conversation history for each user session on the backend
- **🎯 Configurable System Prompts**: Allows setting or changing system prompts during a session
- **⚙️ Adjustable Parameters**: Supports setting temperature and model ID for LLM requests
- **🌐 CORS Enabled**: Allows cross-origin requests, making it easier to integrate with separate frontend applications
- **📡 RESTful API**: Provides clear endpoints for creating sessions, chatting, and clearing history
- **🔐 Environment Variable Configuration**: Securely manages API keys using `.env` files

## 📁 Project Structure

```
.
├── static/              # Static assets (CSS, JS, images) for the frontend
├── .env.example         # Example environment variables file
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── LICENSE             # Project's MIT License
├── app.py              # Main Flask application logic
├── index.html          # Basic HTML frontend for interacting with the chatbot
├── requirements.txt    # Python package dependencies
└── README.md           # This file
```

## 🔧 Prerequisites

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **pip** - Python package installer
- **Groq API Key** - Sign up at [console.groq.com](https://console.groq.com/)

## 🚀 Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SakibAhmedShuva/Groq-Based-LLM-ChatBot-App.git
cd Groq-Based-LLM-ChatBot-App
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file and add your Groq API key:

```env
GROQ_API_KEY="your_groq_api_key_here"

# Optional: Set Flask environment (defaults to 'production' if not set)
# FLASK_ENV="development"
```

> **Note**: Replace `"your_groq_api_key_here"` with your actual Groq API key.

## 🎯 Running the Application

Start the Flask application:

```bash
python app.py
```

The application will start on **http://localhost:5000**. Open this URL in your web browser to interact with the chatbot.

## 📚 API Endpoints

### `GET /`
**Description**: Serves the index.html frontend.

---

### `POST /create-session`
**Description**: Creates a new unique session ID and initializes its history on the backend.

**Request Body**: None

**Response**:
```json
{
    "status": "success",
    "session_id": "unique_session_identifier"
}
```

---

### `POST /chat`
**Description**: Sends a user prompt to the LLM for the given session and streams back the response.

**Request Body**:
```json
{
    "session_id": "your_session_id",
    "prompt": "Your message to the chatbot.",
    "system_prompt": "Optional: A system prompt to guide the LLM.",
    "temperature": 0.7,
    "model_id": "llama3-8b-8192"
}
```

**Response**: A `text/event-stream` with JSON objects:
- **Intermediate chunks**: `{"text_chunk": "...", "is_final": false}`
- **Final message**: `{"full_response": "...", "is_final": true}`
- **Error**: `{"error": "...", "is_final": true}`

---

### `POST /clear-backend-history`
**Description**: Clears the chat history for a given session ID on the backend.

**Request Body**:
```json
{
    "session_id": "your_session_id"
}
```

**Response**:
```json
{
    "status": "success",
    "message": "Backend chat history cleared for this session."
}
```

## 📦 Dependencies

The `requirements.txt` file includes the following packages:

```txt
Flask
flask-cors
python-dotenv
llama-index-llms-groq
llama-index-core
```

To generate an accurate requirements file after installing packages:

```bash
pip freeze > requirements.txt
```

## 🎨 Frontend Components

### `index.html`
Provides a basic user interface that handles:
- Creating new sessions
- Sending user prompts and displaying streamed responses
- Setting system prompts, temperature, and model parameters
- Clearing chat history

### `static/` Directory
Contains CSS, JavaScript, and image files used by the frontend.

## 📝 .gitignore

The project includes a `.gitignore` file with:

```gitignore
# Virtual Environment
venv/
*.pyc
__pycache__/

# Environment files
.env

# IDE and OS files
.idea/
.vscode/
*.DS_Store
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the Project
2. **Create** your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your Changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the Branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [**Groq**](https://groq.com/) for providing fast LLM inference
- [**LlamaIndex**](https://www.llamaindex.ai/) for the convenient Python library to interact with LLMs
- [**Flask**](https://flask.palletsprojects.com/) for the web framework

---

## 🔧 Final Setup Steps

To make this fully functional, ensure you have:

1. **Created `requirements.txt`**:
   ```bash
   pip install Flask flask-cors python-dotenv llama-index-llms-groq llama-index-core
   pip freeze > requirements.txt
   ```

2. **Created `.env.example`**:
   ```env
   GROQ_API_KEY="your_groq_api_key_here"
   # FLASK_ENV="development"
   ```

3. **Added a `LICENSE` file** with MIT License text

4. **Populated `static/` directory** and refined `index.html` with proper JavaScript to handle API calls

---

<div align="center">

**⭐ If you found this project helpful, please give it a star! ⭐**

</div>
