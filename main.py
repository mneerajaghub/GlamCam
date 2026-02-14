"""
AI Virtual Stylist - Main Application
=====================================
A hybrid AI system combining Computer Vision and Gemini Nano
for personalized fashion styling recommendations.
"""

import os
import io
import json
import base64
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from modules.skin_analyzer import SkinAnalyzer
from modules.outfit_analyzer import OutfitAnalyzer
from modules.harmony_engine import HarmonyEngine
from modules.stylist_ai import StylistAI

# Initialize FastAPI app
app = FastAPI(
    title="AI Virtual Stylist",
    description="Personalized styling recommendations using CV + Gemini Nano",
    version="1.0.0"
)

# Setup static files and templates
script_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(script_dir, "static")
templates_dir = os.path.join(script_dir, "templates")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Initialize modules
skin_analyzer = SkinAnalyzer()
outfit_analyzer = OutfitAnalyzer()
harmony_engine = HarmonyEngine()
stylist_ai = StylistAI()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_style(
    selfie: UploadFile = File(...),
    outfit: UploadFile = File(...),
    occasion: str = Form("casual"),
    outfit_weight: str = Form("medium")
):
    """
    Main analysis endpoint
    - Analyzes selfie for skin tone
    - Analyzes outfit for dominant color
    - Calculates harmony score
    - Generates AI styling recommendations
    """
    try:
        # Read images
        selfie_bytes = await selfie.read()
        outfit_bytes = await outfit.read()
        
        # Step 1: Analyze skin tone
        print("🔍 Analyzing skin tone...")
        skin_result = skin_analyzer.analyze(selfie_bytes)
        
        if not skin_result["success"]:
            return JSONResponse(
                status_code=400,
                content={"error": skin_result.get("error", "Failed to analyze skin tone")}
            )
        
        # Step 2: Analyze outfit color
        print("👗 Analyzing outfit color...")
        outfit_result = outfit_analyzer.analyze(outfit_bytes)
        
        if not outfit_result["success"]:
            return JSONResponse(
                status_code=400,
                content={"error": outfit_result.get("error", "Failed to analyze outfit")}
            )
        
        # Step 3: Calculate harmony score
        print("🎨 Calculating harmony score...")
        harmony_result = harmony_engine.calculate_harmony(
            skin_tone=skin_result["skin_tone"],
            undertone=skin_result["undertone"],
            outfit_color=outfit_result["dominant_color_name"],
            outfit_rgb=outfit_result["dominant_color_rgb"],
            season=skin_result.get("season"),
            color_family=outfit_result.get("color_family"),
            color_temperature=outfit_result.get("color_temperature"),
            season_affinity=outfit_result.get("season_affinity")
        )
        
        # Step 4: Generate AI recommendations
        print("✨ Generating styling recommendations...")
        
        # Extract gender from DeepFace analysis
        deepface_data = skin_result.get("deepface", {})
        detected_gender = deepface_data.get("gender", "Woman") if deepface_data else "Woman"
        print(f"👤 Detected gender: {detected_gender}")
        
        styling_result = await stylist_ai.generate_recommendations(
            skin_tone=skin_result["skin_tone"],
            undertone=skin_result["undertone"],
            outfit_color=outfit_result["dominant_color_name"],
            harmony_score=harmony_result["score"],
            occasion=occasion,
            outfit_weight=outfit_weight,
            gender=detected_gender
        )
        
        # Compile results
        result = {
            "success": True,
            "skin_analysis": {
                "season": skin_result.get("season", "Unknown"),
                "season_description": skin_result.get("season_description", ""),
                "skin_tone": skin_result["skin_tone"],
                "undertone": skin_result["undertone"],
                "color_dimensions": skin_result.get("color_dimensions", {}),
                "confidence": skin_result["confidence"],
                "rgb_values": skin_result["rgb_values"],
                "monk_scale": skin_result.get("monk_scale"),
                "deepface": skin_result.get("deepface"),  # Gender + race analysis
                "detected_gender": detected_gender
            },
            "outfit_analysis": {
                "dominant_color": outfit_result["dominant_color_name"],
                "color_rgb": outfit_result["dominant_color_rgb"],
                "color_hex": outfit_result["dominant_color_hex"],
                "color_family": outfit_result.get("color_family", "unknown"),
                "color_temperature": outfit_result.get("color_temperature", "neutral"),
                "season_affinity": outfit_result.get("season_affinity", []),
                "color_properties": outfit_result.get("color_properties", {}),
                "match_confidence": outfit_result.get("match_confidence", 0)
            },
            "harmony": {
                "score": harmony_result["score"],
                "rating": harmony_result["rating"],
                "explanation": harmony_result["explanation"]
            },
            "recommendations": styling_result,
            "context": {
                "occasion": occasion,
                "outfit_weight": outfit_weight
            }
        }
        
        print("✅ Analysis complete!")
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Analysis failed: {str(e)}"}
        )


@app.post("/analyze-skin-only")
async def analyze_skin_only(selfie: UploadFile = File(...)):
    """Analyze only skin tone from selfie"""
    try:
        selfie_bytes = await selfie.read()
        result = skin_analyzer.analyze(selfie_bytes)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/analyze-outfit-only")
async def analyze_outfit_only(outfit: UploadFile = File(...)):
    """Analyze only outfit color"""
    try:
        outfit_bytes = await outfit.read()
        result = outfit_analyzer.analyze(outfit_bytes)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Virtual Stylist"}


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("💄 AI Virtual Stylist - Starting Server")
    print("=" * 60)
    print("\n🌐 Open http://localhost:8000 in your browser\n")
    
    # Read port from environment variable (for Render deployment)
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
