"""
Color Harmony Engine Module
===========================
Calculates compatibility score between skin tone and outfit colors
using the 12-season color analysis system.
"""

import numpy as np
import cv2


class HarmonyEngine:
    """Calculates color harmony using 12-season color analysis"""
    
    # 12-Season Color Palettes - colors that harmonize with each season
    SEASON_PALETTES = {
        # SPRING SEASONS - Warm, Light to Medium, Bright
        "Bright Spring": {
            "best": ["coral", "turquoise", "bright yellow", "warm pink", "orange red", 
                    "periwinkle", "light teal", "grass green", "bright coral", "peachy pink"],
            "good": ["ivory", "warm white", "light navy", "bright blue", "mango", 
                    "apricot", "clear red", "light orange"],
            "avoid": ["black", "dark brown", "burgundy", "dusty colors", "muted tones",
                     "charcoal", "dark navy", "olive drab"]
        },
        "True Spring": {
            "best": ["golden yellow", "coral", "peach", "warm green", "aqua", 
                    "orange", "salmon", "warm ivory", "camel", "light orange"],
            "good": ["light gold", "warm beige", "cream", "light brown", "turquoise",
                    "apricot", "warm pink", "clear teal"],
            "avoid": ["black", "pure white", "cool gray", "burgundy", "dark purple",
                     "blue-red", "cool pink", "silver"]
        },
        "Light Spring": {
            "best": ["peach", "light coral", "warm pink", "light aqua", "cream", 
                    "camel", "light gold", "soft yellow", "powder blue", "mint"],
            "good": ["ivory", "champagne", "light turquoise", "soft orange", "blush",
                    "light khaki", "warm gray", "light sage"],
            "avoid": ["black", "dark colors", "heavy burgundy", "dark navy", "charcoal",
                     "pure white", "stark colors", "neon"]
        },
        
        # SUMMER SEASONS - Cool, Light to Medium, Muted
        "Light Summer": {
            "best": ["powder blue", "soft pink", "lavender", "light gray", "rose", 
                    "soft aqua", "mauve", "periwinkle", "light plum", "dusty rose"],
            "good": ["soft white", "light navy", "cocoa", "soft teal", "pale yellow",
                    "light sage", "stone", "smoky blue"],
            "avoid": ["orange", "gold", "bright yellow", "black", "warm brown",
                     "rust", "tomato red", "bright colors"]
        },
        "True Summer": {
            "best": ["rose", "raspberry", "soft blue", "blue-gray", "plum", 
                    "watermelon", "cocoa", "soft fuchsia", "blue-red", "mauve"],
            "good": ["soft white", "lavender", "powder pink", "soft navy", "burgundy",
                    "sage", "dusty pink", "soft teal"],
            "avoid": ["orange", "gold", "warm yellow", "camel", "rust", 
                     "tomato red", "warm brown", "peachy tones"]
        },
        "Soft Summer": {
            "best": ["dusty rose", "soft blue", "sage green", "mauve", "cocoa", 
                    "blue-gray", "soft teal", "muted pink", "stone", "soft burgundy"],
            "good": ["charcoal", "dusty lavender", "soft jade", "muted plum", "taupe",
                    "soft white", "rose brown", "medium gray"],
            "avoid": ["orange", "bright yellow", "bright colors", "black", "pure white",
                     "neon", "electric blue", "hot pink"]
        },
        
        # AUTUMN SEASONS - Warm, Medium to Dark, Muted
        "Soft Autumn": {
            "best": ["soft teal", "dusty pink", "sage", "terracotta", "warm gray", 
                    "soft coral", "camel", "stone", "muted gold", "soft olive"],
            "good": ["cream", "soft brown", "dusty rose", "jade", "warm beige",
                    "soft rust", "medium gold", "cocoa"],
            "avoid": ["black", "pure white", "bright colors", "neon", "cool pink",
                     "icy blue", "electric colors", "silver"]
        },
        "True Autumn": {
            "best": ["rust", "olive", "terracotta", "gold", "teal", "warm brown", 
                    "burnt orange", "khaki", "moss green", "pumpkin"],
            "good": ["cream", "camel", "bronze", "deep teal", "mustard", "coffee",
                    "warm beige", "coral", "tomato red"],
            "avoid": ["black", "pure white", "pink", "silver", "cool gray",
                     "blue-based red", "icy colors", "cool pastels"]
        },
        "Deep Autumn": {
            "best": ["olive", "rust", "terracotta", "teal", "bronze", "warm brown", 
                    "deep gold", "burgundy", "forest green", "burnt sienna"],
            "good": ["cream", "coffee", "pumpkin", "deep orange", "moss", "copper",
                    "warm charcoal", "mahogany"],
            "avoid": ["pastels", "light pink", "powder blue", "silver", "gray",
                     "cool colors", "neon", "icy tones"]
        },
        
        # WINTER SEASONS - Cool, Medium to Dark, Bright
        "Deep Winter": {
            "best": ["black", "pure white", "burgundy", "dark teal", "charcoal", 
                    "deep purple", "true red", "emerald", "hot pink", "royal blue"],
            "good": ["navy", "dark brown", "ice gray", "icy pink", "magenta",
                    "dark green", "wine", "bright blue"],
            "avoid": ["orange", "gold", "warm brown", "camel", "peach",
                     "muted colors", "dusty tones", "earthy colors"]
        },
        "True Winter": {
            "best": ["black", "pure white", "true red", "hot pink", "royal blue", 
                    "emerald", "icy gray", "deep purple", "fuchsia", "turquoise"],
            "good": ["navy", "charcoal", "shocking pink", "icy blue", "burgundy",
                    "lemon yellow", "silver", "bright teal"],
            "avoid": ["orange", "gold", "muted colors", "warm brown", "dusty pink",
                     "earthy tones", "soft colors", "beige"]
        },
        "Bright Winter": {
            "best": ["hot pink", "bright red", "electric blue", "bright purple", "turquoise", 
                    "emerald", "bright yellow", "fuchsia", "icy violet", "bright teal"],
            "good": ["black", "white", "royal blue", "silver", "icy pink", "shocking pink",
                    "bright green", "clear colors"],
            "avoid": ["muted colors", "dusty tones", "warm brown", "gold", "orange",
                     "earthy colors", "soft pastels", "camel"]
        }
    }
    
    # Color family keywords for matching
    COLOR_FAMILIES = {
        "red": ["red", "crimson", "scarlet", "maroon", "ruby", "cherry", "fire", "brick"],
        "pink": ["pink", "rose", "salmon", "coral", "blush", "fuchsia", "magenta", "hot pink"],
        "orange": ["orange", "peach", "apricot", "tangerine", "coral", "rust", "terracotta"],
        "yellow": ["yellow", "gold", "cream", "lemon", "mustard", "amber", "honey", "champagne"],
        "green": ["green", "olive", "sage", "emerald", "jade", "lime", "mint", "forest", "teal", "turquoise"],
        "blue": ["blue", "navy", "azure", "cobalt", "royal", "sky", "ocean", "teal", "turquoise", "indigo"],
        "purple": ["purple", "violet", "lavender", "plum", "mauve", "grape", "wine", "berry", "magenta"],
        "brown": ["brown", "tan", "beige", "camel", "chocolate", "coffee", "mocha", "taupe"],
        "gray": ["gray", "grey", "silver", "charcoal", "slate", "ash"],
        "white": ["white", "cream", "ivory", "snow", "pearl"],
        "black": ["black", "ebony", "onyx", "jet"]
    }
    
    def calculate_harmony(
        self,
        skin_tone: str,
        undertone: str,
        outfit_color: str,
        outfit_rgb: list,
        season: str = None,
        color_family: str = None,
        color_temperature: str = None,
        season_affinity: list = None
    ) -> dict:
        """
        Calculate harmony score between skin and outfit using 12-season system
        
        Args:
            skin_tone: Detected skin tone (Fair, Light, Medium, etc.)
            undertone: Detected undertone (Warm, Cool, Neutral)
            outfit_color: Color name of outfit
            outfit_rgb: RGB values of outfit color
            season: The 12-season color type (e.g., "Bright Spring")
            color_family: Color family from outfit analyzer (red, blue, etc.)
            color_temperature: Warm/cool from outfit analyzer
            season_affinity: List of seasons this color works with
            
        Returns:
            dict with score (0-100), rating, and explanation
        """
        # Use season-based palette if available
        if season and season in self.SEASON_PALETTES:
            rules = self.SEASON_PALETTES[season]
        else:
            # Fallback: determine season from skin_tone and undertone
            season = self._infer_season(skin_tone, undertone)
            rules = self.SEASON_PALETTES.get(season, self.SEASON_PALETTES["Soft Autumn"])
        
        # Extract base season (Spring, Summer, Autumn, Winter)
        base_season = None
        for s in ["Spring", "Summer", "Autumn", "Winter"]:
            if s in season:
                base_season = s
                break
        
        outfit_lower = outfit_color.lower()
        
        # NEW: Check season affinity first (most accurate method)
        if season_affinity and base_season:
            if base_season in season_affinity:
                score = 85  # High score if color naturally suits the season
                matched_rule = "season_match"
            else:
                score = 45  # Lower score if not in affinity
                matched_rule = None
        else:
            score = 50  # Default neutral score
            matched_rule = None
        
        # Check which color families the outfit belongs to
        matched_families = []
        if color_family:
            matched_families.append(color_family)
        for family, keywords in self.COLOR_FAMILIES.items():
            for keyword in keywords:
                if keyword in outfit_lower:
                    matched_families.append(family)
                    break
        
        # Check best colors
        for color in rules["best"]:
            if color.lower() in outfit_lower or any(f in color.lower() for f in matched_families):
                score = 92
                matched_rule = "best"
                break
        
        # Check good colors
        if matched_rule not in ["best"]:
            for color in rules["good"]:
                if color.lower() in outfit_lower or any(f in color.lower() for f in matched_families):
                    score = max(score, 75)
                    matched_rule = "good"
                    break
        
        # Check avoid colors
        for color in rules["avoid"]:
            if color.lower() in outfit_lower or any(f in color.lower() for f in matched_families):
                score = min(score, 35)
                matched_rule = "avoid"
                break
        
        # NEW: Adjust based on temperature match
        if color_temperature and undertone:
            if undertone == "Warm" and color_temperature == "warm":
                score += 5  # Temperature harmony
            elif undertone == "Cool" and color_temperature == "cool":
                score += 5
            elif undertone == "Warm" and color_temperature == "cool":
                score -= 5  # Temperature clash
            elif undertone == "Cool" and color_temperature == "warm":
                score -= 5
        
        # Additional adjustments based on color theory
        score = self._adjust_by_saturation(score, outfit_rgb)
        score = self._adjust_by_contrast(score, skin_tone, outfit_rgb)
        
        # Clamp score
        score = max(0, min(100, score))
        
        # Generate rating and explanation
        rating = self._get_rating(score)
        explanation = self._generate_explanation(
            score, season, outfit_color, matched_rule, rules
        )
        
        return {
            "score": round(score),
            "rating": rating,
            "explanation": explanation,
            "season": season
        }
    
    def _infer_season(self, skin_tone: str, undertone: str) -> str:
        """Infer a season from basic skin tone and undertone"""
        # Map to closest season
        if undertone == "Warm":
            if skin_tone in ["Fair", "Light"]:
                return "Light Spring"
            elif skin_tone in ["Medium", "Olive"]:
                return "True Autumn"
            else:
                return "Deep Autumn"
        elif undertone == "Cool":
            if skin_tone in ["Fair", "Light"]:
                return "Light Summer"
            elif skin_tone in ["Medium"]:
                return "True Summer"
            else:
                return "Deep Winter"
        else:  # Neutral
            if skin_tone in ["Fair", "Light"]:
                return "Soft Summer"
            elif skin_tone in ["Medium", "Olive"]:
                return "Soft Autumn"
            else:
                return "Deep Autumn"
    
    def _adjust_by_saturation(self, score: float, rgb: list) -> float:
        """Adjust score based on color saturation"""
        r, g, b = rgb
        hsv = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2HSV)
        saturation = hsv[0][0][1]
        
        # Very low saturation (washed out) - slight penalty
        if saturation < 30:
            score -= 5
        # Very high saturation (neon-like) - can be harsh
        elif saturation > 240:
            score -= 10
        
        return score
    
    def _adjust_by_contrast(self, score: float, skin_tone: str, rgb: list) -> float:
        """Adjust based on contrast between skin and outfit"""
        r, g, b = rgb
        brightness = (r + g + b) / 3
        
        # Deep skin looks great with bright colors
        if skin_tone == "Deep":
            if brightness > 200:  # Bright colors
                score += 5
            elif brightness < 50:  # Very dark colors
                score -= 5
        
        # Fair skin can be washed out by very pale colors
        elif skin_tone == "Fair":
            if brightness > 230:  # Very pale
                score -= 5
        
        return score
    
    def _get_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 85:
            return "Excellent Match"
        elif score >= 70:
            return "Good Match"
        elif score >= 50:
            return "Acceptable"
        elif score >= 35:
            return "Consider Alternatives"
        else:
            return "Not Recommended"
    
    def _generate_explanation(
        self,
        score: float,
        season: str,
        outfit_color: str,
        matched_rule: str,
        rules: dict
    ) -> str:
        """Generate human-readable explanation"""
        if score >= 85:
            return f"{outfit_color} is an excellent choice for a {season}! This color harmonizes beautifully with your natural coloring and will make you look vibrant and healthy."
        elif score >= 70:
            return f"{outfit_color} works well with your {season} coloring. It complements your natural warmth/coolness and value nicely."
        elif score >= 50:
            return f"{outfit_color} is acceptable for your coloring, though as a {season}, you might shine brighter in colors like {', '.join(rules['best'][:3])}."
        elif score >= 35:
            return f"{outfit_color} may not be the most flattering choice for a {season}. Consider trying {', '.join(rules['best'][:3])} instead."
        else:
            return f"As a {season}, {outfit_color} tends to clash with your natural coloring. Your best colors are {', '.join(rules['best'][:3])}."
