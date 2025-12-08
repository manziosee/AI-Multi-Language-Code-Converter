# 🚀 AI Multi-Language Code Converter

A modern, real-time web application that automatically converts code from one programming language to another using AI (OpenAI GPT-4o).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.4+-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3+-blue.svg)

## ✨ Features

- **🔄 Multi-Language Support**: Convert between Python, Node.js, JavaScript, TypeScript, Java, PHP, Go, C, C++, C#, Rust, SQL, and Prisma Schema
- **📁 File Upload**: Drag-and-drop or click to upload code files
- **🎨 Premium UI**: Modern dark theme with glassmorphism, animated space background, and smooth animations
- **⚡ Real-Time Conversion**: Instant code translation powered by Groq (Llama 3), Hugging Face, or OpenAI
- **📥 Download Results**: Save converted code as files
- **🎯 Auto-Detection**: Automatically detects source language from file extension
- **💻 Syntax Highlighting**: Beautiful code display with JetBrains Mono font

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
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

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

5. Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
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
- **OpenAI API** - GPT-4o for code conversion
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

1. **Install flyctl**: Follow instructions at [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/)

2. **Login to Fly.io**:
   ```bash
   fly auth login
   ```

3. **Initialize App**:
   ```bash
   cd backend
   fly launch
   ```
   - Follow the prompts (Select a region, etc.)
   - **Do not** deploy yet if asked.

4. **Set Secrets**:
   ```bash
   fly secrets set GROQ_API_KEY=your_key
   fly secrets set HUGGINGFACE_API_KEY=your_key
   fly secrets set OPENAI_API_KEY=your_key
   fly secrets set AI_PROVIDER=groq
   fly secrets set CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

The backend will be available at `https://your-app-name.fly.dev`

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```
   - Follow the prompts to link the project.

3. **Configure Environment**:
   - Go to your Vercel project dashboard.
   - Navigate to **Settings > Environment Variables**.
   - Add `VITE_API_URL` with your Fly.io backend URL (e.g., `https://your-app-name.fly.dev`).

4. **Redeploy**:
   ```bash
   vercel --prod
   ```

The frontend will be available at `https://your-project.vercel.app`

## 💡 Future Enhancements

- [ ] **Streaming Conversion**: Real-time output as code is generated
- [ ] **Multi-file Support**: Convert entire projects
- [ ] **Version History**: Save and compare previous conversions
- [ ] **Side-by-side Diff**: Visual comparison of original vs converted
- [ ] **Authentication**: User accounts and saved projects
- [ ] **API Access**: Public API for developers
- [ ] **More Languages**: Support for Rust, C++, C#, Ruby, etc.

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Important Notes

- **API Costs**: Each conversion makes a call to OpenAI's API, which incurs costs
- **Rate Limits**: OpenAI has rate limits on API calls
- **Code Quality**: AI-generated code should be reviewed before production use

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ using Vue.js, FastAPI, and OpenAI**
