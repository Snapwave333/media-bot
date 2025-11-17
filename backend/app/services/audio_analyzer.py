import librosa
import numpy as np
from typing import Dict, List, Any
import json


class AudioAnalyzer:
    """Analyzes audio files for beat detection, tempo, key, and structure."""

    def __init__(self):
        self.sr = 22050  # Sample rate

    def analyze(self, audio_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive audio analysis.

        Returns:
            Dictionary containing tempo, key, beats, sections, and mood indicators
        """
        # Load audio file
        y, sr = librosa.load(audio_path, sr=self.sr)
        duration = librosa.get_duration(y=y, sr=sr)

        # Extract features
        tempo, beats = self._detect_tempo_and_beats(y, sr)
        key = self._detect_key(y, sr)
        sections = self._detect_sections(y, sr, beats)
        mood_features = self._extract_mood_features(y, sr)

        return {
            "tempo": float(tempo),
            "key": key,
            "duration": float(duration),
            "beat_times": [float(b) for b in beats],
            "sections": sections,
            "mood_features": mood_features
        }

    def _detect_tempo_and_beats(self, y: np.ndarray, sr: int) -> tuple:
        """Detect tempo (BPM) and beat positions."""
        # Get onset envelope
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        # Detect tempo
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

        # Get beat frames
        _, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        # Convert frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        return tempo, beat_times

    def _detect_key(self, y: np.ndarray, sr: int) -> str:
        """Detect the musical key of the track."""
        # Extract chromagram
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Sum across time to get overall chroma profile
        chroma_sum = np.sum(chroma, axis=1)

        # Find the most prominent note
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_index = np.argmax(chroma_sum)

        # Determine if major or minor using simple heuristic
        # Check relative major/minor patterns
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

        # Rotate profiles to match detected key
        rotated_major = np.roll(major_profile, key_index)
        rotated_minor = np.roll(minor_profile, key_index)

        # Calculate correlation
        chroma_norm = chroma_sum / np.sum(chroma_sum)
        major_corr = np.corrcoef(chroma_norm, rotated_major)[0, 1]
        minor_corr = np.corrcoef(chroma_norm, rotated_minor)[0, 1]

        mode = "major" if major_corr > minor_corr else "minor"

        return f"{notes[key_index]} {mode}"

    def _detect_sections(self, y: np.ndarray, sr: int, beat_times: np.ndarray) -> List[Dict]:
        """Detect song sections (verse, chorus, bridge, etc.)."""
        # Extract various features for section detection
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        rms = librosa.feature.rms(y=y)

        # Compute self-similarity matrix for structure analysis
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        rec = librosa.segment.recurrence_matrix(chroma, mode='affinity', sym=True)

        # Use structural features to segment
        bounds = librosa.segment.agglomerative(chroma, k=None)
        bound_times = librosa.frames_to_time(bounds, sr=sr)

        # Analyze each section
        sections = []
        for i in range(len(bound_times) - 1):
            start_time = float(bound_times[i])
            end_time = float(bound_times[i + 1])

            # Get frames for this section
            start_frame = librosa.time_to_frames(start_time, sr=sr)
            end_frame = librosa.time_to_frames(end_time, sr=sr)

            # Calculate section characteristics
            section_rms = np.mean(rms[:, start_frame:end_frame]) if end_frame > start_frame else 0
            section_contrast = np.mean(spectral_contrast[:, start_frame:end_frame]) if end_frame > start_frame else 0

            # Determine section type based on energy and position
            section_type = self._classify_section(i, len(bound_times) - 1, float(section_rms), float(section_contrast))

            # Determine mood for this section
            section_mood = self._analyze_section_mood(y, sr, start_time, end_time)

            sections.append({
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "type": section_type,
                "mood": section_mood,
                "energy": float(section_rms),
                "brightness": float(section_contrast)
            })

        return sections

    def _classify_section(self, index: int, total_sections: int, rms: float, contrast: float) -> str:
        """Classify section type based on position and audio features."""
        position = index / total_sections

        # Simple heuristic classification
        if index == 0:
            return "intro"
        elif index == total_sections - 1 or position > 0.9:
            return "outro"
        elif rms > 0.1 and contrast > 15:  # High energy section
            return "chorus"
        elif rms > 0.05:
            return "verse"
        else:
            return "bridge"

    def _analyze_section_mood(self, y: np.ndarray, sr: int, start_time: float, end_time: float) -> Dict[str, float]:
        """Analyze the mood of a specific section."""
        # Extract section
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        section_y = y[start_sample:end_sample]

        if len(section_y) < sr * 0.5:  # Minimum half second
            return {"energy": 0.5, "valence": 0.5, "tension": 0.5}

        # Calculate mood indicators
        rms = librosa.feature.rms(y=section_y)[0]
        zcr = librosa.feature.zero_crossing_rate(section_y)[0]
        spectral_centroid = librosa.feature.spectral_centroid(y=section_y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=section_y, sr=sr)[0]

        # Normalize and combine features
        energy = float(np.mean(rms)) * 10  # Scale up
        energy = min(1.0, max(0.0, energy))

        # Higher spectral centroid = brighter = more positive valence
        valence = float(np.mean(spectral_centroid)) / 5000
        valence = min(1.0, max(0.0, valence))

        # Higher zero crossing rate = more tension/noise
        tension = float(np.mean(zcr))
        tension = min(1.0, max(0.0, tension * 5))

        return {
            "energy": energy,
            "valence": valence,
            "tension": tension
        }

    def _extract_mood_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract overall mood features from the entire track."""
        # Global features
        rms = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

        # Calculate dynamic range
        dynamic_range = float(np.max(rms) - np.min(rms))

        # Estimate overall mood
        avg_energy = float(np.mean(rms)) * 10
        avg_brightness = float(np.mean(spectral_centroid)) / 5000
        avg_roughness = float(np.mean(zcr)) * 5

        # Mood classification
        if avg_energy > 0.7 and avg_brightness > 0.6:
            primary_mood = "energetic"
        elif avg_energy > 0.5 and avg_brightness < 0.4:
            primary_mood = "intense"
        elif avg_energy < 0.3 and avg_brightness > 0.5:
            primary_mood = "peaceful"
        elif avg_energy < 0.3 and avg_brightness < 0.4:
            primary_mood = "somber"
        elif avg_roughness > 0.6:
            primary_mood = "aggressive"
        else:
            primary_mood = "balanced"

        return {
            "primary_mood": primary_mood,
            "energy": min(1.0, max(0.0, avg_energy)),
            "brightness": min(1.0, max(0.0, avg_brightness)),
            "roughness": min(1.0, max(0.0, avg_roughness)),
            "dynamic_range": min(1.0, max(0.0, dynamic_range * 10)),
            "descriptors": self._generate_mood_descriptors(primary_mood, avg_energy, avg_brightness, avg_roughness)
        }

    def _generate_mood_descriptors(self, mood: str, energy: float, brightness: float, roughness: float) -> List[str]:
        """Generate descriptive words for the mood."""
        descriptors = [mood]

        if energy > 0.7:
            descriptors.extend(["powerful", "driving"])
        elif energy < 0.3:
            descriptors.extend(["calm", "gentle"])

        if brightness > 0.7:
            descriptors.extend(["bright", "uplifting"])
        elif brightness < 0.3:
            descriptors.extend(["dark", "deep"])

        if roughness > 0.6:
            descriptors.extend(["textured", "raw"])
        elif roughness < 0.3:
            descriptors.extend(["smooth", "clean"])

        return descriptors[:5]  # Limit to 5 descriptors
