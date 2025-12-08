# 🚀 AI Multi-Language Code Converter

A modern, real-time web application that automatically converts code from one programming language to another using AI (Groq Llama 3.3, OpenAI GPT-4o, or Hugging Face).

**🌐 Live Demo:** https://ai-multi-language-code-converter.vercel.app/

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.4+-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange.svg)

## ✨ Features

- **🔄 Multi-Language Support**: Convert between 13 programming languages
- **📁 File Upload**: Drag-and-drop or click to upload code files
- **🎨 Premium UI**: Modern dark theme with glassmorphism and animated space background
- **⚡ Real-Time Streaming**: Live code translation powered by Groq (Llama 3.3), Hugging Face, or OpenAI
- **💡 Code Explanation**: AI-powered explanations of your code
- **📊 Split View**: Side-by-side code comparison
- **📋 Copy to Clipboard**: One-click copy for source and converted code
- **📜 Conversion History**: LocalStorage-based history of recent conversions
- **📝 Code Templates**: Pre-loaded examples for all languages
- **📊 Code Statistics**: Real-time lines, characters, and word count
- **⌨️ Keyboard Shortcuts**: Power user shortcuts (Ctrl+Enter, Ctrl+E, Ctrl+D)
- **📥 Download Results**: Save converted code as files
- **🎯 Auto-Detection**: Automatically detects source language from file extension

## 🏗️ Architecture

```
┌───────────────────┐
│   Frontend        │
│ Vue.js + Vite     │
│ TypeScript        │
└─────────┬─────────┘
          │ HTTP
          ▼
┌───────────────────┐
│   Backend         │
│ FastAPI (Python)  │
└─────────┬─────────┘
          │ API Call
          ▼
┌───────────────────────────────┐
│          AI Engine            │
│ Groq / Hugging Face / OpenAI  │
└───────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and npm
- **API Key** (Choose one):
  - **Groq API Key** (Recommended - Free) - [Get here](https://console.groq.com/keys)
  - **OpenAI API Key** - [Get here](https://platform.openai.com/api-keys)
  - **Hugging Face API Key** - [Get here](https://huggingface.co/settings/tokens)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```env
# Choose your AI provider: groq, openai, or huggingface
AI_PROVIDER=groq

# Groq Configuration (Recommended - Fast & Free)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# OpenAI Configuration (Alternative)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Hugging Face Configuration (Alternative)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Server Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

6. Run the backend server:
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📖 Usage

1. **Open the application** in your browser at `http://localhost:5173`

2. **Upload a code file** or paste code directly into the source editor

3. **Select source and target languages** from the dropdowns

4. **Click "Convert Code"** to transform your code

5. **Download the result** using the download button

### Supported Conversions

| From       | To                                                                 |
|------------|--------------------------------------------------------------------|
| Python     | Node.js, JS, TS, Java, PHP, Go, C, C++, C#, Rust, SQL, Prisma      |
| Node.js    | Python, JS, TS, Java, PHP, Go, C, C++, C#, Rust, SQL, Prisma       |
| JavaScript | Python, Node.js, TS, Java, PHP, Go, C, C++, C#, Rust, SQL, Prisma  |
| TypeScript | Python, Node.js, JS, Java, PHP, Go, C, C++, C#, Rust, SQL, Prisma  |
| Java       | Python, Node.js, JS, TS, PHP, Go, C, C++, C#, Rust, SQL, Prisma    |
| PHP        | Python, Node.js, JS, TS, Java, Go, C, C++, C#, Rust, SQL, Prisma   |
| Go         | Python, Node.js, JS, TS, Java, PHP, C, C++, C#, Rust, SQL, Prisma  |
| C/C++      | Python, Node.js, JS, TS, Java, PHP, Go, C#, Rust, SQL, Prisma      |
| C#         | Python, Node.js, JS, TS, Java, PHP, Go, C, C++, Rust, SQL, Prisma  |
| Rust       | Python, Node.js, JS, TS, Java, PHP, Go, C, C++, C#, SQL, Prisma    |
| SQL        | Python, Node.js, JS, TS, Java, PHP, Go, C, C++, C#, Rust, Prisma   |
| Prisma     | Python, Node.js, JS, TS, Java, PHP, Go, C, C++, C#, Rust, SQL      |

## 🔌 API Documentation

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "online",
  "service": "AI Multi-Language Code Converter",
  "version": "1.0.0"
}
```

#### `GET /health`
Detailed health check.

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true,
  "model": "gpt-4o-mini"
}
```

#### `POST /convert`
Convert code from one language to another.

**Request Body:**
```json
{
  "source_language": "python",
  "target_language": "nodejs",
  "code": "def hello():\n    print('Hello, World!')"
}
```

**Response:**
```json
{
  "converted_code": "function hello() {\n    console.log('Hello, World!');\n}",
  "source_language": "python",
  "target_language": "nodejs",
  "success": true
}
```

#### `POST /convert-file`
Convert code from an uploaded file.

**Form Data:**
- `file`: Code file (multipart/form-data)
- `source_language`: Source language (string)
- `target_language`: Target language (string)

**Response:** Same as `/convert`

### Interactive API Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## 🛠️ Tech Stack

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vite** - Next-generation frontend tooling
- **TypeScript** - Type-safe JavaScript
- **Axios** - HTTP client
- **Custom CSS** - Premium dark theme with glassmorphism

### Backend
- **FastAPI** - Modern Python web framework
- **Groq API** - Llama 3.3 for fast code conversion
- **OpenAI API** - GPT-4o alternative
- **Hugging Face** - Open-source models alternative
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## 📁 Project Structure

```
AI-Multi-Language-Code-Converter/
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # Vue components
│   │   ├── types/         # TypeScript types
│   │   ├── App.vue        # Main component
│   │   ├── main.ts        # Entry point
│   │   └── style.css      # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/
│   ├── app/
│   │   ├── config.py      # Configuration
│   │   ├── models.py      # Pydantic models
│   │   └── converter.py   # Conversion logic
│   ├── main.py            # FastAPI app
│   └── requirements.txt
│
└── README.md
```

## 🚀 Deployment

### Backend Deployment (Fly.io)

**Quick Deploy:**
```bash
cd backend

# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch --no-deploy

# Set secrets
flyctl secrets set AI_PROVIDER=groq
flyctl secrets set GROQ_API_KEY=your_groq_api_key
flyctl secrets set CORS_ORIGINS="http://localhost:5173,https://your-app.vercel.app"

# Deploy
flyctl deploy
```

**Or use the automated script:**
```bash
cd backend
./deploy.sh
```

The backend will be available at `https://ai-code-converter-manzi.fly.dev/`



### Frontend Deployment (Vercel)

**Quick Deploy:**
```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable
vercel env add VITE_API_URL production
# Enter: https://your-app-name.fly.dev

# Deploy to production
vercel --prod
```

The frontend will be available at `https://your-project.vercel.app`

See [frontend/DEPLOYMENT.md](frontend/DEPLOYMENT.md) for detailed instructions.

## 💡 Features Implemented

- ✅ **Streaming Conversion**: Real-time output as code is generated
- ✅ **File Upload**: Drag-and-drop support with auto-detection
- ✅ **13 Languages**: Python, JS, TS, Node.js, Java, PHP, Go, C, C++, C#, Rust, SQL, Prisma
- ✅ **Multiple AI Providers**: Groq, OpenAI, Hugging Face
- ✅ **Code Explanation**: AI-powered code explanations
- ✅ **Split View**: Side-by-side code comparison
- ✅ **Copy to Clipboard**: One-click copy functionality
- ✅ **Conversion History**: LocalStorage-based history (last 10)
- ✅ **Code Templates**: Pre-loaded examples for all languages
- ✅ **Code Statistics**: Real-time line/character/word count
- ✅ **Keyboard Shortcuts**: Power user productivity features
- ✅ **Setup Guide**: Configuration and dependency guide for each language
- ✅ **Production Ready**: Deployed on Fly.io + Vercel

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📦 Repository

**GitHub:** https://github.com/manziosee/AI-Multi-Language-Code-Converter

```bash
# Clone the repository
git clone https://github.com/manziosee/AI-Multi-Language-Code-Converter.git
cd AI-Multi-Language-Code-Converter
```

For issues or questions:
- Open an issue on [GitHub](https://github.com/manziosee/AI-Multi-Language-Code-Converter/issues)
- Email: manziosee3@gmail.com

## 👨💻 Author

**Manzi Niyongira Osee**
- GitHub: [@manziosee](https://github.com/manziosee)
- Email: manziosee3@gmail.com

## 🆕 New Features

### 💡 Code Explanation
- Click "Explain Code" to understand what your code does
- Detailed breakdown of logic, functions, and patterns
- Works with all 13 supported languages

### 📊 Split View
- Toggle between single and split view modes
- Perfect for reviewing conversions
- Responsive design for all screen sizes

### 📋 Copy to Clipboard
- One-click copy for both source and converted code
- Visual feedback on successful copy
- Works across all modern browsers

### 📜 Conversion History
- Automatic saving of recent conversions (last 10)
- Quick access to previous work
- LocalStorage-based (no backend required)
- One-click restore from history

### 📝 Code Templates
- Pre-loaded examples for all 13 languages
- Quick start for testing and learning
- Fibonacci example demonstrates language syntax

### 📊 Code Statistics
- Real-time line count
- Character count
- Non-empty line count
- Displayed for both source and converted code

### ⌨️ Keyboard Shortcuts
- **Ctrl+Enter** (or Cmd+Enter): Convert code
- **Ctrl+E** (or Cmd+E): Explain code
- **Ctrl+D** (or Cmd+D): Download converted code
- Power user productivity features

### ⚙️ Setup Guide
- Click "Setup" button to view configuration guide for target language
- Shows required dependencies and installation commands
- Provides configuration files (package.json, tsconfig.json, etc.)
- Includes quick tips and best practices
- One-click copy for all commands and config files
- Covers all 13 supported languages

## 📊 Performance

- **Response Time**: < 5 seconds for most conversions
- **Uptime**: 99.9% (Fly.io auto-scaling)
- **Concurrent Users**: Supports multiple simultaneous conversions

---

**Built with ❤️ using Vue.js, FastAPI, Groq, and deployed on Fly.io + Vercel**
