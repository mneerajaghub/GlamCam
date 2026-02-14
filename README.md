# GlamCam — AI Virtual Stylist with Computer Vision & Gemini

## Project Description

GlamCam is a real-time AI-powered virtual styling assistant that analyzes a user's selfie and outfit image using Computer Vision, Color Science, and Google Gemini AI.

It provides:

- Personalized makeup recommendations  
- Outfit harmony scoring  
- Accessories suggestions  
- AI-powered virtual try-on preview  

The system combines:

- 12-Season Color Analysis  
- Monk Skin Tone Scale mapping  
- CIE Delta E 2000 perceptual color science  
- Gemini multimodal AI  

Built for TinkHerHack 2026.

---

## Live Demo

**Demo Video:**  
https://youtu.be/HiwQNv-nhj8 

---

## Features

### Computer Vision Engine

- 12-Season Color Analysis (Light Spring → Bright Winter)
- Monk Skin Tone Scale mapping (MST-1 to MST-10)
- MediaPipe 478 facial landmark detection
- Dominant outfit color extraction using K-Means clustering

### Color Science

- CIE Delta E 2000 harmony scoring
- Warm / Cool undertone detection
- Outfit temperature matching
- Harmony score (0–100) with semantic rating

### AI-Powered Styling

- Gemini 2.0 Flash for contextual styling advice
- Occasion-aware recommendations (casual, formal, party, business, date)
- Structured AI prompting with fallback rule engine

### Virtual Try-On

- Gemini image generation for photorealistic preview
- MediaPipe-based fallback virtual makeup overlay
- Real-time processing pipeline

---

## Tech Stack

### Backend
- Python 3.13
- FastAPI
- Uvicorn

### Computer Vision
- OpenCV
- MediaPipe Face Mesh

### Machine Learning
- DeepFace
- stone (Monk Skin Tone Scale)

### Color Science
- colormath (CIE Delta E 2000)
- ColorThief
- scikit-learn (K-Means)

### AI
- Google Gemini 2.0 Flash
- Gemini Image Generation API

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript

### Deployment
- Render / Railway / GCP

---

## Architecture

```
User Uploads Images
        ↓
FastAPI Backend
        ↓
Skin Analyzer (MediaPipe + DeepFace)
        ↓
Outfit Analyzer (ColorThief + KMeans)
        ↓
Harmony Engine (CIE Delta E 2000)
        ↓
Gemini AI Stylist
        ↓
Virtual Try-On Generator
        ↓
JSON Response to Frontend
```

Detailed diagrams available in `docs/architecture.md`

---

## Project Structure

```
glamcam/
│
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── modules/
│   ├── skin_analyzer.py
│   ├── outfit_analyzer.py
│   ├── harmony_engine.py
│   ├── stylist_ai.py
│   └── image_generator.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   ├── script.js
│   └── images/
│
└── docs/
    ├── architecture.md
    └── screenshots/
```

- Lowercase folder names  
- No spaces in filenames  
- Modular backend structure  
- No single giant file  

---

## Installation

### Prerequisites

- Python 3.13 or higher
- pip package manager
- Git
- 2GB RAM minimum (4GB recommended for ML models)

### Clone the Repository

```bash
git clone https://github.com/yourusername/GlamCam.git
cd GlamCam
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your Gemini API key to `.env`:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

**Get your free Gemini API key**: https://aistudio.google.com/app/apikey

### Run the Application

```bash
python main.py
```

The server will start at `http://localhost:8000`

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```




---

## API Documentation

### Endpoints

#### GET /
Main web interface

#### POST /analyze
Performs full skin + outfit analysis

Form fields:
- `selfie` (image file)
- `outfit` (image file)
- `occasion` (string)
- `outfit_weight` (light / medium / heavy)

#### POST /generate-look
Generates virtual try-on preview

#### POST /analyze-skin-only
Skin tone analysis only

#### POST /analyze-outfit-only
Outfit color analysis only

#### GET /health
Health check endpoint
```

### Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  **Nandhana S** - Full Stack Developer, Computer Vision Engineer
- **Neeraja Manohar** - AI/ML Engineer, Color Science Specialistt_outfit.jpg" \
  -F "occasion=casual" \
  -F "outfit_weight=medium"
```

### Example Response

```json
{
  "skin_analysis": {
    "tone": "Medium",
    "undertone": "Warm",
    "season": "Warm Autumn",
    "mst_value": 5,
    "ita_angle": 41.2,
    "recommendations": ["Earth tones", "Olive green", "Warm browns"]
  },
  "outfit_analysis": {
    "dominant_color": "Navy Blue",
    "color_family": "Blue",
    "temperature": "Cool",
    "outfit_colors": [
      {"name": "Navy", "hex": "#000080", "rgb": [0, 0, 128]},
      {"name": "White", "hex": "#FFFFFF", "rgb": [255, 255, 255]}
    ]
  },
  "harmony_score": 78,
  "harmony_rating": "Good",
  "ai_recommendations": {
    "styling_tips": ["Pair with warm accessories", "Add gold jewelry"],
    "makeup_suggestions": ["Warm bronze eyeshadow", "Coral blush"],
    "accessories": ["Gold hoop earrings", "Brown leather bag"],
    "colors_to_try": ["Olive", "Terracotta", "Cream"],
    "colors_to_avoid": ["Icy pastels", "Pure black"]
  }
}

---

## Team Members

- Nandhana S 
- Neeraja Manohar  

---

## AI Tools Used

- Google Gemini 2.0 Flash  
- Gemini Image Generation API  
- DeepFace  
- MediaPipe  
- OpenCV  

---

## Root Files Checklist

- README.md  
- LICENSE  
- .gitignore  
- requirements.txt  

---

## Deployment Checklist

- HTTPS live link  
- No runtime errors  
- Environment variables secured  
- Production-ready FastAPI server  

---

## License

This project is licensed under the MIT License.  
See `LICENSE` file for details.