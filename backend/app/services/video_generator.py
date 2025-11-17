import httpx
import openai
from typing import Dict, List, Any, Optional
import json
import os
import asyncio
from pathlib import Path
import base64
from app.config import get_settings

settings = get_settings()


class VideoClipGenerator:
    """
    Generates video clips using AI services.
    Supports multiple backends: OpenAI DALL-E (for images), Replicate, Runway, etc.
    """

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def generate_clip_for_section(
        self,
        section: Dict[str, Any],
        style_preset: str,
        job_id: int,
        clip_index: int
    ) -> str:
        """
        Generate a video clip for a specific song section.

        Returns:
            Path to the generated clip file
        """
        # Build the prompt based on section analysis
        prompt = self._build_generation_prompt(section, style_preset)

        # Generate visuals (images or video depending on service)
        clip_path = await self._generate_clip(
            prompt=prompt,
            duration=section.get("duration", 4.0),
            job_id=job_id,
            clip_index=clip_index,
            style_preset=style_preset,
            mood=section.get("mood", {})
        )

        return clip_path

    def _build_generation_prompt(self, section: Dict, style_preset: str) -> str:
        """Build an AI generation prompt from section analysis."""
        mood = section.get("mood", {})
        visual_suggestion = section.get("visual_suggestion", "abstract visual patterns")
        key_imagery = section.get("key_imagery", "")
        section_type = section.get("type", "verse")

        # Style-specific prompt modifiers
        style_modifiers = {
            "abstract_vj": "generative art, TouchDesigner aesthetic, particle systems, fluid simulations, abstract geometric patterns, VJ visuals, procedural animation",
            "cinematic_narrative": "cinematic, dramatic lighting, narrative storytelling, film-like composition, emotional depth, movie scene",
            "retro_synthwave": "synthwave aesthetic, neon grid landscape, retrowave, 80s style, chrome, sunset gradient, outrun",
            "organic_nature": "organic forms, nature, fractals, growth patterns, flowing water, natural textures, botanical",
            "glitch_art": "glitch art, data moshing, digital distortion, cyberpunk, corrupted visuals, pixel sorting",
            "minimalist": "minimalist, clean geometric shapes, typography, negative space, monochrome, simple forms"
        }

        style_mod = style_modifiers.get(style_preset, style_modifiers["abstract_vj"])

        # Build comprehensive prompt
        prompt_parts = [
            f"Create a visually stunning music video frame in {style_preset.replace('_', ' ')} style.",
            f"Visual style: {style_mod}.",
        ]

        # Add mood-based descriptors
        energy = mood.get("energy", 0.5)
        valence = mood.get("valence", 0.5)
        tension = mood.get("tension", 0.5)

        if energy > 0.7:
            prompt_parts.append("High energy, dynamic movement, intense visuals.")
        elif energy < 0.3:
            prompt_parts.append("Calm, serene, gentle movement.")

        if valence > 0.7:
            prompt_parts.append("Bright, uplifting colors, positive atmosphere.")
        elif valence < 0.3:
            prompt_parts.append("Deep, moody colors, introspective atmosphere.")

        if tension > 0.6:
            prompt_parts.append("Sharp contrasts, dramatic tension.")
        else:
            prompt_parts.append("Harmonious, balanced composition.")

        # Add section-specific elements
        if section_type == "chorus":
            prompt_parts.append("Peak visual intensity, maximum impact, climactic moment.")
        elif section_type == "verse":
            prompt_parts.append("Building atmosphere, focused composition, narrative progression.")
        elif section_type == "bridge":
            prompt_parts.append("Transitional moment, changing atmosphere, evolution.")
        elif section_type == "intro":
            prompt_parts.append("Opening moment, establishing atmosphere, anticipation.")
        elif section_type == "outro":
            prompt_parts.append("Concluding moment, resolution, fading energy.")

        # Add visual suggestions from lyrics analysis
        if visual_suggestion:
            prompt_parts.append(f"Visual elements: {visual_suggestion}.")

        if key_imagery:
            prompt_parts.append(f"Key imagery: {key_imagery}.")

        # Technical requirements
        prompt_parts.append("High quality, 4K resolution, cinematic aspect ratio, professional music video production value.")

        return " ".join(prompt_parts)

    async def _generate_clip(
        self,
        prompt: str,
        duration: float,
        job_id: int,
        clip_index: int,
        style_preset: str,
        mood: Dict
    ) -> str:
        """
        Generate a video clip using available AI services.

        Strategy: Generate multiple images and create motion between them,
        or use video generation APIs if available.
        """
        # For this implementation, we'll use DALL-E to generate keyframes
        # and then create motion between them using MoviePy
        num_keyframes = max(2, int(duration / 2))  # One keyframe every 2 seconds

        keyframe_paths = []

        for i in range(num_keyframes):
            # Modify prompt slightly for each keyframe to create progression
            frame_prompt = self._modify_prompt_for_keyframe(prompt, i, num_keyframes, mood)

            image_path = await self._generate_image(frame_prompt, job_id, clip_index, i)
            keyframe_paths.append(image_path)

        # Create video from keyframes with motion
        clip_path = await self._create_motion_clip(
            keyframe_paths, duration, job_id, clip_index, mood
        )

        return clip_path

    def _modify_prompt_for_keyframe(self, base_prompt: str, frame_index: int, total_frames: int, mood: Dict) -> str:
        """Modify the prompt to create visual progression across keyframes."""
        progression = frame_index / max(1, total_frames - 1)

        # Add progression-based modifications
        if progression < 0.3:
            modifier = "Beginning state, initial formation, emerging patterns."
        elif progression < 0.7:
            modifier = "Peak development, full expression, maximum complexity."
        else:
            modifier = "Resolving state, dissipating energy, transitioning away."

        return f"{base_prompt} {modifier}"

    async def _generate_image(self, prompt: str, job_id: int, clip_index: int, frame_index: int) -> str:
        """Generate a single image using DALL-E."""
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",  # Closest to 16:9
                quality="hd",
                n=1
            )

            image_url = response.data[0].url

            # Download the image
            async with httpx.AsyncClient() as client:
                image_response = await client.get(image_url)
                image_data = image_response.content

            # Save to temp directory
            image_path = self.temp_dir / f"job_{job_id}_clip_{clip_index}_frame_{frame_index}.png"
            with open(image_path, "wb") as f:
                f.write(image_data)

            return str(image_path)

        except Exception as e:
            print(f"Error generating image: {e}")
            # Create a fallback placeholder image
            return await self._create_placeholder_image(job_id, clip_index, frame_index)

    async def _create_placeholder_image(self, job_id: int, clip_index: int, frame_index: int) -> str:
        """Create a placeholder image if generation fails."""
        from PIL import Image, ImageDraw, ImageFont
        import random

        # Create abstract placeholder
        img = Image.new('RGB', (1920, 1080), color=(20, 20, 40))
        draw = ImageDraw.Draw(img)

        # Add some abstract shapes
        for _ in range(50):
            x1 = random.randint(0, 1920)
            y1 = random.randint(0, 1080)
            x2 = x1 + random.randint(50, 200)
            y2 = y1 + random.randint(50, 200)
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255),
            )
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=None)

        image_path = self.temp_dir / f"job_{job_id}_clip_{clip_index}_frame_{frame_index}.png"
        img.save(str(image_path))

        return str(image_path)

    async def _create_motion_clip(
        self,
        keyframe_paths: List[str],
        duration: float,
        job_id: int,
        clip_index: int,
        mood: Dict
    ) -> str:
        """Create a video clip from keyframes with motion effects."""
        from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip
        import numpy as np

        clips = []
        frame_duration = duration / len(keyframe_paths)

        for i, img_path in enumerate(keyframe_paths):
            # Create image clip
            clip = ImageClip(img_path).set_duration(frame_duration)

            # Add motion based on mood
            energy = mood.get("energy", 0.5)

            # Ken Burns effect (zoom and pan)
            if energy > 0.6:
                # More dynamic movement for high energy
                zoom_factor = 1.2
                clip = self._apply_ken_burns(clip, zoom_factor, frame_duration)
            else:
                # Subtle movement for lower energy
                zoom_factor = 1.05
                clip = self._apply_ken_burns(clip, zoom_factor, frame_duration)

            clips.append(clip)

        # Concatenate with crossfade
        if len(clips) > 1:
            final_clip = concatenate_videoclips(clips, method="compose")
        else:
            final_clip = clips[0]

        # Set to target resolution
        final_clip = final_clip.resize((settings.default_video_width, settings.default_video_height))

        # Write to file
        output_path = self.temp_dir / f"job_{job_id}_clip_{clip_index}.mp4"
        final_clip.write_videofile(
            str(output_path),
            fps=settings.default_fps,
            codec='libx264',
            audio=False,
            preset='medium',
            bitrate='5000k'
        )

        # Clean up keyframes
        for path in keyframe_paths:
            try:
                os.remove(path)
            except Exception:
                pass

        return str(output_path)

    def _apply_ken_burns(self, clip, zoom_factor: float, duration: float):
        """Apply Ken Burns effect (zoom and pan) to an image clip."""
        from moviepy.editor import vfx

        def zoom_effect(get_frame, t):
            """Progressive zoom effect."""
            progress = t / duration
            current_zoom = 1 + (zoom_factor - 1) * progress
            frame = get_frame(t)

            # Calculate crop dimensions
            h, w = frame.shape[:2]
            new_h = int(h / current_zoom)
            new_w = int(w / current_zoom)

            # Center crop
            y1 = (h - new_h) // 2
            x1 = (w - new_w) // 2

            cropped = frame[y1:y1+new_h, x1:x1+new_w]

            # Resize back to original
            from PIL import Image
            import numpy as np
            img = Image.fromarray(cropped)
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            return np.array(img)

        return clip.fl(zoom_effect)


class ReplicateVideoGenerator:
    """Alternative video generator using Replicate's video models."""

    def __init__(self):
        self.api_token = settings.replicate_api_token

    async def generate_video(self, prompt: str, duration: float) -> str:
        """Generate video using Replicate's models (e.g., Stable Video Diffusion)."""
        if not self.api_token:
            raise ValueError("Replicate API token not configured")

        # This would use Replicate's API to generate video
        # Implementation would depend on specific model availability
        pass


class RunwayVideoGenerator:
    """Alternative video generator using Runway ML."""

    def __init__(self):
        self.api_key = settings.runway_api_key

    async def generate_video(self, prompt: str, duration: float) -> str:
        """Generate video using Runway ML's Gen-2 or similar."""
        if not self.api_key:
            raise ValueError("Runway API key not configured")

        # This would use Runway's API
        # Implementation would follow their API documentation
        pass
