# Deployment Guide

## ⚠️ Important: This Project is Designed for Local Development

This RAG Mini-Platform is designed as a **full-stack Docker application** for **local development and demonstration purposes**. It's not optimized for cloud deployment due to its architecture requirements.

### Why Cloud Deployment is Challenging:

1. **Backend Requirements**: FastAPI backend needs persistent storage for ChromaDB and SQLite
2. **Docker Compose**: The application requires Docker Compose orchestration
3. **Vector Database**: ChromaDB needs persistent file storage
4. **File Uploads**: Large file processing requires more resources than serverless functions provide
5. **Local Development Focus**: Designed for hands-on development and testing

## ✅ Recommended Usage

### **Local Development Only** (Recommended)

This project is best used for:

- **Local development and testing**
- **Demonstrations and presentations**
- **Learning and experimentation**
- **Personal projects**

### **Alternative Deployment Options** (Advanced)

If you need cloud deployment, consider:

1. **Self-Hosted VPS**

   - Full control
   - Cost-effective
   - Use Docker Compose

2. **AWS ECS/Fargate**

   - Production-ready
   - Scalable
   - Supports Docker Compose

3. **Google Cloud Run**

   - Serverless containers
   - Good for production
   - Supports Docker

4. **DigitalOcean App Platform**
   - Supports Docker containers
   - Automatic scaling
   - Good for production use

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

## 🚫 Removing Cloud Deployment Projects

If you have cloud deployment projects connected to this repository:

### **Vercel Projects:**

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**
2. **Find the projects** (rag-backend, rag-frontend, rag-mini-platform)
3. **Delete each project**
4. **Disconnect from GitHub repository**

### **Railway Projects:**

1. **Go to [Railway Dashboard](https://railway.app/dashboard)**
2. **Find the projects** (pleasing-upliftment, responsible-education)
3. **Delete each project**
4. **Disconnect from GitHub repository**

### **Render Projects:**

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. **Find any connected projects**
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
