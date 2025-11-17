from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import JobStatus, SubscriptionStatus


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime
    subscription_status: Optional[SubscriptionStatus]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Video Job schemas
class VideoJobCreate(BaseModel):
    lyrics_text: Optional[str] = None
    style_preset: Optional[str] = "abstract_vj"
    video_width: Optional[int] = 1920
    video_height: Optional[int] = 1080


class AudioAnalysisResult(BaseModel):
    tempo: float
    key: str
    duration: float
    beat_count: int
    sections: List[dict]
    mood: dict


class VideoJobResponse(BaseModel):
    id: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    tempo: Optional[float]
    key: Optional[str]
    duration: Optional[float]
    sections: Optional[List[dict]]
    mood_analysis: Optional[dict]
    output_video_path: Optional[str]
    thumbnail_path: Optional[str]
    error_message: Optional[str]
    style_preset: str

    class Config:
        from_attributes = True


class VideoJobListResponse(BaseModel):
    id: int
    status: JobStatus
    created_at: datetime
    style_preset: str
    duration: Optional[float]
    thumbnail_path: Optional[str]

    class Config:
        from_attributes = True


# Payment schemas
class PaymentIntentCreate(BaseModel):
    video_job_id: Optional[int] = None
    payment_type: str = "single_video"


class PaymentIntentResponse(BaseModel):
    client_secret: str
    amount: int
    currency: str


class WebhookEvent(BaseModel):
    type: str
    data: dict


# Generation schemas
class GenerationProgress(BaseModel):
    job_id: int
    status: JobStatus
    progress_percentage: float
    current_step: str
    clips_generated: int
    total_clips: int


class StylePreset(BaseModel):
    id: str
    name: str
    description: str
    example_thumbnail: str


class AvailableStyles(BaseModel):
    styles: List[StylePreset] = [
        StylePreset(
            id="abstract_vj",
            name="Abstract VJ",
            description="Dynamic abstract visuals with generative patterns, perfect for electronic music",
            example_thumbnail="/styles/abstract_vj.jpg"
        ),
        StylePreset(
            id="cinematic_narrative",
            name="Cinematic Narrative",
            description="Story-driven visuals that interpret your lyrics cinematically",
            example_thumbnail="/styles/cinematic.jpg"
        ),
        StylePreset(
            id="retro_synthwave",
            name="Retro Synthwave",
            description="80s-inspired neon aesthetics with grid landscapes and chrome",
            example_thumbnail="/styles/synthwave.jpg"
        ),
        StylePreset(
            id="organic_nature",
            name="Organic Nature",
            description="Flowing natural forms, fractals, and organic growth patterns",
            example_thumbnail="/styles/organic.jpg"
        ),
        StylePreset(
            id="glitch_art",
            name="Glitch Art",
            description="Digital distortion, data moshing, and cyberpunk aesthetics",
            example_thumbnail="/styles/glitch.jpg"
        ),
        StylePreset(
            id="minimalist",
            name="Minimalist",
            description="Clean geometric shapes and typography-focused visuals",
            example_thumbnail="/styles/minimalist.jpg"
        )
    ]
