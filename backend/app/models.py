from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    EDITING = "editing"
    COMPLETED = "completed"
    FAILED = "failed"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Stripe
    stripe_customer_id = Column(String(255), unique=True)
    subscription_status = Column(SQLEnum(SubscriptionStatus), nullable=True)
    subscription_id = Column(String(255), nullable=True)

    # Relationships
    video_jobs = relationship("VideoJob", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Input files
    audio_file_path = Column(String(500), nullable=False)
    lyrics_text = Column(Text, nullable=True)

    # Analysis results
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    tempo = Column(Float)
    key = Column(String(50))
    duration = Column(Float)
    beat_times = Column(JSON)  # List of beat timestamps
    sections = Column(JSON)    # Song sections with moods
    mood_analysis = Column(JSON)  # Overall mood data

    # Output
    output_video_path = Column(String(500))
    thumbnail_path = Column(String(500))
    error_message = Column(Text)

    # Settings
    style_preset = Column(String(100), default="abstract_vj")
    video_width = Column(Integer, default=1920)
    video_height = Column(Integer, default=1080)

    # Relationships
    user = relationship("User", back_populates="video_jobs")
    generated_clips = relationship("GeneratedClip", back_populates="video_job")
    payment = relationship("Payment", back_populates="video_job", uselist=False)


class GeneratedClip(Base):
    __tablename__ = "generated_clips"

    id = Column(Integer, primary_key=True, index=True)
    video_job_id = Column(Integer, ForeignKey("video_jobs.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Clip info
    clip_path = Column(String(500), nullable=False)
    start_time = Column(Float)  # Where this clip starts in final video
    duration = Column(Float)
    prompt = Column(Text)  # The AI prompt used to generate this clip
    mood = Column(String(100))
    section_type = Column(String(100))  # verse, chorus, bridge, etc.

    # Generation metadata
    generation_service = Column(String(50))  # runway, kaiber, replicate, etc.
    generation_params = Column(JSON)

    # Relationships
    video_job = relationship("VideoJob", back_populates="generated_clips")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_job_id = Column(Integer, ForeignKey("video_jobs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Stripe
    stripe_payment_intent_id = Column(String(255), unique=True)
    amount = Column(Integer)  # In cents
    currency = Column(String(10), default="usd")
    status = Column(String(50))

    # Type
    payment_type = Column(String(50))  # single_video, subscription

    # Relationships
    user = relationship("User", back_populates="payments")
    video_job = relationship("VideoJob", back_populates="payment")
