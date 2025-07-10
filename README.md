
# 🎧 Client Call Audio Analyzer (AI-Powered)

A full-stack Flask web application that allows users to upload client call recordings and automatically generates an insightful, AI-powered report including **transcription**, **sentiment analysis**, **customer satisfaction**, and **conversation summaries** using advanced language models.

---

## 🔍 Overview

This project enables automatic evaluation of customer support calls through:

- 🎙️ Audio transcription
- 💬 Sentiment & emotion detection
- 📋 Detailed call analysis (reason, urgency, resolution)
- 📊 Summary generation
- 🎨 Interactive, styled UI with upload & playback

The system processes uploaded `.mp3` or `.wav` files and provides a structured report via a modern web interface.

---

## 🚀 Features

- 📤 Upload and play client call audio
- 🧠 AI-driven transcription and analysis
- 🎯 Breakdown of customer concerns, agent effectiveness, and sentiment journey
- ✨ Responsive UI with animated visuals and dynamic background transitions
- 🛡️ Secure API key management using `.env`
- 🎓 Built for research, learning, and client feedback automation use-cases

---

## 🧠 AI Capabilities

- **Automatic Transcription:** Converts audio into readable speaker-labeled dialogue
- **Sentiment Analysis:** Determines emotional tone and satisfaction
- **Structured Extraction:** Identifies urgency, main issue, resolution, and compensation
- **Natural Language Summary:** Generates a human-readable paragraph summarizing the conversation

---

## 🛠️ Tech Stack

| Layer           | Technology                           |
|----------------|---------------------------------------|
| 🧩 Backend       | Flask, Flask-SQLAlchemy, Python       |
| 🎨 Frontend      | HTML5, CSS3 (Responsive UI)           |
| 🧠 AI Logic      | Pretrained transformer-based models (via `requests`) |
| 🗃️ Database      | MySQL                                 |
| 🌐 APIs Used     | AssemblyAI (speech-to-text), DeepSeek (analysis) |
| ⚙️ Dev Tools     | Gunicorn, Python-Dotenv               |

---

## 📁 Project Structure

```

client\_sentiment/
│
├── app.py                       # Main Flask application
├── templates/
│   ├── index.html               # Upload page
│   └── view\_audio.html          # Results page
├── uploads/                     # Folder to store uploaded files
├── .env                         # API keys (not committed)
├── .env.example                 # Template for your API keys
├── requirements.txt             # Project dependencies
└── README.md                    # You're here!

````

---

## 🧪 Setup & Run Locally

### 1. Clone this repository

```bash
git clone https://github.com/your-username/client-call-analyzer.git
cd client-call-analyzer
````

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API keys

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
ASSEMBLYAI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
```

### 5. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser.

---

## 📸 Screenshots

### 🔹 Upload UI
![Upload UI](screenshots/dashboard.png)

### 🔹 Sentiment Analysis & Summary Display
![Analysis Display 1](screenshots/analysis%201.png)
![Analysis Display 2](screenshots/analysis%202.png)
![Analysis Display 3](screenshots/analysis%203.png)

---

## 🎥 Demo

[![Watch the Demo](https://img.youtube.com/vi/aWcNewcyWIo/0.jpg)](https://youtu.be/aWcNewcyWIo)

> ✨ Click the image to watch a short demo of the UI transition, audio upload flow, and sentiment analysis.

---


## 🧠 Author Learning & Contributions


* Built the full-stack architecture with Flask and MySQL
* Explored and implemented AI-driven analysis pipelines using external LLM APIs
* Designed a responsive frontend with clean UX and subtle animations
* Gained experience in text parsing, prompt engineering, and inference interpretation
* Learned secure API integration and deployment practices

---

## 🛡️ Security Notes

* API keys are **secured via `.env`**
* `.env` is included in `.gitignore` and **should never be committed**

---


## 🙌 Acknowledgements

* [AssemblyAI](https://www.assemblyai.com/) for speech-to-text APIs
* [DeepSeek](https://deepseek.com/) for natural language analysis APIs
* [Flask](https://flask.palletsprojects.com/)


