# AI Music Video SaaS

Transform your music into stunning visual experiences. Professional music videos for independent musicians—no $5,000 budget required.

**Price: $50 per video**

## Overview

An AI-powered SaaS platform that automatically generates professional music videos from uploaded audio tracks. The system uses advanced audio analysis (beat detection, tempo, mood analysis) combined with AI visual generation to create beat-synced, visually stunning music videos.

## Features

- **Audio Analysis**: Beat detection, tempo/BPM analysis, key detection, and section segmentation using librosa
- **Mood Analysis**: AI-powered lyrics and audio mood interpretation using OpenAI GPT-4
- **Visual Generation**: AI-generated visuals tailored to your music's mood and energy
- **Beat-Synced Editing**: Automatic video editing that cuts perfectly to the beat
- **Multiple Style Presets**: Abstract VJ, Cinematic, Synthwave, Organic, Glitch Art, Minimalist
- **Full-Stack SaaS**: User authentication, payment processing, job queue, and dashboard

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI    │────▶│  PostgreSQL │
│  Frontend   │     │   Backend    │     │   Database  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Redis     │
                    │   (Queue)    │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Celery     │
                    │   Worker     │
                    └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  librosa │ │  OpenAI  │ │ MoviePy/ │
        │  Audio   │ │   DALL-E │ │  FFmpeg  │
        │ Analysis │ │ Visuals  │ │  Editor  │
        └──────────┘ └──────────┘ └──────────┘
```

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **PostgreSQL** - Relational database for users and jobs
- **Redis** - Message broker for Celery
- **Celery** - Distributed task queue for video processing
- **librosa** - Audio analysis library (beat detection, tempo, key)
- **MoviePy/FFmpeg** - Video editing and compilation
- **OpenAI GPT-4** - Lyrics mood analysis
- **OpenAI DALL-E 3** - Visual generation
- **Stripe** - Payment processing

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Navigation
- **react-dropzone** - File uploads

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Stripe account (for payments)

### 1. Clone and Configure

```bash
git clone <repository-url>
cd media-bot

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Set Environment Variables

Edit `.env` with:

```env
# Required
DB_PASSWORD=your-secure-password
SECRET_KEY=your-jwt-secret-key
OPENAI_API_KEY=sk-your-openai-key

# Optional (for payments)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Start with Docker Compose

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis message broker
- FastAPI backend (port 8000)
- Celery worker
- React frontend (port 80)

### 4. Access the Application

- Frontend: http://localhost
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Development Setup

### Backend (Python)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run migrations (creates tables)
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

# Start development server
python run.py
```

### Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Celery Worker

```bash
cd backend
celery -A app.celery_app worker -l info
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create new account
- `POST /api/v1/auth/login` - Get access token
- `GET /api/v1/auth/me` - Get current user

### Video Jobs
- `POST /api/v1/videos/upload` - Upload audio and create job
- `POST /api/v1/videos/{id}/start` - Start processing
- `GET /api/v1/videos/` - List user's videos
- `GET /api/v1/videos/{id}` - Get job details
- `GET /api/v1/videos/{id}/download` - Download video
- `GET /api/v1/videos/{id}/thumbnail` - Get thumbnail
- `DELETE /api/v1/videos/{id}` - Delete video

### Payments
- `POST /api/v1/payments/create-payment-intent` - Create Stripe payment
- `POST /api/v1/payments/webhook` - Stripe webhook handler
- `GET /api/v1/payments/subscription/status` - Check subscription

## How Video Generation Works

1. **Upload**: User uploads MP3 and optional lyrics
2. **Audio Analysis**:
   - librosa detects tempo (BPM)
   - Beat positions are extracted
   - Musical key is identified
   - Song sections are segmented (intro, verse, chorus, bridge, outro)
   - Mood features extracted (energy, brightness, roughness)
3. **Mood Analysis**:
   - OpenAI GPT-4 analyzes lyrics for themes and emotions
   - Audio mood combined with lyrics mood
   - Visual suggestions generated per section
4. **Visual Generation**:
   - DALL-E 3 generates keyframe images for each section
   - Prompts tailored to mood, energy, and style preset
   - Ken Burns effect applied for motion
5. **Video Editing**:
   - MoviePy stitches clips together
   - Cuts synced to beat times (every 4-8 beats)
   - Transitions matched to energy (hard cuts vs crossfades)
   - Audio track overlaid
   - Post-processing effects (vignette, color grading)
6. **Delivery**: User downloads HD video

## Style Presets

| Style | Description |
|-------|-------------|
| **Abstract VJ** | Generative patterns, particle systems, TouchDesigner aesthetics |
| **Cinematic** | Story-driven visuals with dramatic lighting |
| **Synthwave** | 80s neon grids, retrowave, outrun aesthetics |
| **Organic** | Natural forms, fractals, flowing patterns |
| **Glitch Art** | Digital distortion, data moshing, cyberpunk |
| **Minimalist** | Clean geometry, typography, negative space |

## Pricing Model

- **Single Video**: $50 per video
- **Subscription**: Contact for monthly unlimited plans

Revenue model designed for independent musicians who need professional videos but can't afford $5,000+ traditional production costs.

## Scaling Considerations

1. **GPU Workers**: Add GPU-enabled Celery workers for faster processing
2. **CDN**: Use CloudFront/S3 for video delivery
3. **Video Generation APIs**: Integrate Runway ML, Kaiber, or Replicate for higher-quality video generation
4. **Caching**: Redis caching for frequently accessed data
5. **Load Balancing**: Multiple backend instances behind nginx/AWS ALB

## Environment Variables

See `.env.example` for all configuration options:

- Database connection
- Redis/Celery configuration
- OpenAI API credentials
- Stripe payment keys
- JWT authentication settings
- Video output settings

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Stripe webhook signature verification
- File type validation
- File size limits
- User isolation (users can only access their own data)

## Future Enhancements

- [ ] Real-time progress streaming via WebSockets
- [ ] Advanced video generation using Runway ML or Kaiber
- [ ] Custom prompt editing for advanced users
- [ ] A/B testing different visual styles
- [ ] Social sharing integrations
- [ ] Batch processing for albums
- [ ] Mobile app
- [ ] Collaborative features (bands)

## Directory Structure

```
media-bot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication
│   │   ├── celery_app.py        # Celery configuration
│   │   ├── tasks.py             # Background tasks
│   │   ├── routers/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── videos.py        # Video job endpoints
│   │   │   └── payments.py      # Payment endpoints
│   │   └── services/
│   │       ├── audio_analyzer.py    # librosa audio analysis
│   │       ├── mood_analyzer.py     # AI mood analysis
│   │       ├── video_generator.py   # AI visual generation
│   │       └── video_editor.py      # MoviePy video editing
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── store/
│   │   │   └── authStore.ts     # Zustand auth state
│   │   ├── services/
│   │   │   └── api.ts           # Axios API client
│   │   ├── components/
│   │   │   └── Layout.tsx       # App layout
│   │   └── pages/
│   │       ├── Landing.tsx      # Marketing page
│   │       ├── Login.tsx        # Login form
│   │       ├── Register.tsx     # Registration form
│   │       ├── Dashboard.tsx    # User dashboard
│   │       ├── CreateVideo.tsx  # Upload wizard
│   │       └── VideoDetail.tsx  # Video details/download
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## License

MIT License

## Support

For issues and feature requests, please open a GitHub issue.

---

Built with AI for musicians who dream big but budget smart.
