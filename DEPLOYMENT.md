# Deployment Guide

## ⚠️ Important: This Project Cannot Be Deployed on Vercel

This RAG Mini-Platform is designed as a **full-stack Docker application** and **cannot be deployed on Vercel** for the following reasons:

### Why Vercel Won't Work:
1. **Backend Requirements**: FastAPI backend needs persistent storage for ChromaDB and SQLite
2. **Docker Compose**: The application requires Docker Compose orchestration
3. **Serverless Limitations**: Vercel's serverless functions can't handle the backend requirements
4. **Vector Database**: ChromaDB needs persistent file storage
5. **File Uploads**: Large file processing requires more resources than serverless functions provide

## ✅ Recommended Deployment Options

### 1. **Railway** (Recommended for Demo)
- Supports Docker Compose
- Easy deployment from GitHub
- Free tier available
- Perfect for demos and small projects

### 2. **DigitalOcean App Platform**
- Supports Docker containers
- Automatic scaling
- Good for production use

### 3. **AWS ECS/Fargate**
- Production-ready
- Scalable
- Supports Docker Compose

### 4. **Google Cloud Run**
- Serverless containers
- Good for production
- Supports Docker

### 5. **Self-Hosted (VPS)**
- Full control
- Cost-effective
- Use Docker Compose

## 🚀 Quick Deployment on Railway

1. **Fork this repository** to your GitHub account
2. **Go to [Railway](https://railway.app/)**
3. **Connect your GitHub account**
4. **Create new project** → Deploy from GitHub repo
5. **Add environment variables**:
   ```
   GROQ_API_KEY=your_actual_groq_api_key
   GROQ_MODEL=llama3-8b-8192
   ```
6. **Deploy** - Railway will automatically detect Docker Compose

## 🔧 Local Development

For local development, use the provided start script:

```bash
./start.sh
```

This will:
- Start all services with Docker Compose
- Set up the environment
- Provide access URLs

## 📝 Environment Variables

Create a `.env` file with:

```bash
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=llama3-8b-8192
CHROMA_PERSIST_DIRECTORY=./backend/chroma_db
MAX_FILE_SIZE=10485760
```

## 🚫 Removing Vercel Projects

If you have Vercel projects connected to this repository:

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Find the projects** (rag-backend, rag-frontend, rag-mini-platform)
3. **Delete each project**
4. **Disconnect from GitHub repository**

## 📊 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Vector DB     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (ChromaDB)    │
│   Port 3000     │    │   Port 8000     │    │   Persistent    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SQLite DB     │
                    │   (Metadata)    │
                    └─────────────────┘
```

## 🔍 Troubleshooting

### Common Issues:
1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **API key**: Make sure GROQ_API_KEY is set correctly
3. **File permissions**: Ensure Docker has write permissions
4. **Memory**: ChromaDB requires sufficient RAM

### Logs:
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📞 Support

For deployment issues:
1. Check the logs using `docker-compose logs`
2. Verify environment variables are set
3. Ensure Docker and Docker Compose are installed
4. Check system resources (RAM, disk space)
