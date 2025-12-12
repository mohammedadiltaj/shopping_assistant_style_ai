# Setup Guide

## Prerequisites

- Docker Desktop installed and running
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

## Step-by-Step Setup

### 1. Environment Configuration

Create `.env` files from the examples:

```bash
# Root directory
cp .env.example .env

# Backend
cp backend/.env.example backend/.env

# Frontend (optional, uses root .env)
cp frontend/.env.example frontend/.env
```

Edit the `.env` files and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Start Database and Backend

```bash
# Start PostgreSQL with pgvector
docker-compose up -d postgres

# Wait for database to be ready (about 10 seconds)
```

### 3. Generate Synthetic Data

```bash
cd backend
python scripts/generate_synthetic_data.py
```

This will create JSON and Parquet files in the `data/` directory:
- 1,500 products
- 30,000 SKUs
- 6,000 reviews
- 15,000 customers
- 20,000 orders

### 4. Load Data into Database

```bash
# Make sure you're in the backend directory
python scripts/load_data.py
```

This will:
- Create all database tables
- Load product hierarchy
- Load products, variants, and SKUs
- Load customers and style profiles
- Load reviews and orders

### 5. Start Backend API

```bash
# From backend directory
uvicorn main:app --reload
```

Or use Docker:
```bash
docker-compose up -d backend
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 6. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## Quick Test

1. Open http://localhost:3000
2. In the chat interface, try:
   - "Find me a blue dress"
   - "Show me casual outfits"
   - "What's my order status?"
   - "I want to return an item"

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps

# Check database logs
docker logs shopping_assistant_db

# Restart database
docker-compose restart postgres
```

### Backend Not Starting

- Check that `OPENAI_API_KEY` is set in `.env`
- Verify database is running: `docker ps`
- Check backend logs: `docker logs shopping_assistant_backend`

### Frontend Not Connecting

- Verify `NEXT_PUBLIC_API_URL` in frontend `.env` points to `http://localhost:8000`
- Check browser console for CORS errors
- Ensure backend is running

### Data Loading Issues

- Make sure you've run `generate_synthetic_data.py` first
- Check that `data/` directory exists with JSON files
- Verify database connection string in `.env`

## Production Deployment

For production, update:
1. Database credentials in `docker-compose.yml`
2. Environment variables
3. CORS settings in `backend/main.py`
4. Next.js build configuration

```bash
# Build frontend
cd frontend
npm run build

# Start production
docker-compose -f docker-compose.prod.yml up -d
```

