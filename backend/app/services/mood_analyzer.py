import openai
from typing import Dict, List, Any, Optional
import json
from app.config import get_settings

settings = get_settings()


class MoodAnalyzer:
    """Uses AI to analyze lyrics and combine with audio mood for comprehensive mood analysis."""

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def analyze_lyrics(self, lyrics: str) -> Dict[str, Any]:
        """
        Analyze lyrics for mood, themes, and visual suggestions.

        Returns:
            Dictionary containing mood analysis, themes, and visual suggestions
        """
        prompt = f"""Analyze these song lyrics for mood, themes, and visual imagery.
Return a JSON object with the following structure:
{{
    "overall_mood": "primary emotional tone (e.g., melancholic, euphoric, introspective)",
    "mood_progression": ["list", "of", "mood", "changes", "throughout"],
    "themes": ["main", "thematic", "elements"],
    "imagery": ["visual", "elements", "mentioned", "or", "implied"],
    "color_palette": ["suggested", "colors", "that", "match", "mood"],
    "visual_style": "recommended visual approach (e.g., abstract, narrative, symbolic)",
    "energy_level": "low/medium/high",
    "sections": [
        {{
            "type": "verse/chorus/bridge",
            "mood": "specific mood for this section",
            "key_imagery": "main visual concept for this section",
            "suggested_visuals": "description of visuals that would work"
        }}
    ]
}}

Lyrics:
{lyrics}

Respond only with valid JSON, no additional text."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a creative director who analyzes song lyrics to suggest music video visuals. Respond only in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "overall_mood": "neutral",
                "mood_progression": ["steady"],
                "themes": ["music"],
                "imagery": ["abstract"],
                "color_palette": ["blue", "purple", "white"],
                "visual_style": "abstract",
                "energy_level": "medium",
                "sections": []
            }

    def combine_audio_and_lyrics_mood(
        self,
        audio_mood: Dict[str, Any],
        lyrics_mood: Optional[Dict[str, Any]],
        audio_sections: List[Dict]
    ) -> Dict[str, Any]:
        """
        Combine audio analysis with lyrics analysis for comprehensive mood mapping.

        Returns:
            Combined mood analysis with per-section recommendations
        """
        if not lyrics_mood:
            # If no lyrics, use audio-only analysis
            return {
                "overall_mood": audio_mood.get("primary_mood", "neutral"),
                "energy": audio_mood.get("energy", 0.5),
                "brightness": audio_mood.get("brightness", 0.5),
                "visual_style": "abstract",
                "color_palette": self._generate_colors_from_audio(audio_mood),
                "sections": self._enhance_sections_audio_only(audio_sections),
                "themes": ["musical", "abstract", "rhythm"],
                "descriptors": audio_mood.get("descriptors", [])
            }

        # Combine both analyses
        combined_mood = self._blend_moods(audio_mood, lyrics_mood)
        enhanced_sections = self._enhance_sections_with_lyrics(audio_sections, lyrics_mood)

        return {
            "overall_mood": combined_mood,
            "energy": audio_mood.get("energy", 0.5),
            "brightness": audio_mood.get("brightness", 0.5),
            "visual_style": lyrics_mood.get("visual_style", "abstract"),
            "color_palette": lyrics_mood.get("color_palette", ["blue", "purple"]),
            "sections": enhanced_sections,
            "themes": lyrics_mood.get("themes", []),
            "imagery": lyrics_mood.get("imagery", []),
            "descriptors": audio_mood.get("descriptors", [])
        }

    def _blend_moods(self, audio_mood: Dict, lyrics_mood: Dict) -> str:
        """Blend audio and lyrics mood into a unified description."""
        audio_primary = audio_mood.get("primary_mood", "neutral")
        lyrics_primary = lyrics_mood.get("overall_mood", "neutral")

        # If they align, strengthen the mood
        if audio_primary == lyrics_primary:
            return f"strongly {audio_primary}"

        # Otherwise, combine them
        return f"{lyrics_primary} with {audio_primary} undertones"

    def _generate_colors_from_audio(self, audio_mood: Dict) -> List[str]:
        """Generate color palette based purely on audio features."""
        energy = audio_mood.get("energy", 0.5)
        brightness = audio_mood.get("brightness", 0.5)
        roughness = audio_mood.get("roughness", 0.5)

        colors = []

        # Base colors on energy
        if energy > 0.7:
            colors.extend(["#FF4444", "#FF8800"])  # Reds and oranges
        elif energy < 0.3:
            colors.extend(["#334455", "#445566"])  # Dark blues
        else:
            colors.extend(["#6666FF", "#8888FF"])  # Medium blues

        # Add brightness colors
        if brightness > 0.7:
            colors.extend(["#FFFF44", "#FFFFFF"])  # Bright yellows and whites
        elif brightness < 0.3:
            colors.extend(["#221133", "#332244"])  # Deep purples
        else:
            colors.extend(["#AA88FF", "#BB99FF"])  # Medium purples

        # Add texture color based on roughness
        if roughness > 0.6:
            colors.append("#FF44FF")  # Magenta for texture
        else:
            colors.append("#44FFFF")  # Cyan for smoothness

        return colors[:5]

    def _enhance_sections_audio_only(self, audio_sections: List[Dict]) -> List[Dict]:
        """Enhance sections with visual suggestions based on audio only."""
        enhanced = []

        for section in audio_sections:
            mood = section.get("mood", {})
            section_type = section.get("type", "verse")

            # Generate visual suggestions based on audio features
            energy = mood.get("energy", 0.5)
            valence = mood.get("valence", 0.5)
            tension = mood.get("tension", 0.5)

            visual_suggestion = self._generate_visual_from_audio(energy, valence, tension, section_type)

            enhanced.append({
                **section,
                "visual_suggestion": visual_suggestion,
                "camera_movement": self._suggest_camera_movement(energy),
                "transition_style": self._suggest_transition(section_type, energy)
            })

        return enhanced

    def _enhance_sections_with_lyrics(self, audio_sections: List[Dict], lyrics_mood: Dict) -> List[Dict]:
        """Enhance sections with both audio and lyrics analysis."""
        enhanced = []
        lyrics_sections = lyrics_mood.get("sections", [])

        for i, section in enumerate(audio_sections):
            # Try to match with lyrics section
            if i < len(lyrics_sections):
                lyrics_section = lyrics_sections[i]
                visual_suggestion = lyrics_section.get("suggested_visuals", "")
                key_imagery = lyrics_section.get("key_imagery", "abstract patterns")
            else:
                visual_suggestion = ""
                key_imagery = "abstract patterns"

            mood = section.get("mood", {})
            energy = mood.get("energy", 0.5)
            section_type = section.get("type", "verse")

            if not visual_suggestion:
                visual_suggestion = self._generate_visual_from_audio(
                    energy, mood.get("valence", 0.5), mood.get("tension", 0.5), section_type
                )

            enhanced.append({
                **section,
                "visual_suggestion": visual_suggestion,
                "key_imagery": key_imagery,
                "camera_movement": self._suggest_camera_movement(energy),
                "transition_style": self._suggest_transition(section_type, energy)
            })

        return enhanced

    def _generate_visual_from_audio(self, energy: float, valence: float, tension: float, section_type: str) -> str:
        """Generate visual description from audio features."""
        visuals = []

        # Energy-based visuals
        if energy > 0.7:
            visuals.append("rapid particle explosions")
        elif energy > 0.4:
            visuals.append("flowing geometric shapes")
        else:
            visuals.append("slow-moving abstract forms")

        # Valence-based colors
        if valence > 0.7:
            visuals.append("bright warm colors")
        elif valence < 0.3:
            visuals.append("deep cool tones")
        else:
            visuals.append("balanced color spectrum")

        # Tension-based movement
        if tension > 0.6:
            visuals.append("sharp angular transformations")
        else:
            visuals.append("smooth organic transitions")

        # Section-specific
        if section_type == "chorus":
            visuals.append("maximalist visual density")
        elif section_type == "verse":
            visuals.append("focused central elements")
        elif section_type == "bridge":
            visuals.append("transitional morphing effects")

        return ", ".join(visuals)

    def _suggest_camera_movement(self, energy: float) -> str:
        """Suggest camera movement based on energy."""
        if energy > 0.7:
            return "rapid push-ins and rotations"
        elif energy > 0.4:
            return "steady dolly movements"
        else:
            return "slow floating camera"

    def _suggest_transition(self, section_type: str, energy: float) -> str:
        """Suggest transition style between sections."""
        if section_type == "chorus":
            return "hard cut on beat"
        elif section_type == "bridge":
            return "cross-dissolve"
        elif energy > 0.6:
            return "whip pan"
        else:
            return "fade through black"
