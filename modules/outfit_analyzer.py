"""
Advanced Outfit Color Analyzer Module
=====================================
Extracts and analyzes colors from outfit images using multiple
color analysis libraries for accurate identification.

Uses: ColorThief, colormath for professional color analysis
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import io
import tempfile
import os
from colorthief import ColorThief
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


class OutfitAnalyzer:
    """Advanced outfit color analyzer using multiple color science libraries"""
    
    # Comprehensive color database with color theory categories
    COLOR_DATABASE = {
        # Reds
        "Red": {"rgb": (255, 0, 0), "family": "red", "temp": "warm", "season_affinity": ["Winter", "Autumn"]},
        "Crimson": {"rgb": (220, 20, 60), "family": "red", "temp": "cool", "season_affinity": ["Winter"]},
        "Scarlet": {"rgb": (255, 36, 0), "family": "red", "temp": "warm", "season_affinity": ["Autumn", "Spring"]},
        "Ruby": {"rgb": (224, 17, 95), "family": "red", "temp": "cool", "season_affinity": ["Winter"]},
        "Burgundy": {"rgb": (128, 0, 32), "family": "red", "temp": "cool", "season_affinity": ["Winter", "Autumn"]},
        "Maroon": {"rgb": (128, 0, 0), "family": "red", "temp": "warm", "season_affinity": ["Autumn"]},
        "Wine": {"rgb": (114, 47, 55), "family": "red", "temp": "cool", "season_affinity": ["Summer", "Autumn"]},
        "Cherry": {"rgb": (222, 49, 99), "family": "red", "temp": "cool", "season_affinity": ["Winter"]},
        "Tomato Red": {"rgb": (255, 99, 71), "family": "red", "temp": "warm", "season_affinity": ["Autumn", "Spring"]},
        "Brick Red": {"rgb": (203, 65, 84), "family": "red", "temp": "warm", "season_affinity": ["Autumn"]},
        
        # Pinks
        "Pink": {"rgb": (255, 192, 203), "family": "pink", "temp": "cool", "season_affinity": ["Summer", "Spring"]},
        "Hot Pink": {"rgb": (255, 105, 180), "family": "pink", "temp": "cool", "season_affinity": ["Winter", "Spring"]},
        "Fuchsia": {"rgb": (255, 0, 255), "family": "pink", "temp": "cool", "season_affinity": ["Winter"]},
        "Magenta": {"rgb": (255, 0, 144), "family": "pink", "temp": "cool", "season_affinity": ["Winter"]},
        "Rose": {"rgb": (255, 0, 127), "family": "pink", "temp": "cool", "season_affinity": ["Summer", "Winter"]},
        "Blush": {"rgb": (222, 93, 131), "family": "pink", "temp": "warm", "season_affinity": ["Spring", "Summer"]},
        "Coral": {"rgb": (255, 127, 80), "family": "pink", "temp": "warm", "season_affinity": ["Spring", "Autumn"]},
        "Salmon": {"rgb": (250, 128, 114), "family": "pink", "temp": "warm", "season_affinity": ["Spring", "Autumn"]},
        "Dusty Rose": {"rgb": (194, 125, 160), "family": "pink", "temp": "neutral", "season_affinity": ["Summer", "Autumn"]},
        "Mauve": {"rgb": (224, 176, 255), "family": "pink", "temp": "cool", "season_affinity": ["Summer"]},
        
        # Oranges
        "Orange": {"rgb": (255, 165, 0), "family": "orange", "temp": "warm", "season_affinity": ["Autumn", "Spring"]},
        "Tangerine": {"rgb": (255, 144, 0), "family": "orange", "temp": "warm", "season_affinity": ["Spring"]},
        "Peach": {"rgb": (255, 218, 185), "family": "orange", "temp": "warm", "season_affinity": ["Spring", "Autumn"]},
        "Apricot": {"rgb": (251, 206, 177), "family": "orange", "temp": "warm", "season_affinity": ["Spring"]},
        "Rust": {"rgb": (183, 65, 14), "family": "orange", "temp": "warm", "season_affinity": ["Autumn"]},
        "Terracotta": {"rgb": (204, 78, 92), "family": "orange", "temp": "warm", "season_affinity": ["Autumn"]},
        "Burnt Orange": {"rgb": (204, 85, 0), "family": "orange", "temp": "warm", "season_affinity": ["Autumn"]},
        "Pumpkin": {"rgb": (255, 117, 24), "family": "orange", "temp": "warm", "season_affinity": ["Autumn"]},
        "Copper": {"rgb": (184, 115, 51), "family": "orange", "temp": "warm", "season_affinity": ["Autumn"]},
        
        # Yellows
        "Yellow": {"rgb": (255, 255, 0), "family": "yellow", "temp": "warm", "season_affinity": ["Spring", "Winter"]},
        "Gold": {"rgb": (255, 215, 0), "family": "yellow", "temp": "warm", "season_affinity": ["Autumn", "Spring"]},
        "Mustard": {"rgb": (255, 219, 88), "family": "yellow", "temp": "warm", "season_affinity": ["Autumn"]},
        "Lemon": {"rgb": (255, 247, 0), "family": "yellow", "temp": "cool", "season_affinity": ["Spring", "Winter"]},
        "Cream": {"rgb": (255, 253, 208), "family": "yellow", "temp": "warm", "season_affinity": ["Spring", "Autumn"]},
        "Ivory": {"rgb": (255, 255, 240), "family": "yellow", "temp": "warm", "season_affinity": ["Spring", "Autumn"]},
        "Champagne": {"rgb": (247, 231, 206), "family": "yellow", "temp": "warm", "season_affinity": ["Spring", "Autumn"]},
        "Honey": {"rgb": (235, 177, 52), "family": "yellow", "temp": "warm", "season_affinity": ["Autumn"]},
        "Amber": {"rgb": (255, 191, 0), "family": "yellow", "temp": "warm", "season_affinity": ["Autumn"]},
        
        # Greens
        "Green": {"rgb": (0, 128, 0), "family": "green", "temp": "neutral", "season_affinity": ["Autumn"]},
        "Emerald": {"rgb": (80, 200, 120), "family": "green", "temp": "cool", "season_affinity": ["Winter"]},
        "Jade": {"rgb": (0, 168, 107), "family": "green", "temp": "cool", "season_affinity": ["Summer", "Winter"]},
        "Olive": {"rgb": (128, 128, 0), "family": "green", "temp": "warm", "season_affinity": ["Autumn"]},
        "Sage": {"rgb": (188, 184, 138), "family": "green", "temp": "neutral", "season_affinity": ["Summer", "Autumn"]},
        "Mint": {"rgb": (152, 255, 152), "family": "green", "temp": "cool", "season_affinity": ["Spring", "Summer"]},
        "Forest Green": {"rgb": (34, 139, 34), "family": "green", "temp": "cool", "season_affinity": ["Autumn", "Winter"]},
        "Moss": {"rgb": (138, 154, 91), "family": "green", "temp": "warm", "season_affinity": ["Autumn"]},
        "Lime": {"rgb": (191, 255, 0), "family": "green", "temp": "warm", "season_affinity": ["Spring"]},
        "Teal": {"rgb": (0, 128, 128), "family": "green", "temp": "cool", "season_affinity": ["Autumn", "Summer"]},
        "Turquoise": {"rgb": (64, 224, 208), "family": "green", "temp": "cool", "season_affinity": ["Spring", "Summer"]},
        "Aqua": {"rgb": (0, 255, 255), "family": "green", "temp": "cool", "season_affinity": ["Winter", "Spring"]},
        "Seafoam": {"rgb": (159, 226, 191), "family": "green", "temp": "cool", "season_affinity": ["Summer"]},
        "Khaki": {"rgb": (195, 176, 145), "family": "green", "temp": "warm", "season_affinity": ["Autumn"]},
        
        # Blues
        "Blue": {"rgb": (0, 0, 255), "family": "blue", "temp": "cool", "season_affinity": ["Winter"]},
        "Navy": {"rgb": (0, 0, 128), "family": "blue", "temp": "cool", "season_affinity": ["Winter", "Summer"]},
        "Royal Blue": {"rgb": (65, 105, 225), "family": "blue", "temp": "cool", "season_affinity": ["Winter"]},
        "Cobalt": {"rgb": (0, 71, 171), "family": "blue", "temp": "cool", "season_affinity": ["Winter"]},
        "Sky Blue": {"rgb": (135, 206, 235), "family": "blue", "temp": "cool", "season_affinity": ["Summer", "Spring"]},
        "Baby Blue": {"rgb": (137, 207, 240), "family": "blue", "temp": "cool", "season_affinity": ["Summer"]},
        "Powder Blue": {"rgb": (176, 224, 230), "family": "blue", "temp": "cool", "season_affinity": ["Summer"]},
        "Steel Blue": {"rgb": (70, 130, 180), "family": "blue", "temp": "cool", "season_affinity": ["Summer"]},
        "Denim": {"rgb": (21, 96, 189), "family": "blue", "temp": "cool", "season_affinity": ["Summer", "Autumn"]},
        "Indigo": {"rgb": (75, 0, 130), "family": "blue", "temp": "cool", "season_affinity": ["Winter"]},
        "Periwinkle": {"rgb": (204, 204, 255), "family": "blue", "temp": "cool", "season_affinity": ["Summer", "Spring"]},
        "Slate Blue": {"rgb": (106, 90, 205), "family": "blue", "temp": "cool", "season_affinity": ["Summer"]},
        
        # Purples
        "Purple": {"rgb": (128, 0, 128), "family": "purple", "temp": "cool", "season_affinity": ["Winter"]},
        "Violet": {"rgb": (238, 130, 238), "family": "purple", "temp": "cool", "season_affinity": ["Summer", "Winter"]},
        "Lavender": {"rgb": (230, 230, 250), "family": "purple", "temp": "cool", "season_affinity": ["Summer"]},
        "Plum": {"rgb": (221, 160, 221), "family": "purple", "temp": "cool", "season_affinity": ["Summer", "Autumn"]},
        "Grape": {"rgb": (111, 45, 168), "family": "purple", "temp": "cool", "season_affinity": ["Winter"]},
        "Eggplant": {"rgb": (97, 64, 81), "family": "purple", "temp": "cool", "season_affinity": ["Autumn", "Winter"]},
        "Orchid": {"rgb": (218, 112, 214), "family": "purple", "temp": "cool", "season_affinity": ["Summer"]},
        "Lilac": {"rgb": (200, 162, 200), "family": "purple", "temp": "cool", "season_affinity": ["Summer"]},
        "Amethyst": {"rgb": (153, 102, 204), "family": "purple", "temp": "cool", "season_affinity": ["Summer", "Winter"]},
        
        # Browns
        "Brown": {"rgb": (139, 69, 19), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        "Chocolate": {"rgb": (123, 63, 0), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        "Coffee": {"rgb": (111, 78, 55), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        "Camel": {"rgb": (193, 154, 107), "family": "brown", "temp": "warm", "season_affinity": ["Autumn", "Spring"]},
        "Tan": {"rgb": (210, 180, 140), "family": "brown", "temp": "warm", "season_affinity": ["Autumn", "Spring"]},
        "Beige": {"rgb": (245, 245, 220), "family": "brown", "temp": "warm", "season_affinity": ["Autumn", "Spring"]},
        "Taupe": {"rgb": (72, 60, 50), "family": "brown", "temp": "neutral", "season_affinity": ["Summer", "Autumn"]},
        "Mocha": {"rgb": (190, 160, 140), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        "Espresso": {"rgb": (78, 54, 41), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        "Cocoa": {"rgb": (210, 105, 30), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        "Mahogany": {"rgb": (192, 64, 0), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        "Sienna": {"rgb": (160, 82, 45), "family": "brown", "temp": "warm", "season_affinity": ["Autumn"]},
        
        # Neutrals
        "Black": {"rgb": (0, 0, 0), "family": "neutral", "temp": "cool", "season_affinity": ["Winter"]},
        "White": {"rgb": (255, 255, 255), "family": "neutral", "temp": "cool", "season_affinity": ["Winter", "Summer"]},
        "Gray": {"rgb": (128, 128, 128), "family": "neutral", "temp": "neutral", "season_affinity": ["Summer"]},
        "Charcoal": {"rgb": (54, 69, 79), "family": "neutral", "temp": "cool", "season_affinity": ["Winter", "Summer"]},
        "Silver": {"rgb": (192, 192, 192), "family": "neutral", "temp": "cool", "season_affinity": ["Summer", "Winter"]},
        "Off-White": {"rgb": (250, 249, 246), "family": "neutral", "temp": "warm", "season_affinity": ["Spring", "Autumn"]},
        "Stone": {"rgb": (146, 142, 133), "family": "neutral", "temp": "neutral", "season_affinity": ["Summer", "Autumn"]},
        "Slate": {"rgb": (112, 128, 144), "family": "neutral", "temp": "cool", "season_affinity": ["Summer"]},
    }
    
    def __init__(self, n_colors: int = 5):
        """Initialize outfit analyzer"""
        self.n_colors = n_colors
    
    def analyze(self, image_bytes: bytes) -> dict:
        """
        Analyze outfit image using multiple color extraction methods
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            dict with comprehensive color analysis
        """
        try:
            # Load image
            image = self._load_image(image_bytes)
            
            if image is None:
                return {"success": False, "error": "Could not load image"}
            
            # Method 1: ColorThief for dominant color (most accurate)
            dominant_color = self._extract_with_colorthief(image_bytes)
            
            # Method 2: K-means clustering for color palette
            kmeans_colors, percentages = self._extract_colors(self._preprocess_image(image))
            
            # Use ColorThief result if available, else K-means
            if dominant_color:
                r, g, b = dominant_color
            elif kmeans_colors is not None and len(kmeans_colors) > 0:
                r, g, b = int(kmeans_colors[0][0]), int(kmeans_colors[0][1]), int(kmeans_colors[0][2])
            else:
                return {"success": False, "error": "Could not extract colors"}
            
            # Find closest named color using Delta E 2000 (perceptually accurate)
            color_match = self._find_closest_color(r, g, b)
            
            # Get color properties using color theory
            color_properties = self._analyze_color_properties(r, g, b)
            
            # Convert to hex
            hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            
            # Build all colors list
            all_colors = []
            if kmeans_colors is not None and percentages is not None:
                for i, (color, pct) in enumerate(zip(kmeans_colors, percentages)):
                    cr, cg, cb = int(color[0]), int(color[1]), int(color[2])
                    match = self._find_closest_color(cr, cg, cb)
                    all_colors.append({
                        "rgb": [cr, cg, cb],
                        "hex": '#{:02x}{:02x}{:02x}'.format(cr, cg, cb),
                        "name": match["name"],
                        "percentage": round(pct * 100, 1)
                    })
            
            return {
                "success": True,
                "dominant_color_name": color_match["name"],
                "dominant_color_rgb": [r, g, b],
                "dominant_color_hex": hex_color,
                "color_family": color_match["family"],
                "color_temperature": color_match["temp"],
                "season_affinity": color_match.get("season_affinity", []),
                "color_properties": color_properties,
                "match_confidence": round(color_match["confidence"], 1),
                "all_colors": all_colors
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_with_colorthief(self, image_bytes: bytes) -> tuple:
        """Extract dominant color using ColorThief (most accurate method)"""
        try:
            # Save to temp file for ColorThief
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                img = Image.open(io.BytesIO(image_bytes))
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(f.name, 'PNG')
                temp_path = f.name
            
            # Use ColorThief
            color_thief = ColorThief(temp_path)
            dominant = color_thief.get_color(quality=1)
            
            # Clean up
            os.unlink(temp_path)
            
            return dominant
        except Exception as e:
            print(f"ColorThief error: {e}")
            return None
    
    def _find_closest_color(self, r: int, g: int, b: int) -> dict:
        """Find the closest named color using CIE Delta E 2000"""
        # Convert input color to Lab
        input_rgb = sRGBColor(r/255, g/255, b/255)
        input_lab = convert_color(input_rgb, LabColor)
        
        min_delta = float('inf')
        best_match = {
            "name": "Unknown",
            "family": "neutral",
            "temp": "neutral",
            "confidence": 0
        }
        
        for name, data in self.COLOR_DATABASE.items():
            ref_r, ref_g, ref_b = data["rgb"]
            ref_rgb = sRGBColor(ref_r/255, ref_g/255, ref_b/255)
            ref_lab = convert_color(ref_rgb, LabColor)
            
            # Calculate Delta E 2000 (perceptual color difference)
            try:
                delta = delta_e_cie2000(input_lab, ref_lab)
            except:
                # Fallback to Euclidean
                delta = np.sqrt((r - ref_r)**2 + (g - ref_g)**2 + (b - ref_b)**2)
            
            if delta < min_delta:
                min_delta = delta
                best_match = {
                    "name": name,
                    "family": data["family"],
                    "temp": data["temp"],
                    "season_affinity": data.get("season_affinity", []),
                    "confidence": max(0, 100 - delta * 2)  # Convert to confidence
                }
        
        return best_match
    
    def _analyze_color_properties(self, r: int, g: int, b: int) -> dict:
        """Analyze color properties using color theory"""
        # Convert to HSV
        rgb = np.uint8([[[r, g, b]]])
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        h, s, v = hsv[0][0]
        
        # Convert to Lab
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l, a, b_ch = lab[0][0]
        
        # Saturation (chroma) level
        if s < 30:
            saturation = "muted"
        elif s < 100:
            saturation = "moderate"
        elif s < 180:
            saturation = "saturated"
        else:
            saturation = "vivid"
        
        # Value (lightness) level
        if v < 60:
            lightness = "dark"
        elif v < 120:
            lightness = "medium-dark"
        elif v < 180:
            lightness = "medium-light"
        else:
            lightness = "light"
        
        # Temperature based on hue
        if 0 <= h < 15 or h >= 165:
            temp_tendency = "warm"
        elif 15 <= h < 45:
            temp_tendency = "warm"
        elif 45 <= h < 75:
            temp_tendency = "neutral-warm"
        elif 75 <= h < 105:
            temp_tendency = "neutral"
        elif 105 <= h < 135:
            temp_tendency = "neutral-cool"
        else:
            temp_tendency = "cool"
        
        return {
            "hue": int(h * 2),
            "saturation_value": int(s / 255 * 100),
            "brightness_value": int(v / 255 * 100),
            "saturation_level": saturation,
            "lightness_level": lightness,
            "temperature_tendency": temp_tendency
        }
    
    def _load_image(self, image_bytes: bytes) -> np.ndarray:
        """Load image from bytes"""
        try:
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
            
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')
            
            return np.array(pil_image)
            
        except Exception:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is not None:
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image to focus on clothing
        - Remove very dark and very light pixels (background)
        - Apply slight blur to reduce noise
        """
        # Resize for faster processing
        max_dim = 300
        h, w = image.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            image = cv2.resize(image, (int(w * scale), int(h * scale)))
        
        # Convert to HSV to filter by saturation and value
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Create mask to exclude very dark/light/unsaturated pixels
        # These are likely background or shadows
        lower = np.array([0, 20, 30])
        upper = np.array([180, 255, 240])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Apply mask
        masked = cv2.bitwise_and(image, image, mask=mask)
        
        return masked
    
    def _extract_colors(self, image: np.ndarray):
        """Extract dominant colors using K-means clustering"""
        # Reshape image to be a list of pixels
        pixels = image.reshape(-1, 3)
        
        # Remove black pixels (from masking)
        pixels = pixels[np.any(pixels != 0, axis=1)]
        
        if len(pixels) < self.n_colors * 10:
            return None, None
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=self.n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get cluster centers (colors) and labels
        colors = kmeans.cluster_centers_
        labels = kmeans.labels_
        
        # Count pixels in each cluster
        counts = np.bincount(labels)
        percentages = counts / len(labels)
        
        # Sort by frequency (most dominant first)
        sorted_indices = np.argsort(percentages)[::-1]
        colors = colors[sorted_indices]
        percentages = percentages[sorted_indices]
        
        return colors, percentages
