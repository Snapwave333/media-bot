from moviepy.editor import (
    VideoFileClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, TextClip, vfx
)
from typing import List, Dict, Any
import os
from pathlib import Path
import numpy as np
from app.config import get_settings

settings = get_settings()


class VideoEditor:
    """
    Programmatic video editor that stitches AI-generated clips together,
    syncing cuts to the song's beat and matching visual mood to sections.
    """

    def __init__(self):
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(settings.temp_dir)

    async def compile_music_video(
        self,
        audio_path: str,
        clip_paths: List[str],
        sections: List[Dict],
        beat_times: List[float],
        job_id: int,
        mood_analysis: Dict
    ) -> str:
        """
        Compile all generated clips into a final music video synced to the audio.

        Returns:
            Path to the final compiled video
        """
        # Load audio
        audio = AudioFileClip(audio_path)

        # Load all video clips
        video_clips = []
        for path in clip_paths:
            try:
                clip = VideoFileClip(path)
                video_clips.append(clip)
            except Exception as e:
                print(f"Error loading clip {path}: {e}")

        if not video_clips:
            raise ValueError("No video clips were successfully loaded")

        # Match clips to sections and beats
        timeline = self._create_beat_synced_timeline(
            video_clips, sections, beat_times, audio.duration
        )

        # Apply transitions between clips
        final_video = self._apply_transitions(timeline, beat_times, mood_analysis)

        # Add audio
        final_video = final_video.set_audio(audio)

        # Add optional visual effects based on overall mood
        final_video = self._apply_mood_effects(final_video, mood_analysis)

        # Write final output
        output_path = self.output_dir / f"music_video_{job_id}.mp4"
        final_video.write_videofile(
            str(output_path),
            fps=settings.default_fps,
            codec='libx264',
            audio_codec='aac',
            bitrate='8000k',
            preset='medium',
            threads=4
        )

        # Clean up clips
        for clip in video_clips:
            clip.close()
        audio.close()
        final_video.close()

        # Generate thumbnail
        thumbnail_path = await self._generate_thumbnail(str(output_path), job_id)

        return str(output_path), str(thumbnail_path)

    def _create_beat_synced_timeline(
        self,
        clips: List[VideoFileClip],
        sections: List[Dict],
        beat_times: List[float],
        total_duration: float
    ) -> List[Dict]:
        """
        Create a timeline that syncs clip cuts to the beat.
        """
        timeline = []
        current_time = 0
        clip_index = 0

        # Calculate optimal cut points (every 4 or 8 beats for natural rhythm)
        cut_points = self._calculate_cut_points(beat_times, sections, total_duration)

        for i in range(len(cut_points) - 1):
            start_time = cut_points[i]
            end_time = cut_points[i + 1]
            segment_duration = end_time - start_time

            # Select appropriate clip for this segment
            clip = clips[clip_index % len(clips)]

            # Ensure clip is long enough, loop if necessary
            if clip.duration < segment_duration:
                # Loop the clip
                num_loops = int(np.ceil(segment_duration / clip.duration))
                clip = concatenate_videoclips([clip] * num_loops)

            # Trim clip to exact duration
            segment_clip = clip.subclip(0, segment_duration)

            timeline.append({
                "clip": segment_clip,
                "start_time": start_time,
                "duration": segment_duration,
                "section_index": self._find_section_for_time(start_time, sections)
            })

            clip_index += 1
            current_time = end_time

        return timeline

    def _calculate_cut_points(
        self,
        beat_times: List[float],
        sections: List[Dict],
        total_duration: float
    ) -> List[float]:
        """
        Calculate optimal cut points based on beats and sections.
        Cuts typically happen every 4 or 8 beats (1-2 bars).
        """
        cut_points = [0.0]  # Start at beginning

        # Add section boundaries as cut points
        for section in sections:
            start = section.get("start_time", 0)
            if start > 0 and start not in cut_points:
                cut_points.append(start)

        # Add beat-based cut points (every 4 beats)
        if len(beat_times) > 4:
            for i in range(0, len(beat_times), 4):
                beat_time = beat_times[i]
                if beat_time not in cut_points and beat_time > 0:
                    cut_points.append(beat_time)

        # Ensure we have the end point
        if total_duration not in cut_points:
            cut_points.append(total_duration)

        # Sort and remove duplicates
        cut_points = sorted(list(set(cut_points)))

        # Remove cut points that are too close together (minimum 2 seconds)
        filtered_cuts = [cut_points[0]]
        for cut in cut_points[1:]:
            if cut - filtered_cuts[-1] >= 2.0:
                filtered_cuts.append(cut)

        if filtered_cuts[-1] != total_duration:
            filtered_cuts.append(total_duration)

        return filtered_cuts

    def _find_section_for_time(self, time: float, sections: List[Dict]) -> int:
        """Find which section a given time belongs to."""
        for i, section in enumerate(sections):
            if section["start_time"] <= time < section["end_time"]:
                return i
        return 0

    def _apply_transitions(
        self,
        timeline: List[Dict],
        beat_times: List[float],
        mood_analysis: Dict
    ) -> VideoFileClip:
        """
        Apply transitions between clips based on beat and mood.
        """
        if not timeline:
            raise ValueError("Empty timeline")

        if len(timeline) == 1:
            return timeline[0]["clip"]

        # Determine transition style based on mood
        energy = mood_analysis.get("energy", 0.5)

        if energy > 0.7:
            # Hard cuts for high energy
            transition_duration = 0.0
        elif energy > 0.4:
            # Quick crossfades
            transition_duration = 0.3
        else:
            # Longer dissolves for mellow tracks
            transition_duration = 0.8

        # Build composite timeline
        clips_with_positions = []

        for segment in timeline:
            clip = segment["clip"]
            start = segment["start_time"]

            # Apply fade in/out for crossfade effect
            if transition_duration > 0:
                clip = clip.crossfadein(transition_duration)
                clip = clip.crossfadeout(transition_duration)

            clip = clip.set_start(start)
            clips_with_positions.append(clip)

        # Composite all clips
        final = CompositeVideoClip(clips_with_positions)

        return final

    def _apply_mood_effects(self, video: VideoFileClip, mood_analysis: Dict) -> VideoFileClip:
        """
        Apply subtle visual effects based on overall mood.
        """
        energy = mood_analysis.get("energy", 0.5)
        brightness = mood_analysis.get("brightness", 0.5)

        # Apply color grading based on mood
        if brightness < 0.3:
            # Darken for moody tracks
            video = video.fx(vfx.colorx, 0.9)
        elif brightness > 0.7:
            # Brighten for uplifting tracks
            video = video.fx(vfx.colorx, 1.1)

        # Add subtle vignette for cinematic feel
        video = self._add_vignette(video)

        return video

    def _add_vignette(self, clip: VideoFileClip) -> VideoFileClip:
        """Add a subtle vignette effect to the video."""
        def vignette_frame(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]

            # Create vignette mask
            Y, X = np.ogrid[:h, :w]
            center_y, center_x = h / 2, w / 2

            # Distance from center (normalized)
            distance = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
            max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
            distance_norm = distance / max_distance

            # Vignette effect (darken edges)
            vignette = 1 - (distance_norm ** 2) * 0.3  # Subtle 30% darkening at edges

            # Apply to all channels
            result = frame.copy().astype(float)
            for i in range(3):
                result[:, :, i] = result[:, :, i] * vignette

            return result.astype(np.uint8)

        return clip.fl(vignette_frame)

    async def _generate_thumbnail(self, video_path: str, job_id: int) -> str:
        """Generate a thumbnail from the video."""
        from PIL import Image

        # Extract frame at 10% of video duration
        video = VideoFileClip(video_path)
        thumb_time = video.duration * 0.1

        # Get frame
        frame = video.get_frame(thumb_time)

        # Convert to PIL Image
        img = Image.fromarray(frame)

        # Resize to thumbnail size (maintain aspect ratio)
        img.thumbnail((640, 360))

        # Save
        thumb_path = self.output_dir / f"thumbnail_{job_id}.jpg"
        img.save(str(thumb_path), "JPEG", quality=85)

        video.close()

        return str(thumb_path)

    async def cleanup_temp_files(self, job_id: int):
        """Clean up temporary files for a job."""
        pattern = f"job_{job_id}_*"
        for file in self.temp_dir.glob(pattern):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error removing temp file {file}: {e}")
