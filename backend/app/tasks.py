import asyncio
from app.celery_app import celery_app
from app.services.audio_analyzer import AudioAnalyzer
from app.services.mood_analyzer import MoodAnalyzer
from app.services.video_generator import VideoClipGenerator
from app.services.video_editor import VideoEditor
from app.database import AsyncSessionLocal
from app.models import VideoJob, JobStatus, GeneratedClip
from sqlalchemy import select
import json


def run_async(coro):
    """Helper to run async functions in sync context."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Create new loop for sync context
        import nest_asyncio
        nest_asyncio.apply()
    return asyncio.run(coro)


@celery_app.task(bind=True, name="process_music_video")
def process_music_video(self, job_id: int):
    """
    Main task that orchestrates the entire music video generation pipeline.

    Steps:
    1. Analyze audio (beat detection, tempo, key)
    2. Analyze lyrics for mood (if provided)
    3. Generate video clips for each section
    4. Edit clips together with beat-synced cuts
    5. Produce final music video
    """

    async def _process():
        async with AsyncSessionLocal() as session:
            # Get the job
            result = await session.execute(select(VideoJob).where(VideoJob.id == job_id))
            job = result.scalar_one_or_none()

            if not job:
                raise ValueError(f"Job {job_id} not found")

            try:
                # Step 1: Analyze Audio
                await update_job_status(session, job, JobStatus.ANALYZING, "Analyzing audio...")

                audio_analyzer = AudioAnalyzer()
                audio_analysis = audio_analyzer.analyze(job.audio_file_path)

                # Update job with analysis results
                job.tempo = audio_analysis["tempo"]
                job.key = audio_analysis["key"]
                job.duration = audio_analysis["duration"]
                job.beat_times = audio_analysis["beat_times"]
                job.sections = audio_analysis["sections"]
                await session.commit()

                # Step 2: Analyze Lyrics and Mood
                mood_analyzer = MoodAnalyzer()

                if job.lyrics_text:
                    lyrics_mood = await mood_analyzer.analyze_lyrics(job.lyrics_text)
                else:
                    lyrics_mood = None

                # Combine audio and lyrics mood analysis
                combined_mood = mood_analyzer.combine_audio_and_lyrics_mood(
                    audio_analysis["mood_features"],
                    lyrics_mood,
                    audio_analysis["sections"]
                )

                job.mood_analysis = combined_mood
                await session.commit()

                # Step 3: Generate Video Clips
                await update_job_status(session, job, JobStatus.GENERATING, "Generating visuals...")

                video_generator = VideoClipGenerator()
                clip_paths = []

                # Generate a clip for each section (or subset for longer songs)
                sections_to_process = combined_mood.get("sections", audio_analysis["sections"])

                # Limit number of clips for cost efficiency
                max_clips = 10
                if len(sections_to_process) > max_clips:
                    # Sample sections evenly
                    step = len(sections_to_process) // max_clips
                    sections_to_process = sections_to_process[::step][:max_clips]

                for i, section in enumerate(sections_to_process):
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current_step': f'Generating clip {i+1}/{len(sections_to_process)}',
                            'progress': (i / len(sections_to_process)) * 50  # 0-50% for generation
                        }
                    )

                    clip_path = await video_generator.generate_clip_for_section(
                        section=section,
                        style_preset=job.style_preset,
                        job_id=job_id,
                        clip_index=i
                    )
                    clip_paths.append(clip_path)

                    # Save clip info to database
                    generated_clip = GeneratedClip(
                        video_job_id=job_id,
                        clip_path=clip_path,
                        start_time=section.get("start_time", 0),
                        duration=section.get("duration", 4),
                        prompt=section.get("visual_suggestion", ""),
                        mood=json.dumps(section.get("mood", {})),
                        section_type=section.get("type", "verse"),
                        generation_service="openai_dalle",
                        generation_params={"style_preset": job.style_preset}
                    )
                    session.add(generated_clip)

                await session.commit()

                # Step 4: Edit and Compile Final Video
                await update_job_status(session, job, JobStatus.EDITING, "Compiling video...")

                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current_step': 'Editing and syncing to beat',
                        'progress': 75
                    }
                )

                video_editor = VideoEditor()
                output_path, thumbnail_path = await video_editor.compile_music_video(
                    audio_path=job.audio_file_path,
                    clip_paths=clip_paths,
                    sections=audio_analysis["sections"],
                    beat_times=audio_analysis["beat_times"],
                    job_id=job_id,
                    mood_analysis=combined_mood
                )

                # Step 5: Finalize
                job.output_video_path = output_path
                job.thumbnail_path = thumbnail_path
                job.status = JobStatus.COMPLETED

                await session.commit()

                # Cleanup temp files
                await video_editor.cleanup_temp_files(job_id)

                return {
                    "job_id": job_id,
                    "status": "completed",
                    "output_path": output_path,
                    "thumbnail_path": thumbnail_path
                }

            except Exception as e:
                # Mark job as failed
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                await session.commit()

                raise

    return run_async(_process())


async def update_job_status(session, job: VideoJob, status: JobStatus, message: str = ""):
    """Update job status in database."""
    job.status = status
    await session.commit()


@celery_app.task(name="cleanup_old_jobs")
def cleanup_old_jobs(days_old: int = 30):
    """Periodic task to clean up old job files."""
    # Implementation for cleanup
    pass
