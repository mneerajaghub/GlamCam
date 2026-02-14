"""
AI Stylist Module
=================
Integrates with Google Gemini to generate personalized
styling recommendations based on analysis results.
"""

import os
import json
from typing import Optional


class StylistAI:
    """AI-powered styling recommendation engine using Gemini"""
    
    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = None
        self._init_gemini()
    
    def _init_gemini(self):
        """Initialize Google Generative AI"""
        if not self.api_key:
            print("⚠️  GEMINI_API_KEY not set. AI recommendations will use fallback rules.")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini AI initialized successfully")
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini: {e}")
            self.model = None
    
    async def generate_recommendations(
        self,
        skin_tone: str,
        undertone: str,
        outfit_color: str,
        harmony_score: int,
        occasion: str,
        outfit_weight: str,
        gender: str = "Woman"
    ) -> dict:
        """
        Generate styling recommendations
        
        Args:
            skin_tone: Detected skin tone
            undertone: Detected undertone
            outfit_color: Current outfit color
            harmony_score: Calculated harmony score
            occasion: Selected occasion type
            outfit_weight: Light/Medium/Heavy
            gender: Detected gender (Man/Woman)
            
        Returns:
            dict with styling recommendations
        """
        if self.model:
            return await self._generate_with_gemini(
                skin_tone, undertone, outfit_color,
                harmony_score, occasion, outfit_weight, gender
            )
        else:
            return self._generate_fallback(
                skin_tone, undertone, outfit_color,
                harmony_score, occasion, outfit_weight, gender
            )
    
    async def _generate_with_gemini(
        self,
        skin_tone: str,
        undertone: str,
        outfit_color: str,
        harmony_score: int,
        occasion: str,
        outfit_weight: str,
        gender: str = "Woman"
    ) -> dict:
        """Generate recommendations using Gemini API"""
        
        prompt = f"""You are an expert fashion stylist AI. Based on the following analysis, provide personalized styling recommendations.

USER PROFILE:
- Gender: {gender}
- Skin Tone: {skin_tone}
- Undertone: {undertone}
- Current Outfit Color: {outfit_color}
- Color Harmony Score: {harmony_score}/100

CONTEXT:
- Occasion: {occasion}
- Outfit Weight/Season: {outfit_weight}

Please provide {"makeup" if gender == "Woman" else "grooming"} and accessory recommendations appropriate for a {gender.lower()} in the following JSON format:
{{
    "makeup": {{
        "foundation_tip": "Brief tip about foundation matching",
        "lip_colors": ["3 recommended lip colors"],
        "eye_makeup": "Eye makeup suggestions",
        "blush": "Blush recommendation"
    }},
    "hairstyle": {{
        "style_suggestion": "Hairstyle that complements the look",
        "hair_color_tips": "If considering hair color, what would work"
    }},
    "accessories": {{
        "jewelry_metal": "Gold, silver, or rose gold recommendation",
        "jewelry_style": "Style suggestions",
        "bag_color": "Complementary bag color",
        "shoes": "Shoe color/style recommendation"
    }},
    "alternate_outfits": {{
        "better_colors": ["3-5 colors that would be more flattering"],
        "color_combinations": ["2-3 outfit color combinations"],
        "patterns": "Pattern suggestions if applicable"
    }},
    "overall_tip": "One key styling tip for this person"
}}

Provide specific, actionable advice tailored to the {skin_tone} skin tone with {undertone} undertones. Consider the {occasion} context."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            # Parse JSON from response
            # Find JSON block in response
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                recommendations = json.loads(json_str)
                return recommendations
            else:
                return self._generate_fallback(
                    skin_tone, undertone, outfit_color,
                    harmony_score, occasion, outfit_weight
                )
                
        except Exception as e:
            print(f"Gemini error: {e}")
            return self._generate_fallback(
                skin_tone, undertone, outfit_color,
                harmony_score, occasion, outfit_weight
            )
    
    def _generate_fallback(
        self,
        skin_tone: str,
        undertone: str,
        outfit_color: str,
        harmony_score: int,
        occasion: str,
        outfit_weight: str,
        gender: str = "Woman"
    ) -> dict:
        """Generate recommendations using rule-based fallback"""
        
        # Makeup/grooming recommendations based on gender and undertone
        if gender == "Woman":
            makeup = self._get_makeup_recommendations(skin_tone, undertone)
        else:
            makeup = self._get_grooming_recommendations(skin_tone, undertone)
        
        # Accessory recommendations based on gender, undertone, occasion, and outfit color
        accessories = self._get_accessory_recommendations(undertone, gender, occasion, outfit_weight, outfit_color)
        
        # Alternative colors
        better_colors = self._get_better_colors(skin_tone, undertone)
        
        # Occasion-specific outfit recommendations
        outfit_suggestions = self._get_outfit_recommendations(occasion, gender, undertone, outfit_weight)
        
        return {
            "makeup": makeup,
            "hairstyle": {
                "style_suggestion": self._get_hairstyle(occasion, gender),
                "hair_color_tips": self._get_hair_color_tip(skin_tone, undertone)
            },
            "accessories": accessories,
            "alternate_outfits": {
                "better_colors": better_colors,
                "color_combinations": self._get_color_combos(skin_tone, undertone),
                "patterns": self._get_pattern_suggestion(occasion),
                "suggested_outfits": outfit_suggestions
            },
            "overall_tip": self._get_overall_tip(skin_tone, undertone, harmony_score, gender)
        }
    
    def _get_makeup_recommendations(self, skin_tone: str, undertone: str) -> dict:
        """Get makeup recommendations based on skin analysis"""
        
        lip_colors = {
            ("Fair", "Warm"): ["Coral", "Peach", "Warm nude"],
            ("Fair", "Cool"): ["Rose pink", "Berry", "Mauve"],
            ("Fair", "Neutral"): ["Dusty rose", "Soft coral", "Pink nude"],
            ("Light", "Warm"): ["Coral red", "Peach", "Warm pink"],
            ("Light", "Cool"): ["Raspberry", "Plum", "Cool pink"],
            ("Light", "Neutral"): ["Rose", "Soft berry", "Pink"],
            ("Medium", "Warm"): ["Terracotta", "Brick red", "Orange-red"],
            ("Medium", "Cool"): ["Berry", "Wine", "Fuchsia"],
            ("Medium", "Neutral"): ["Mauve", "Dusty rose", "Soft red"],
            ("Olive", "Warm"): ["Coral", "Rust", "Warm brown"],
            ("Olive", "Cool"): ["Plum", "Berry", "Deep pink"],
            ("Olive", "Neutral"): ["Terracotta", "Mauve", "Brick"],
            ("Tan", "Warm"): ["Orange-red", "Coral", "Bronze"],
            ("Tan", "Cool"): ["Deep berry", "Plum", "Fuchsia"],
            ("Tan", "Neutral"): ["Terracotta", "Deep rose", "Red"],
            ("Deep", "Warm"): ["Orange", "Coral", "Warm red"],
            ("Deep", "Cool"): ["Fuchsia", "Deep berry", "Plum"],
            ("Deep", "Neutral"): ["True red", "Berry", "Deep coral"]
        }
        
        key = (skin_tone, undertone)
        lips = lip_colors.get(key, ["Rose", "Coral", "Natural"])
        
        blush = {
            "Warm": "Peach or coral blush",
            "Cool": "Pink or berry blush",
            "Neutral": "Dusty rose or soft peach blush"
        }
        
        eye_makeup = {
            "Warm": "Warm browns, gold, copper, and bronze eyeshadows",
            "Cool": "Cool taupes, silver, purple, and blue-toned shadows",
            "Neutral": "Soft browns, mauve, and neutral tones"
        }
        
        return {
            "foundation_tip": f"Look for foundations with {undertone.lower()} undertones for a perfect match",
            "lip_colors": lips,
            "eye_makeup": eye_makeup.get(undertone, "Neutral brown tones"),
            "blush": blush.get(undertone, "Dusty rose")
        }
    
    def _get_grooming_recommendations(self, skin_tone: str, undertone: str) -> dict:
        """Get grooming recommendations for men - beard care, skincare, etc."""
        
        # Skincare based on skin tone
        skincare = {
            ("Fair", "Warm"): "SPF 30+ daily, lightweight moisturizer with warm undertone",
            ("Fair", "Cool"): "SPF 30+ daily, hydrating cream with rose or cool tones",
            ("Medium", "Warm"): "SPF 15-30, oil-free moisturizer, anti-tan products",
            ("Medium", "Cool"): "SPF 15-30, hydrating serum, brightening products",
            ("Deep", "Warm"): "Lightweight moisturizer, vitamin C serum for glow",
            ("Deep", "Cool"): "Rich moisturizer, even-toning products"
        }
        
        # Lip care for men
        lip_care = {
            "Warm": "Tinted lip balm with warm undertone, SPF lip care",
            "Cool": "Clear or neutral lip balm, medicated lip care",
            "Neutral": "Natural lip balm, petroleum-free options"
        }
        
        # Beard care and grooming
        beard_care = {
            "Warm": "Warm brown beard oil, natural wood comb, keep edges sharp",
            "Cool": "Unscented beard balm, cool-toned beard dye if graying, clean lines",
            "Neutral": "Argan or jojoba beard oil, regular trimming, natural look"
        }
        
        # Face care
        face_care = {
            "Warm": "Matte finish products, charcoal face wash, anti-shine",
            "Cool": "Hydrating face wash, subtle highlighter for glow",
            "Neutral": "Balanced cleanser, light moisturizer"
        }
        
        return {
            "foundation_tip": skincare.get((skin_tone, undertone), f"SPF moisturizer with {undertone.lower()} undertone"),
            "lip_colors": [lip_care.get(undertone, "Natural lip balm")],
            "eye_makeup": beard_care.get(undertone, "Keep beard well-groomed with natural products"),
            "blush": face_care.get(undertone, "Regular face care routine")
        }
    
    def _get_accessory_recommendations(self, undertone: str, gender: str = "Woman", occasion: str = "casual", outfit_weight: str = "medium", outfit_color: str = "") -> dict:
        """Get accessory recommendations based on gender, undertone, occasion, and outfit color"""
        
        metals = {
            "Warm": "Gold or rose gold",
            "Cool": "Silver or platinum",
            "Neutral": "Both gold and silver work well"
        }
        
        # Get curated accessory items based on gender, undertone, occasion, and outfit color
        accessory_items = self._get_accessory_items(undertone, gender, occasion, outfit_weight, outfit_color)
        
        if gender == "Woman":
            return {
                "jewelry_metal": metals.get(undertone, "Mixed metals"),
                "jewelry_style": self._get_jewelry_style(occasion),
                "bag_color": self._get_bag_suggestion(occasion, undertone),
                "shoes": self._get_shoe_suggestion(occasion, undertone, gender),
                "curated_items": accessory_items
            }
        else:
            return {
                "jewelry_metal": metals.get(undertone, "Mixed metals"),
                "jewelry_style": "Minimal, classic pieces",
                "bag_color": self._get_bag_suggestion(occasion, undertone),
                "shoes": self._get_shoe_suggestion(occasion, undertone, gender),
                "curated_items": accessory_items
            }
    
    def _get_jewelry_style(self, occasion: str) -> str:
        """Get jewelry style based on occasion"""
        styles = {
            "casual": "Delicate chains, small studs, minimal rings",
            "formal": "Statement earrings, elegant pendant, classic bracelet",
            "business": "Subtle studs, thin chain, professional watch",
            "party": "Bold earrings, layered necklaces, statement rings",
            "date": "Romantic pendants, drop earrings, delicate bracelet",
            "traditional": "Jhumkas, temple jewelry, kundan sets",
            "wedding": "Heavy kundan, polki sets, maang tikka, choker"
        }
        return styles.get(occasion, "Classic pieces that complement your outfit")
    
    def _get_bag_suggestion(self, occasion: str, undertone: str) -> str:
        """Get bag color suggestion based on occasion"""
        if occasion in ["formal", "business"]:
            return "Black or nude structured bag"
        elif occasion in ["party", "date"]:
            return "Metallic gold or silver clutch" if undertone == "Warm" else "Silver or crystal clutch"
        elif occasion in ["traditional", "wedding"]:
            return "Embroidered potli or zari clutch"
        else:
            return "Tan, brown, or neutral tote"
    
    def _get_shoe_suggestion(self, occasion: str, undertone: str, gender: str) -> str:
        """Get shoe suggestion based on occasion, undertone, and gender"""
        
        # Determine shoe color tone based on undertone
        if undertone == "Warm":
            neutral_color = "tan, brown, or camel"
            metallic = "gold"
        elif undertone == "Cool":
            neutral_color = "black, gray, or taupe"
            metallic = "silver"
        else:
            neutral_color = "nude, beige, or brown"
            metallic = "rose gold"
        
        if gender == "Man":
            shoes = {
                "casual": f"White sneakers, {neutral_color} loafers, or canvas shoes",
                "formal": f"Black oxfords or {neutral_color} leather brogues",
                "business": f"Brown derbies, black monk straps, or {neutral_color} loafers",
                "party": f"Velvet loafers, sleek boots, or {neutral_color} Chelsea boots",
                "date": f"Clean {neutral_color} loafers or smart casual boots",
                "traditional": f"Embroidered mojaris, kolhapuris, or {neutral_color} juttis",
                "wedding": f"Golden mojaris, embroidered juttis, or formal {neutral_color} shoes"
            }
        else:
            shoes = {
                "casual": f"White sneakers, {neutral_color} ballet flats, or slip-on mules",
                "formal": f"Black stilettos, {neutral_color} pumps, or elegant kitten heels",
                "business": f"{neutral_color.title()} pumps, black flats, or low block heels",
                "party": f"{metallic.title()} strappy heels, embellished sandals, or statement stilettos",
                "date": f"Elegant {neutral_color} heels, dressy flats, or kitten heel mules",
                "traditional": f"{metallic.title()} embellished heels, kolhapuris, or {neutral_color} wedges",
                "wedding": f"Embellished {metallic} heels, bridal juttis, or statement stilettos"
            }
        return shoes.get(occasion, f"Neutral {neutral_color} shoes that complement your outfit")
    
    def _get_accessory_items(self, undertone: str, gender: str = "Woman", occasion: str = "casual", outfit_weight: str = "medium", outfit_color: str = "") -> list:
        """Get curated accessory items with images and links based on outfit color matching"""
        
        # Color mapping for complementary and matching accessories
        color_family = self._get_color_family(outfit_color)
        complementary = self._get_complementary_color(color_family)
        
        # ========== TYPE-SPECIFIC ACCESSORY IMAGES ==========
        # Using local SVG images for each accessory type
        type_images = {
            # Women's accessories
            "earrings": "/static/images/earrings.svg",
            "necklace": "/static/images/necklace.svg",
            "bag": "/static/images/bag.svg",
            "bangles": "/static/images/bangles.svg",
            "bracelet": "/static/images/bracelet.svg",
            # Men's accessories
            "watch": "/static/images/watch.svg",
            "belt": "/static/images/belt.svg",
            "tie": "/static/images/tie.svg",
            "wallet": "/static/images/wallet.svg",
            "cufflinks": "/static/images/cufflinks.svg",
            "pocket-square": "/static/images/pocket-square.svg",
        }
        
        women_accessories = {
            "red": [
                {"name": "Ruby Drop Earrings", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=red+ruby+earrings+women", "price_range": "₹400 - ₹1500", "occasions": ["party", "date", "wedding"]},
                {"name": "Red Beaded Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=red+beaded+necklace", "price_range": "₹350 - ₹1200", "occasions": ["casual", "party", "traditional"]},
                {"name": "Red Silk Clutch", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=red+clutch+bag+women", "price_range": "₹600 - ₹2000", "occasions": ["party", "wedding", "formal"]},
                {"name": "Red Bangles Set", "type": "bangles", "image": type_images["bangles"], "link": "https://www.amazon.in/s?k=red+bangles+set", "price_range": "₹250 - ₹800", "occasions": ["traditional", "wedding", "casual"]},
            ],
            "blue": [
                {"name": "Sapphire Blue Studs", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=blue+sapphire+earrings", "price_range": "₹500 - ₹2000", "occasions": ["formal", "business", "party"]},
                {"name": "Blue Pendant Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=blue+beaded+necklace+women", "price_range": "₹400 - ₹1500", "occasions": ["casual", "party", "date"]},
                {"name": "Navy Leather Handbag", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=navy+blue+handbag+women", "price_range": "₹800 - ₹3000", "occasions": ["formal", "business", "casual"]},
                {"name": "Blue Crystal Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=blue+crystal+bracelet", "price_range": "₹300 - ₹1000", "occasions": ["party", "casual", "date"]},
            ],
            "green": [
                {"name": "Emerald Drop Earrings", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=emerald+green+earrings", "price_range": "₹450 - ₹1800", "occasions": ["party", "wedding", "traditional"]},
                {"name": "Green Kundan Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=green+kundan+necklace", "price_range": "₹600 - ₹2500", "occasions": ["wedding", "traditional", "party"]},
                {"name": "Olive Green Tote", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=green+tote+bag+women", "price_range": "₹700 - ₹2000", "occasions": ["casual", "business", "formal"]},
                {"name": "Jade Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=green+jade+bracelet", "price_range": "₹400 - ₹1500", "occasions": ["casual", "traditional", "party"]},
            ],
            "pink": [
                {"name": "Rose Quartz Earrings", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=pink+rose+quartz+earrings", "price_range": "₹350 - ₹1200", "occasions": ["casual", "date", "party"]},
                {"name": "Pink Pearl Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=pink+pearl+necklace", "price_range": "₹500 - ₹2000", "occasions": ["party", "wedding", "formal"]},
                {"name": "Blush Pink Clutch", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=pink+clutch+bag", "price_range": "₹500 - ₹1800", "occasions": ["party", "wedding", "date"]},
                {"name": "Pink Crystal Bangles", "type": "bangles", "image": type_images["bangles"], "link": "https://www.amazon.in/s?k=pink+crystal+bangles", "price_range": "₹300 - ₹1000", "occasions": ["casual", "party", "traditional"]},
            ],
            "yellow": [
                {"name": "Citrine Earrings", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=yellow+citrine+earrings", "price_range": "₹400 - ₹1500", "occasions": ["casual", "party", "traditional"]},
                {"name": "Gold Pendant Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=yellow+beaded+necklace", "price_range": "₹350 - ₹1200", "occasions": ["casual", "party", "date"]},
                {"name": "Mustard Sling Bag", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=mustard+yellow+sling+bag", "price_range": "₹600 - ₹2000", "occasions": ["casual", "party", "formal"]},
                {"name": "Yellow Enamel Bangles", "type": "bangles", "image": type_images["bangles"], "link": "https://www.amazon.in/s?k=yellow+enamel+bangles", "price_range": "₹250 - ₹800", "occasions": ["casual", "traditional", "party"]},
            ],
            "purple": [
                {"name": "Amethyst Drop Earrings", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=purple+amethyst+earrings", "price_range": "₹450 - ₹1800", "occasions": ["party", "formal", "wedding"]},
                {"name": "Purple Stone Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=purple+stone+necklace", "price_range": "₹400 - ₹1500", "occasions": ["party", "date", "formal"]},
                {"name": "Violet Velvet Clutch", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=purple+velvet+clutch", "price_range": "₹600 - ₹2000", "occasions": ["party", "wedding", "formal"]},
                {"name": "Lavender Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=purple+crystal+bracelet", "price_range": "₹350 - ₹1200", "occasions": ["casual", "party", "date"]},
            ],
            "orange": [
                {"name": "Coral Earrings", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=coral+orange+earrings", "price_range": "₹350 - ₹1200", "occasions": ["casual", "party", "date"]},
                {"name": "Orange Bead Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=orange+bead+necklace", "price_range": "₹300 - ₹1000", "occasions": ["casual", "party", "traditional"]},
                {"name": "Tangerine Crossbody", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=orange+crossbody+bag", "price_range": "₹600 - ₹1800", "occasions": ["casual", "party", "formal"]},
                {"name": "Orange Lac Bangles", "type": "bangles", "image": type_images["bangles"], "link": "https://www.amazon.in/s?k=orange+lac+bangles", "price_range": "₹200 - ₹700", "occasions": ["traditional", "casual", "party"]},
            ],
            "black": [
                {"name": "Black Onyx Studs", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=black+onyx+earrings", "price_range": "₹400 - ₹1500", "occasions": ["formal", "party", "business"]},
                {"name": "Black Pearl Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=black+pearl+necklace", "price_range": "₹500 - ₹2000", "occasions": ["party", "formal", "date"]},
                {"name": "Black Leather Tote", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=black+leather+tote+women", "price_range": "₹800 - ₹3000", "occasions": ["business", "formal", "casual"]},
                {"name": "Black Diamond Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=black+diamond+bracelet", "price_range": "₹450 - ₹1800", "occasions": ["party", "formal", "date"]},
            ],
            "white": [
                {"name": "Pearl Drop Earrings", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=pearl+drop+earrings", "price_range": "₹400 - ₹1500", "occasions": ["wedding", "formal", "party"]},
                {"name": "White Pearl Choker", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=white+pearl+choker", "price_range": "₹500 - ₹2000", "occasions": ["wedding", "party", "formal"]},
                {"name": "White Leather Clutch", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=white+clutch+bag", "price_range": "₹600 - ₹2000", "occasions": ["party", "wedding", "formal"]},
                {"name": "Crystal Tennis Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=crystal+tennis+bracelet", "price_range": "₹500 - ₹2000", "occasions": ["party", "wedding", "formal"]},
            ],
            "gold": [
                {"name": "Traditional Jhumkas", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=gold+jhumka+earrings", "price_range": "₹500 - ₹2000", "occasions": ["traditional", "wedding", "party"]},
                {"name": "Gold Kundan Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=gold+kundan+necklace", "price_range": "₹800 - ₹3500", "occasions": ["wedding", "traditional", "party"]},
                {"name": "Gold Chain Clutch", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=gold+clutch+bag", "price_range": "₹700 - ₹2500", "occasions": ["party", "wedding", "formal"]},
                {"name": "Gold Bangles Set", "type": "bangles", "image": type_images["bangles"], "link": "https://www.amazon.in/s?k=gold+bangles+set", "price_range": "₹400 - ₹1500", "occasions": ["traditional", "wedding", "casual"]},
            ],
            "silver": [
                {"name": "Silver Oxidized Jhumkas", "type": "earrings", "image": type_images["earrings"], "link": "https://www.amazon.in/s?k=silver+oxidized+jhumka", "price_range": "₹300 - ₹1000", "occasions": ["traditional", "casual", "party"]},
                {"name": "Silver Chain Necklace", "type": "necklace", "image": type_images["necklace"], "link": "https://www.amazon.in/s?k=silver+chain+necklace+women", "price_range": "₹400 - ₹1500", "occasions": ["casual", "party", "formal"]},
                {"name": "Silver Metallic Clutch", "type": "bag", "image": type_images["bag"], "link": "https://www.amazon.in/s?k=silver+clutch+bag", "price_range": "₹600 - ₹2000", "occasions": ["party", "formal", "date"]},
                {"name": "Silver Cuff Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=silver+cuff+bracelet+women", "price_range": "₹350 - ₹1200", "occasions": ["party", "casual", "formal"]},
            ],
        }
        
        men_accessories = {
            "red": [
                {"name": "Red Dial Watch", "type": "watch", "image": type_images["watch"], "link": "https://www.amazon.in/s?k=red+dial+watch+men", "price_range": "₹1500 - ₹5000", "occasions": ["casual", "party"]},
                {"name": "Maroon Leather Belt", "type": "belt", "image": type_images["belt"], "link": "https://www.amazon.in/s?k=maroon+leather+belt+men", "price_range": "₹500 - ₹1500", "occasions": ["formal", "casual", "business"]},
                {"name": "Red Silk Pocket Square", "type": "pocket-square", "image": type_images["pocket-square"], "link": "https://www.amazon.in/s?k=red+pocket+square", "price_range": "₹200 - ₹800", "occasions": ["formal", "wedding", "party"]},
            ],
            "blue": [
                {"name": "Blue Chronograph", "type": "watch", "image": type_images["watch"], "link": "https://www.amazon.in/s?k=blue+dial+watch+men", "price_range": "₹2000 - ₹6000", "occasions": ["formal", "business", "casual"]},
                {"name": "Navy Blue Tie", "type": "tie", "image": type_images["tie"], "link": "https://www.amazon.in/s?k=navy+blue+tie+men", "price_range": "₹300 - ₹1000", "occasions": ["formal", "business", "wedding"]},
                {"name": "Blue Leather Wallet", "type": "wallet", "image": type_images["wallet"], "link": "https://www.amazon.in/s?k=blue+leather+wallet+men", "price_range": "₹500 - ₹2000", "occasions": ["casual", "formal", "business"]},
            ],
            "green": [
                {"name": "Green Dial Watch", "type": "watch", "image": type_images["watch"], "link": "https://www.amazon.in/s?k=green+dial+watch+men", "price_range": "₹1500 - ₹5000", "occasions": ["casual", "party"]},
                {"name": "Olive Belt", "type": "belt", "image": type_images["belt"], "link": "https://www.amazon.in/s?k=olive+green+belt+men", "price_range": "₹500 - ₹1500", "occasions": ["casual", "formal"]},
                {"name": "Green Silk Tie", "type": "tie", "image": type_images["tie"], "link": "https://www.amazon.in/s?k=green+silk+tie", "price_range": "₹400 - ₹1200", "occasions": ["formal", "party", "wedding"]},
            ],
            "black": [
                {"name": "Black Chronograph", "type": "watch", "image": type_images["watch"], "link": "https://www.amazon.in/s?k=black+chronograph+watch+men", "price_range": "₹2000 - ₹8000", "occasions": ["formal", "business", "party"]},
                {"name": "Black Leather Belt", "type": "belt", "image": type_images["belt"], "link": "https://www.amazon.in/s?k=black+leather+belt+men", "price_range": "₹500 - ₹2000", "occasions": ["formal", "casual", "business"]},
                {"name": "Black Cufflinks", "type": "cufflinks", "image": type_images["cufflinks"], "link": "https://www.amazon.in/s?k=black+cufflinks+men", "price_range": "₹400 - ₹1500", "occasions": ["formal", "business", "wedding"]},
            ],
            "gold": [
                {"name": "Gold Tone Watch", "type": "watch", "image": type_images["watch"], "link": "https://www.amazon.in/s?k=gold+watch+men", "price_range": "₹2000 - ₹8000", "occasions": ["formal", "wedding", "party"]},
                {"name": "Gold Cufflinks", "type": "cufflinks", "image": type_images["cufflinks"], "link": "https://www.amazon.in/s?k=gold+cufflinks+men", "price_range": "₹500 - ₹2000", "occasions": ["formal", "wedding", "business"]},
                {"name": "Gold Chain Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=gold+bracelet+men", "price_range": "₹800 - ₹3000", "occasions": ["party", "casual", "traditional"]},
            ],
            "silver": [
                {"name": "Silver Chronograph", "type": "watch", "image": type_images["watch"], "link": "https://www.amazon.in/s?k=silver+watch+men", "price_range": "₹1500 - ₹6000", "occasions": ["formal", "business", "casual"]},
                {"name": "Silver Cufflinks", "type": "cufflinks", "image": type_images["cufflinks"], "link": "https://www.amazon.in/s?k=silver+cufflinks+men", "price_range": "₹400 - ₹1500", "occasions": ["formal", "business", "wedding"]},
                {"name": "Silver Bracelet", "type": "bracelet", "image": type_images["bracelet"], "link": "https://www.amazon.in/s?k=silver+bracelet+men", "price_range": "₹600 - ₹2000", "occasions": ["casual", "party"]},
            ],
            "white": [
                {"name": "White Dial Watch", "type": "watch", "image": type_images["watch"], "link": "https://www.amazon.in/s?k=white+dial+watch+men", "price_range": "₹1500 - ₹5000", "occasions": ["formal", "business", "casual"]},
                {"name": "White Leather Belt", "type": "belt", "image": type_images["belt"], "link": "https://www.amazon.in/s?k=white+leather+belt+men", "price_range": "₹500 - ₹1500", "occasions": ["casual", "party"]},
                {"name": "Pearl Cufflinks", "type": "cufflinks", "image": type_images["cufflinks"], "link": "https://www.amazon.in/s?k=pearl+cufflinks+men", "price_range": "₹500 - ₹1800", "occasions": ["formal", "wedding"]},
            ],
        }
        
        # Select accessory database based on gender
        accessory_db = men_accessories if gender == "Man" else women_accessories
        
        # Build result list with matching + complementary colors
        result = []
        
        # First add matching color accessories
        if color_family in accessory_db:
            matching_items = accessory_db[color_family]
            for item in matching_items:
                item_copy = item.copy()
                item_copy["color_match"] = "matching"
                item_copy["color_note"] = f"Matches your {color_family} outfit"
                result.append(item_copy)
        
        # Then add complementary color accessories
        if complementary in accessory_db and complementary != color_family:
            comp_items = accessory_db[complementary]
            for item in comp_items[:2]:  # Add 2 complementary items
                item_copy = item.copy()
                item_copy["color_match"] = "complementary"
                item_copy["color_note"] = f"Complementary {complementary} pairs beautifully with {color_family}"
                result.append(item_copy)
        
        # Add neutral metallic based on undertone if not enough items
        if len(result) < 4:
            metallic = "gold" if undertone == "Warm" else "silver"
            if metallic in accessory_db:
                for item in accessory_db[metallic][:2]:
                    item_copy = item.copy()
                    item_copy["color_match"] = "neutral"
                    item_copy["color_note"] = f"{metallic.capitalize()} complements your {undertone.lower()} undertone"
                    result.append(item_copy)
        
        # Filter by occasion if specific
        if occasion in ["casual", "formal", "business", "party", "date", "traditional", "wedding"]:
            filtered = [item for item in result if occasion in item.get("occasions", ["casual"])]
            if len(filtered) >= 3:
                return filtered[:5]
        
        return result[:5]
    
    def _get_color_family(self, color_name: str) -> str:
        """Map color name to basic color family"""
        color_name = color_name.lower() if color_name else ""
        
        color_mappings = {
            "red": ["red", "crimson", "scarlet", "maroon", "burgundy", "ruby", "cherry", "wine"],
            "blue": ["blue", "navy", "azure", "cobalt", "indigo", "royal", "sapphire", "teal", "cyan", "turquoise"],
            "green": ["green", "olive", "emerald", "lime", "mint", "sage", "forest", "jade", "teal"],
            "pink": ["pink", "rose", "blush", "fuchsia", "magenta", "coral", "salmon", "peach"],
            "yellow": ["yellow", "gold", "mustard", "lemon", "amber", "honey", "canary"],
            "purple": ["purple", "violet", "lavender", "plum", "mauve", "lilac", "amethyst", "grape"],
            "orange": ["orange", "tangerine", "coral", "peach", "apricot", "terracotta", "rust"],
            "black": ["black", "charcoal", "ebony", "onyx", "jet"],
            "white": ["white", "ivory", "cream", "pearl", "snow", "off-white", "beige", "ecru"],
            "gold": ["gold", "golden", "metallic gold", "brass", "bronze"],
            "silver": ["silver", "metallic silver", "chrome", "platinum", "gray", "grey"],
        }
        
        for family, variants in color_mappings.items():
            if any(variant in color_name for variant in variants):
                return family
        
        return "gold"  # Default to gold/neutral
    
    def _get_complementary_color(self, color_family: str) -> str:
        """Get complementary color based on color wheel"""
        complementary_map = {
            "red": "green",
            "blue": "orange",
            "green": "red",
            "yellow": "purple",
            "purple": "yellow",
            "orange": "blue",
            "pink": "green",
            "black": "gold",
            "white": "silver",
            "gold": "purple",
            "silver": "blue",
        }
        return complementary_map.get(color_family, "gold")
    
    def _get_better_colors(self, skin_tone: str, undertone: str) -> list:
        """Get recommended outfit colors"""
        
        colors = {
            ("Fair", "Warm"): ["Coral", "Cream", "Warm brown", "Peach", "Gold"],
            ("Fair", "Cool"): ["Navy", "Rose", "Lavender", "Silver gray", "Burgundy"],
            ("Fair", "Neutral"): ["Dusty pink", "Sage green", "Soft navy", "Taupe"],
            ("Medium", "Warm"): ["Terracotta", "Olive", "Gold", "Warm red", "Orange"],
            ("Medium", "Cool"): ["Royal blue", "Emerald", "Purple", "Fuchsia", "Silver"],
            ("Medium", "Neutral"): ["Teal", "Coral", "Jade", "Dusty rose"],
            ("Deep", "Warm"): ["Orange", "Gold", "Coral", "Warm white", "Yellow"],
            ("Deep", "Cool"): ["Fuchsia", "Royal blue", "Emerald", "White", "Silver"],
            ("Deep", "Neutral"): ["Bright coral", "Teal", "White", "Jade", "Purple"]
        }
        
        key = (skin_tone, undertone)
        return colors.get(key, ["Navy", "White", "Black", "Gray", "Beige"])
    
    def _get_color_combos(self, skin_tone: str, undertone: str) -> list:
        """Get outfit color combinations"""
        
        if undertone == "Warm":
            return [
                "Cream top + terracotta bottom",
                "Olive pants + coral blouse",
                "Gold jewelry + warm brown outfit"
            ]
        elif undertone == "Cool":
            return [
                "Navy blazer + white shirt",
                "Silver jewelry + emerald dress",
                "Gray pants + berry top"
            ]
        else:
            return [
                "Teal top + cream pants",
                "Navy + dusty rose",
                "Jade green + soft gray"
            ]
    
    def _get_hairstyle(self, occasion: str, gender: str = "Woman") -> str:
        """Get hairstyle suggestion based on occasion and gender"""
        
        if gender == "Man":
            styles = {
                "casual": "Textured, natural style or clean fade",
                "formal": "Slicked back or neat side part",
                "business": "Professional cut, well-groomed",
                "party": "Styled with product, textured look",
                "traditional": "Classic, well-oiled style",
                "wedding": "Formal, well-groomed with neat edges"
            }
        else:
            styles = {
                "casual": "Soft waves or natural texture",
                "formal": "Elegant updo or sleek blowout",
                "business": "Polished and professional - neat bun or styled down",
                "party": "Glamorous curls or chic updo",
                "date": "Romantic soft curls or half-up style",
                "traditional": "Classic bun, braided style, or elegant updo",
                "wedding": "Elaborate updo with accessories or flowing curls"
            }
        
        return styles.get(occasion.lower(), "Styled natural texture")
    
    def _get_hair_color_tip(self, skin_tone: str, undertone: str) -> str:
        """Get hair color recommendation"""
        
        if undertone == "Warm":
            return "Warm tones like golden blonde, auburn, or warm brown complement your skin"
        elif undertone == "Cool":
            return "Cool tones like ash blonde, cool brown, or burgundy suit your undertones"
        else:
            return "Neutral to slightly warm shades work best for your balanced undertones"
    
    def _get_pattern_suggestion(self, occasion: str) -> str:
        """Get pattern suggestions"""
        
        if occasion.lower() in ["formal", "business"]:
            return "Subtle patterns like pinstripes or small prints"
        elif occasion.lower() in ["casual", "party"]:
            return "Florals, geometric prints, or bold patterns"
        else:
            return "Choose patterns that complement your personality"
    
    def _get_overall_tip(self, skin_tone: str, undertone: str, harmony_score: int, gender: str = "Woman") -> str:
        """Generate overall styling tip"""
        
        base_tip = ""
        if harmony_score >= 80:
            base_tip = f"Your color choice is excellent! As someone with {skin_tone.lower()} skin and {undertone.lower()} undertones, continue choosing colors from this family."
        elif harmony_score >= 60:
            base_tip = f"Good color choice! To enhance your {skin_tone.lower()} skin with {undertone.lower()} undertones, try accessorizing with complementary colors."
        else:
            base_tip = f"Consider trying colors that better complement your {skin_tone.lower()} skin with {undertone.lower()} undertones for a more flattering look."
        
        if gender == "Man":
            base_tip += " Focus on well-fitted clothing and minimal, quality accessories for a polished look."
        else:
            base_tip += " Don't forget to coordinate your jewelry metal with your outfit palette!"
        
        return base_tip

    def _get_outfit_recommendations(self, occasion: str, gender: str, undertone: str, outfit_weight: str) -> list:
        """Get occasion-specific outfit recommendations with cultural awareness"""
        
        # ========== WOMEN'S OUTFITS BY OCCASION ==========
        women_outfits = {
            "casual": [
                {"outfit": "Cotton Kurti with Jeans", "description": "Comfortable Indo-western look", "colors": "Pastel shades, earthy tones"},
                {"outfit": "A-line Dress", "description": "Easy breezy casual wear", "colors": "Florals, solid pastels"},
                {"outfit": "Palazzo with Crop Top", "description": "Trendy casual style", "colors": "Complementary contrasts"},
                {"outfit": "Denim with Embroidered Top", "description": "Chic everyday look", "colors": "Blue denim + colorful top"}
            ],
            "formal": [
                {"outfit": "Tailored Blazer with Trousers", "description": "Power dressing", "colors": "Navy, black, charcoal"},
                {"outfit": "Pencil Skirt with Blouse", "description": "Classic formal", "colors": "Neutral tones"},
                {"outfit": "Formal Saree", "description": "Elegant formal Indian wear", "colors": "Solid silks, subtle prints"},
                {"outfit": "Midi Dress with Blazer", "description": "Modern formal look", "colors": "Muted sophisticated shades"}
            ],
            "business": [
                {"outfit": "Formal Churidar Suit", "description": "Professional Indian wear", "colors": "Subtle prints, solid colors"},
                {"outfit": "Structured Kurta with Pants", "description": "Indo-western office wear", "colors": "Muted tones, minimal prints"},
                {"outfit": "Tailored Pantsuit", "description": "Corporate power look", "colors": "Navy, grey, black"},
                {"outfit": "Cotton Saree", "description": "Traditional yet professional", "colors": "Handloom, cotton prints"}
            ],
            "party": [
                {"outfit": "Sequin Saree", "description": "Glamorous party wear", "colors": "Gold, silver, jewel tones"},
                {"outfit": "Designer Lehenga", "description": "Statement party look", "colors": "Bold, vibrant shades"},
                {"outfit": "Cocktail Gown", "description": "Western party glamour", "colors": "Black, red, metallics"},
                {"outfit": "Sharara Set", "description": "Trendy fusion party wear", "colors": "Bright, festive colors"},
                {"outfit": "Anarkali Suit", "description": "Elegant party Indian wear", "colors": "Rich, deep colors"}
            ],
            "date": [
                {"outfit": "Flowy Midi Dress", "description": "Romantic and feminine", "colors": "Soft pinks, florals"},
                {"outfit": "Kurti with Dhoti Pants", "description": "Stylish Indo-western", "colors": "Pastels, romantic shades"},
                {"outfit": "Off-shoulder Top with Skirt", "description": "Flirty modern look", "colors": "Soft, romantic colors"},
                {"outfit": "Elegant Saree", "description": "Traditional romantic", "colors": "Soft silks, chiffons"}
            ],
            "traditional": [
                {"outfit": "Silk Saree", "description": "Classic traditional elegance", "colors": "Rich silks, temple borders"},
                {"outfit": "Anarkali Suit", "description": "Graceful Indian wear", "colors": "Deep reds, greens, purples"},
                {"outfit": "Pattu Pavadai / Half Saree", "description": "South Indian traditional", "colors": "Bright, auspicious colors"},
                {"outfit": "Bandhani Saree", "description": "Traditional tie-dye", "colors": "Red, yellow, traditional hues"},
                {"outfit": "Salwar Kameez Set", "description": "Comfortable traditional", "colors": "Printed, embroidered"}
            ],
            "wedding": [
                {"outfit": "Bridal Lehenga", "description": "Grand wedding attire", "colors": "Red, maroon, gold, pink"},
                {"outfit": "Banarasi Silk Saree", "description": "Classic wedding elegance", "colors": "Rich reds, golds, deep colors"},
                {"outfit": "Designer Anarkali", "description": "Elegant wedding guest", "colors": "Jewel tones, pastels"},
                {"outfit": "Kanjeevaram Saree", "description": "South Indian wedding glory", "colors": "Temple colors, zari work"},
                {"outfit": "Sharara Lehenga", "description": "Modern bridal fusion", "colors": "Blush, mint, coral, gold"},
                {"outfit": "Gharara Set", "description": "Royal wedding look", "colors": "Royal blue, emerald, maroon"}
            ]
        }
        
        # ========== MEN'S OUTFITS BY OCCASION ==========
        men_outfits = {
            "casual": [
                {"outfit": "Polo Shirt with Chinos", "description": "Smart casual look", "colors": "Earth tones, pastels"},
                {"outfit": "Kurta with Jeans", "description": "Indo-western casual", "colors": "White, light colors"},
                {"outfit": "Linen Shirt with Shorts", "description": "Relaxed weekend wear", "colors": "Light, breathable shades"},
                {"outfit": "T-shirt with Joggers", "description": "Athleisure style", "colors": "Neutrals, monochromes"}
            ],
            "formal": [
                {"outfit": "Three-piece Suit", "description": "Classic formal elegance", "colors": "Navy, charcoal, black"},
                {"outfit": "Formal Kurta Pajama", "description": "Indian formal wear", "colors": "Cream, white, pastels"},
                {"outfit": "Blazer with Dress Shirt", "description": "Semi-formal smart", "colors": "Dark, sophisticated tones"},
                {"outfit": "Bandhgala Suit", "description": "Indian formal jacket", "colors": "Black, navy, maroon"}
            ],
            "business": [
                {"outfit": "Business Suit", "description": "Corporate professional", "colors": "Navy, grey, charcoal"},
                {"outfit": "Dress Shirt with Trousers", "description": "Office essential", "colors": "Light shirts, dark trousers"},
                {"outfit": "Nehru Jacket with Shirt", "description": "Indian business style", "colors": "Neutral, subtle colors"},
                {"outfit": "Blazer with Chinos", "description": "Smart business casual", "colors": "Earth tones, blues"}
            ],
            "party": [
                {"outfit": "Designer Kurta with Jacket", "description": "Stylish party Indian", "colors": "Bold, vibrant shades"},
                {"outfit": "Velvet Blazer with Shirt", "description": "Party statement piece", "colors": "Deep jewel tones"},
                {"outfit": "Indo-western Sherwani", "description": "Fusion party look", "colors": "Black, maroon, navy"},
                {"outfit": "Printed Shirt with Pants", "description": "Trendy party style", "colors": "Prints, patterns"}
            ],
            "date": [
                {"outfit": "Smart Casual Shirt with Jeans", "description": "Relaxed yet put-together", "colors": "Soft, approachable colors"},
                {"outfit": "Kurta with Churidar", "description": "Traditional charm", "colors": "Light, romantic shades"},
                {"outfit": "Blazer with T-shirt", "description": "Effortlessly cool", "colors": "Neutral, stylish tones"},
                {"outfit": "Linen Shirt with Trousers", "description": "Breezy date look", "colors": "Pastels, whites"}
            ],
            "traditional": [
                {"outfit": "Silk Kurta Pajama", "description": "Classic Indian traditional", "colors": "Cream, gold, maroon"},
                {"outfit": "Dhoti Kurta", "description": "Traditional South Indian", "colors": "White with gold border"},
                {"outfit": "Mundu with Shirt", "description": "Kerala traditional", "colors": "White/cream mundu, colored shirt"},
                {"outfit": "Pathani Suit", "description": "North Indian traditional", "colors": "White, cream, pastels"},
                {"outfit": "Angavastram with Kurta", "description": "Temple/pooja attire", "colors": "White, saffron, traditional"}
            ],
            "wedding": [
                {"outfit": "Designer Sherwani", "description": "Grand wedding attire", "colors": "Maroon, gold, ivory, navy"},
                {"outfit": "Silk Kurta with Churidar", "description": "Elegant wedding guest", "colors": "Rich pastels, jewel tones"},
                {"outfit": "Bandhgala with Dhoti", "description": "Royal Indian look", "colors": "Black, maroon, gold"},
                {"outfit": "Jodhpuri Suit", "description": "Regal wedding style", "colors": "Deep colors, gold accents"},
                {"outfit": "Achkan Sherwani", "description": "Classic groom/guest wear", "colors": "Ivory, gold, maroon, navy"},
                {"outfit": "Mundu with Jubba", "description": "South Indian wedding", "colors": "White/gold mundu, silk jubba"}
            ]
        }
        
        # Select outfits based on gender
        outfits = women_outfits if gender == "Woman" else men_outfits
        
        # Get occasion-specific outfits
        occasion_key = occasion.lower() if occasion.lower() in outfits else "casual"
        selected_outfits = outfits[occasion_key]
        
        # Add color suggestions based on undertone
        for outfit in selected_outfits:
            if undertone == "Warm":
                outfit["recommended_colors"] = "Gold accents, warm reds, terracotta, coral, warm browns"
            elif undertone == "Cool":
                outfit["recommended_colors"] = "Silver accents, cool pinks, blues, emerald, plum"
            else:
                outfit["recommended_colors"] = "Both warm and cool tones work - try jewel tones"
        
        return selected_outfits
