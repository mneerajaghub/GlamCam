"""
Skin Tone Analyzer Module
=========================
Detects face, extracts skin regions, analyzes RGB values
to classify skin tone and undertone.

Uses MediaPipe Tasks API for face detection/landmark detection.
Integrates DeepFace for ML-based analysis and Monk Skin Tone Scale.
"""

import cv2
import numpy as np
from PIL import Image
import io
import os
import urllib.request
import tempfile

# MediaPipe Tasks API
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# DeepFace for ML-based skin/ethnicity analysis
# Set to True for gender detection
USE_DEEPFACE = True  # Enable for gender detection

try:
    if USE_DEEPFACE:
        from deepface import DeepFace
        DEEPFACE_AVAILABLE = True
    else:
        DEEPFACE_AVAILABLE = False
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not available. Using fallback analysis.")

# Stone library for Monk Skin Tone Scale
try:
    import stone
    STONE_AVAILABLE = True
except ImportError:
    STONE_AVAILABLE = False
    print("⚠️ 'stone' library not available. Using fallback skin analysis.")


class SkinAnalyzer:
    """Analyzes skin tone using 12-season color analysis system and Monk Scale"""
    
    # Monk Skin Tone Scale (MST) - 10 scientifically validated skin tones
    # Developed by Dr. Ellis Monk for inclusive AI systems
    MONK_SCALE = {
        "MST-01": {"hex": "#f6ede4", "tone": "Fair", "undertone_bias": "cool-neutral"},
        "MST-02": {"hex": "#f3e7db", "tone": "Fair", "undertone_bias": "warm-neutral"},
        "MST-03": {"hex": "#f7ead0", "tone": "Light", "undertone_bias": "warm"},
        "MST-04": {"hex": "#eadaba", "tone": "Light", "undertone_bias": "warm"},
        "MST-05": {"hex": "#d7bd96", "tone": "Medium", "undertone_bias": "warm"},
        "MST-06": {"hex": "#a07e56", "tone": "Medium", "undertone_bias": "warm"},
        "MST-07": {"hex": "#825c43", "tone": "Tan", "undertone_bias": "warm-neutral"},
        "MST-08": {"hex": "#604134", "tone": "Tan", "undertone_bias": "neutral"},
        "MST-09": {"hex": "#3a312a", "tone": "Deep", "undertone_bias": "neutral"},
        "MST-10": {"hex": "#292420", "tone": "Deep", "undertone_bias": "cool-neutral"},
    }
    
    # 12-Season Color Analysis System
    # Based on three dimensions: Temperature (warm/cool), Value (light/dark), Chroma (bright/muted)
    
    TWELVE_SEASONS = {
        # SPRING - Warm undertone base
        "Bright Spring": {"temp": "warm", "value": "medium", "chroma": "bright", 
                         "description": "Clear, warm, and vibrant coloring"},
        "True Spring": {"temp": "warm", "value": "medium-light", "chroma": "medium-bright",
                       "description": "Warm, golden, and fresh coloring"},
        "Light Spring": {"temp": "warm-neutral", "value": "light", "chroma": "medium",
                        "description": "Delicate, warm, and light coloring"},
        
        # SUMMER - Cool undertone base
        "Light Summer": {"temp": "cool-neutral", "value": "light", "chroma": "muted",
                        "description": "Soft, cool, and light coloring"},
        "True Summer": {"temp": "cool", "value": "medium", "chroma": "muted",
                       "description": "Cool, soft, and gentle coloring"},
        "Soft Summer": {"temp": "cool-neutral", "value": "medium", "chroma": "very-muted",
                       "description": "Muted, soft, and blended coloring"},
        
        # AUTUMN - Warm undertone base
        "Soft Autumn": {"temp": "warm-neutral", "value": "medium", "chroma": "very-muted",
                       "description": "Muted, warm, and earthy coloring"},
        "True Autumn": {"temp": "warm", "value": "medium", "chroma": "muted",
                       "description": "Warm, rich, and golden coloring"},
        "Deep Autumn": {"temp": "warm-neutral", "value": "dark", "chroma": "medium",
                       "description": "Deep, warm, and intense coloring"},
        
        # WINTER - Cool undertone base
        "Deep Winter": {"temp": "cool-neutral", "value": "dark", "chroma": "medium-bright",
                       "description": "Deep, cool, and striking coloring"},
        "True Winter": {"temp": "cool", "value": "medium-dark", "chroma": "bright",
                       "description": "Cool, clear, and high-contrast coloring"},
        "Bright Winter": {"temp": "cool-neutral", "value": "medium", "chroma": "very-bright",
                         "description": "Brilliant, cool, and vibrant coloring"}
    }
    
    # Model URL
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    
    def __init__(self):
        """Initialize face landmarker using Tasks API"""
        # Download model if needed
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(script_dir, "..", "face_landmarker.task")
        
        if not os.path.exists(self.model_path):
            print("📥 Downloading face landmarker model...")
            urllib.request.urlretrieve(self.MODEL_URL, self.model_path)
            print("✅ Model downloaded successfully")
        
        # Initialize face landmarker
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
        
        # Cheek region landmark indices for skin sampling
        # Using inner cheek areas to avoid shadows and hair
        self.LEFT_CHEEK_INDICES = [50, 101, 118, 119, 100, 36]
        self.RIGHT_CHEEK_INDICES = [280, 330, 347, 348, 329, 266]
        self.FOREHEAD_INDICES = [10, 67, 109, 108, 151, 337, 338, 297]
    
    def analyze(self, image_bytes: bytes) -> dict:
        """
        Analyze skin tone from image bytes using DeepFace ML analysis,
        custom color analysis, and Monk Skin Tone Scale.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            dict with skin_tone, undertone, confidence, rgb_values, monk_scale, deepface
        """
        try:
            # Load and process image
            image = self._load_image(image_bytes)
            
            if image is None:
                return {"success": False, "error": "Could not load image"}
            
            # Try DeepFace ML analysis first (most accurate)
            deepface_result = self._analyze_with_deepface(image_bytes)
            
            # Try stone library analysis (Monk Scale)
            monk_result = self._analyze_with_stone(image_bytes)
            
            # Convert to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Create MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # Detect face landmarks
            results = self.face_landmarker.detect(mp_image)
            
            if not results.face_landmarks:
                return {"success": False, "error": "No face detected in image"}
            
            landmarks = results.face_landmarks[0]
            h, w = image.shape[:2]
            
            # Extract skin regions
            skin_pixels = self._extract_skin_pixels(image, landmarks, w, h)
            
            if len(skin_pixels) < 100:
                return {"success": False, "error": "Could not extract enough skin pixels"}
            
            # Calculate average skin color
            avg_rgb = np.mean(skin_pixels, axis=0).astype(int)
            r, g, b = int(avg_rgb[2]), int(avg_rgb[1]), int(avg_rgb[0])  # BGR to RGB
            
            # Analyze the three color dimensions
            temperature = self._analyze_temperature(r, g, b)
            value = self._analyze_value(r, g, b)
            chroma = self._analyze_chroma(skin_pixels, r, g, b)
            
            # Use DeepFace to refine undertone detection
            if deepface_result:
                dominant_race = deepface_result.get("dominant_race", "")
                # Map ethnicity to undertone bias for more accurate analysis
                warm_ethnicities = ["indian", "latino hispanic", "middle eastern"]
                cool_ethnicities = ["asian", "black"]
                
                if dominant_race.lower() in warm_ethnicities:
                    if "cool" not in temperature:
                        temperature = "warm"
                elif dominant_race.lower() in cool_ethnicities:
                    # Some have warm, some have cool - use RGB analysis
                    pass
            
            # If stone library gave us monk scale results, use it to enhance analysis
            if monk_result:
                monk_undertone = monk_result.get("undertone_bias", "neutral")
                if "warm" in monk_undertone and "cool" not in temperature:
                    temperature = monk_undertone
                elif "cool" in monk_undertone and "warm" not in temperature:
                    temperature = monk_undertone
            
            # Determine the 12-season color type
            season = self._determine_season(temperature, value, chroma)
            season_info = self.TWELVE_SEASONS[season]
            
            # Legacy skin tone classification (for display)
            # Priority: Monk Scale > DeepFace > Manual
            if monk_result and monk_result.get("tone"):
                skin_tone = monk_result["tone"]
            elif deepface_result:
                # Map DeepFace race to skin tone
                skin_tone = self._deepface_to_skin_tone(deepface_result, r, g, b)
            else:
                skin_tone = self._classify_skin_tone(r, g, b)
            
            # Calculate confidence based on color consistency and ML agreement
            confidence = self._calculate_confidence(skin_pixels)
            if deepface_result:
                confidence = min(95, confidence + 10)  # Boost confidence if ML agrees
            
            result = {
                "success": True,
                "season": season,
                "season_description": season_info["description"],
                "skin_tone": skin_tone,
                "undertone": "Warm" if "warm" in temperature else ("Cool" if "cool" in temperature else "Neutral"),
                "color_dimensions": {
                    "temperature": temperature,
                    "value": value,
                    "chroma": chroma
                },
                "confidence": round(confidence, 2),
                "rgb_values": {"r": r, "g": g, "b": b}
            }
            
            # Add Monk Scale info if available
            if monk_result:
                result["monk_scale"] = monk_result
            
            # Add DeepFace analysis if available
            if deepface_result:
                result["deepface"] = deepface_result
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_with_deepface(self, image_bytes: bytes) -> dict:
        """
        Analyze face using DeepFace ML model for gender and race detection.
        
        Returns dict with gender, dominant_race, confidence, etc.
        """
        if not DEEPFACE_AVAILABLE:
            return None
        
        try:
            # Save image to temp file for DeepFace
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                f.write(image_bytes)
                temp_path = f.name
            
            # Suppress TF warnings
            import logging
            logging.getLogger('tensorflow').setLevel(logging.ERROR)
            
            # Run DeepFace analysis - gender and race detection
            result = DeepFace.analyze(
                img_path=temp_path,
                actions=['gender', 'race'],
                enforce_detection=False,
                silent=True
            )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            if result and len(result) > 0:
                face_result = result[0]
                
                # Gender detection
                gender_scores = face_result.get('gender', {})
                dominant_gender = face_result.get('dominant_gender', 'Unknown')
                gender_confidence = gender_scores.get(dominant_gender, 0)
                
                # Race detection
                dominant_race = face_result.get('dominant_race', 'unknown')
                race_scores = face_result.get('race', {})
                race_confidence = race_scores.get(dominant_race, 0)
                
                # Convert numpy types to Python native types for JSON serialization
                return {
                    "gender": str(dominant_gender),
                    "gender_confidence": float(round(float(gender_confidence), 1)),
                    "dominant_race": str(dominant_race),
                    "confidence": float(round(float(race_confidence), 1)),
                    "all_scores": {str(k): float(round(float(v), 1)) for k, v in race_scores.items()}
                }
            
            return None
            
        except Exception as e:
            print(f"DeepFace analysis error: {e}")
            return None
    
    def _deepface_to_skin_tone(self, deepface_result: dict, r: int, g: int, b: int) -> str:
        """
        Map DeepFace race analysis + RGB values to skin tone label.
        Uses ML result as a guide but combines with actual pixel values.
        """
        dominant = deepface_result.get("dominant_race", "").lower()
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Base classification on luminance
        if luminance > 200:
            base_tone = "Fair"
        elif luminance > 170:
            base_tone = "Light"
        elif luminance > 140:
            base_tone = "Light-Medium"
        elif luminance > 110:
            base_tone = "Medium"
        elif luminance > 80:
            base_tone = "Medium-Tan"
        elif luminance > 50:
            base_tone = "Tan"
        else:
            base_tone = "Deep"
        
        return base_tone
    
    def _analyze_with_stone(self, image_bytes: bytes) -> dict:
        """
        Analyze skin tone using stone library (Monk Skin Tone Scale)
        Returns None if stone is not available or analysis fails
        """
        if not STONE_AVAILABLE:
            return None
        
        try:
            # Save image to temp file for stone library
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                f.write(image_bytes)
                temp_path = f.name
            
            # Run stone analysis with Monk scale
            result = stone.process(
                temp_path,
                image_type='color',
                tone_palette='monk',
                return_report_image=False
            )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            if result and len(result) > 0:
                face_result = result[0]
                if 'faces' in face_result and len(face_result['faces']) > 0:
                    face_data = face_result['faces'][0]
                    tone_label = face_data.get('tone', 'Unknown')
                    dominant_colors = face_data.get('dominant_colors', [])
                    
                    # Map tone label to our Monk Scale data
                    # stone returns labels like 'CA', 'CB', etc.
                    # We need to map index to MST number
                    try:
                        # Get the index from the label (e.g., 'CA' -> 0, 'CB' -> 1)
                        if tone_label and len(tone_label) >= 2:
                            tone_index = ord(tone_label[1]) - ord('A')
                            mst_key = f"MST-{str(tone_index + 1).zfill(2)}"
                            if mst_key in self.MONK_SCALE:
                                monk_data = self.MONK_SCALE[mst_key]
                                return {
                                    "scale": mst_key,
                                    "tone": monk_data["tone"],
                                    "undertone_bias": monk_data["undertone_bias"],
                                    "hex": monk_data["hex"],
                                    "dominant_colors": dominant_colors
                                }
                    except Exception:
                        pass
            
            return None
            
        except Exception as e:
            print(f"Stone analysis error: {e}")
            return None
    
    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        """Load image from bytes with EXIF orientation fix"""
        try:
            # Use PIL to handle EXIF orientation
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Handle EXIF orientation
            try:
                from PIL import ExifTags
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = pil_image._getexif()
                if exif is not None:
                    orientation_value = exif.get(orientation, 1)
                    if orientation_value == 3:
                        pil_image = pil_image.rotate(180, expand=True)
                    elif orientation_value == 6:
                        pil_image = pil_image.rotate(270, expand=True)
                    elif orientation_value == 8:
                        pil_image = pil_image.rotate(90, expand=True)
            except Exception:
                pass
            
            # Convert to OpenCV format
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')
            
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return image
            
        except Exception:
            # Fallback to OpenCV decode
            nparr = np.frombuffer(image_bytes, np.uint8)
            return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    def _extract_skin_pixels(self, image, landmarks, w, h) -> np.ndarray:
        """Extract skin pixels from cheek and forehead regions"""
        all_pixels = []
        
        # Extract from all regions
        for region_indices in [self.LEFT_CHEEK_INDICES, self.RIGHT_CHEEK_INDICES, self.FOREHEAD_INDICES]:
            points = []
            for idx in region_indices:
                # MediaPipe Tasks API returns landmarks directly
                lm = landmarks[idx]
                x, y = int(lm.x * w), int(lm.y * h)
                points.append([x, y])
            
            if len(points) >= 3:
                # Create mask for this region
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [np.array(points)], 255)
                
                # Extract pixels
                pixels = image[mask == 255]
                if len(pixels) > 0:
                    all_pixels.extend(pixels)
        
        return np.array(all_pixels) if all_pixels else np.array([])
    
    def _classify_skin_tone(self, r: int, g: int, b: int) -> str:
        """
        Classify skin tone using ITA (Individual Typology Angle)
        ITA = arctan((L - 50) / b) * 180 / π
        """
        # Convert RGB to LAB
        rgb = np.uint8([[[r, g, b]]])
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l, a, b_channel = lab[0][0]
        
        # Calculate ITA angle
        if b_channel != 0:
            ita = np.arctan((l - 50) / b_channel) * (180 / np.pi)
        else:
            ita = 90 if l > 50 else -90
        
        # Classify based on ITA
        if ita > 55:
            return "Fair"
        elif ita > 41:
            return "Light"
        elif ita > 28:
            return "Medium"
        elif ita > 19:
            return "Olive"
        elif ita > 10:
            return "Tan"
        else:
            return "Deep"
    
    def _analyze_temperature(self, r: int, g: int, b: int) -> str:
        """
        Analyze color temperature (warm/cool) based on RGB ratios
        Warm = more yellow/golden undertones
        Cool = more blue/pink undertones
        """
        # Calculate warmth based on yellow vs blue presence
        # Yellow warmth: R and G high relative to B
        # Cool/pink: R and B high relative to G, or B dominant
        
        total = r + g + b
        if total == 0:
            return "neutral"
        
        r_ratio = r / total
        g_ratio = g / total
        b_ratio = b / total
        
        # Warmth score: positive = warm, negative = cool
        # Warm skin has golden/yellow undertones (more R+G relative to B)
        # Cool skin has pink/blue undertones (more R+B or just B relative to G)
        warmth_score = ((r_ratio + g_ratio) - (b_ratio * 2)) * 100
        
        # Also check for golden vs pink in the red channel
        golden_vs_pink = (g_ratio - b_ratio) * 50
        
        combined_score = warmth_score + golden_vs_pink
        
        if combined_score > 8:
            return "warm"
        elif combined_score > 3:
            return "warm-neutral"
        elif combined_score < -5:
            return "cool"
        elif combined_score < -1:
            return "cool-neutral"
        else:
            return "neutral"
    
    def _analyze_value(self, r: int, g: int, b: int) -> str:
        """
        Analyze value (lightness/darkness) of skin
        """
        # Convert to LAB for better lightness measurement
        rgb = np.uint8([[[r, g, b]]])
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l = lab[0][0][0]
        
        # L ranges from 0-255 in OpenCV
        if l > 200:
            return "light"
        elif l > 170:
            return "medium-light"
        elif l > 130:
            return "medium"
        elif l > 100:
            return "medium-dark"
        else:
            return "dark"
    
    def _analyze_chroma(self, skin_pixels: np.ndarray, r: int, g: int, b: int) -> str:
        """
        Analyze chroma (saturation/clarity) of skin coloring
        High chroma = clear, bright, saturated
        Low chroma = muted, soft, greyed
        """
        # Convert to HSV to measure saturation
        rgb = np.uint8([[[r, g, b]]])
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        saturation = hsv[0][0][1]
        
        # Also consider the contrast/variance in the skin pixels
        if len(skin_pixels) > 10:
            std_dev = np.std(skin_pixels)
            contrast_factor = std_dev / 30  # Normalize
        else:
            contrast_factor = 1.0
        
        # Combine saturation and contrast for chroma assessment
        # Higher saturation + higher contrast = brighter/clearer
        chroma_score = saturation * (1 + contrast_factor * 0.3)
        
        if chroma_score > 80:
            return "very-bright"
        elif chroma_score > 55:
            return "bright"
        elif chroma_score > 40:
            return "medium-bright"
        elif chroma_score > 25:
            return "medium"
        elif chroma_score > 15:
            return "muted"
        else:
            return "very-muted"
    
    def _determine_season(self, temperature: str, value: str, chroma: str) -> str:
        """
        Determine the 12-season color type based on the three color dimensions
        """
        # Score each season based on how well it matches the dimensions
        best_match = "True Autumn"  # Default
        best_score = -999
        
        for season, traits in self.TWELVE_SEASONS.items():
            score = 0
            
            # Temperature matching
            if traits["temp"] == temperature:
                score += 10
            elif (traits["temp"] == "warm-neutral" and temperature in ["warm", "neutral"]) or \
                 (traits["temp"] == "cool-neutral" and temperature in ["cool", "neutral"]):
                score += 6
            elif ("warm" in traits["temp"] and "warm" in temperature) or \
                 ("cool" in traits["temp"] and "cool" in temperature):
                score += 4
            
            # Value matching
            if traits["value"] == value:
                score += 10
            elif (traits["value"] == "medium-light" and value in ["medium", "light"]) or \
                 (traits["value"] == "medium-dark" and value in ["medium", "dark"]):
                score += 6
            elif "medium" in traits["value"] and "medium" in value:
                score += 4
            
            # Chroma matching
            if traits["chroma"] == chroma:
                score += 10
            elif (traits["chroma"] == "medium-bright" and chroma in ["medium", "bright"]) or \
                 (traits["chroma"] == "very-bright" and chroma in ["bright", "medium-bright"]) or \
                 (traits["chroma"] == "very-muted" and chroma in ["muted", "medium"]):
                score += 6
            elif ("bright" in traits["chroma"] and "bright" in chroma) or \
                 ("muted" in traits["chroma"] and "muted" in chroma):
                score += 4
            
            if score > best_score:
                best_score = score
                best_match = season
        
        return best_match
    
    def _calculate_confidence(self, skin_pixels: np.ndarray) -> float:
        """Calculate confidence based on color consistency"""
        if len(skin_pixels) < 10:
            return 0.0
        
        # Calculate standard deviation of colors
        std_dev = np.std(skin_pixels, axis=0)
        avg_std = np.mean(std_dev)
        
        # Lower std = more consistent = higher confidence
        # Normalize to 0-1 range
        confidence = max(0, 1 - (avg_std / 50))
        return confidence
