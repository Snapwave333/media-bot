from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import os
from pathlib import Path
import aiofiles
from app.database import get_db
from app.models import User, VideoJob, JobStatus
from app.schemas import VideoJobCreate, VideoJobResponse, VideoJobListResponse, AvailableStyles
from app.auth import get_current_user
from app.config import get_settings
from app.tasks import process_music_video
from app.celery_app import celery_app

settings = get_settings()
router = APIRouter(prefix="/videos", tags=["Video Jobs"])

# Ensure upload directory exists
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=VideoJobResponse)
async def create_video_job(
    audio_file: UploadFile = File(...),
    lyrics: Optional[str] = Form(None),
    style_preset: Optional[str] = Form("abstract_vj"),
    video_width: Optional[int] = Form(1920),
    video_height: Optional[int] = Form(1080),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an audio file and optional lyrics to create a new video job.
    """
    # Validate file type
    if not audio_file.filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio file format. Supported: MP3, WAV, FLAC, M4A, OGG"
        )

    # Check file size
    file_size = 0
    contents = await audio_file.read()
    file_size = len(contents)
    await audio_file.seek(0)

    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )

    # Save audio file
    upload_path = Path(settings.upload_dir) / f"user_{current_user.id}"
    upload_path.mkdir(parents=True, exist_ok=True)

    audio_filename = f"{current_user.id}_{audio_file.filename}"
    audio_path = upload_path / audio_filename

    async with aiofiles.open(str(audio_path), 'wb') as f:
        await f.write(contents)

    # Create job record
    new_job = VideoJob(
        user_id=current_user.id,
        audio_file_path=str(audio_path),
        lyrics_text=lyrics,
        style_preset=style_preset,
        video_width=video_width,
        video_height=video_height,
        status=JobStatus.PENDING
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    return new_job


@router.post("/{job_id}/start")
async def start_video_processing(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start processing a video job. This should be called after payment is confirmed.
    """
    # Get job
    result = await db.execute(
        select(VideoJob).where(
            VideoJob.id == job_id,
            VideoJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Job is already {job.status.value}"
        )

    # Start Celery task
    task = process_music_video.delay(job_id)

    return {
        "job_id": job_id,
        "task_id": task.id,
        "status": "processing_started"
    }


@router.get("/", response_model=List[VideoJobListResponse])
async def list_video_jobs(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all video jobs for the current user."""
    result = await db.execute(
        select(VideoJob)
        .where(VideoJob.user_id == current_user.id)
        .order_by(VideoJob.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    jobs = result.scalars().all()
    return jobs


@router.get("/{job_id}", response_model=VideoJobResponse)
async def get_video_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific video job."""
    result = await db.execute(
        select(VideoJob).where(
            VideoJob.id == job_id,
            VideoJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/{job_id}/status")
async def get_job_status(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current status and progress of a video job."""
    result = await db.execute(
        select(VideoJob).where(
            VideoJob.id == job_id,
            VideoJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get Celery task status if processing
    task_info = None
    if job.status in [JobStatus.ANALYZING, JobStatus.GENERATING, JobStatus.EDITING]:
        # Try to get task info from Celery
        # This would require storing task_id in the job
        pass

    return {
        "job_id": job_id,
        "status": job.status,
        "error_message": job.error_message,
        "output_ready": job.output_video_path is not None
    }


@router.get("/{job_id}/download")
async def download_video(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download the generated video file."""
    result = await db.execute(
        select(VideoJob).where(
            VideoJob.id == job_id,
            VideoJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Video not yet ready")

    if not job.output_video_path or not os.path.exists(job.output_video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        job.output_video_path,
        media_type="video/mp4",
        filename=f"music_video_{job_id}.mp4"
    )


@router.get("/{job_id}/thumbnail")
async def get_thumbnail(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the thumbnail image for a video."""
    result = await db.execute(
        select(VideoJob).where(
            VideoJob.id == job_id,
            VideoJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.thumbnail_path or not os.path.exists(job.thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(
        job.thumbnail_path,
        media_type="image/jpeg"
    )


@router.delete("/{job_id}")
async def delete_video_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a video job and its associated files."""
    result = await db.execute(
        select(VideoJob).where(
            VideoJob.id == job_id,
            VideoJob.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Delete associated files
    files_to_delete = [
        job.audio_file_path,
        job.output_video_path,
        job.thumbnail_path
    ]

    for file_path in files_to_delete:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    # Delete job from database
    await db.delete(job)
    await db.commit()

    return {"message": "Job deleted successfully"}


@router.get("/styles/available", response_model=AvailableStyles)
async def get_available_styles():
    """Get list of available visual style presets."""
    return AvailableStyles()
