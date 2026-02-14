# 💄 GlamCam - AI Virtual Stylist

An AI-powered virtual styling assistant that combines Computer Vision and Google Gemini to provide personalized fashion recommendations based on your skin tone and outfit colors.

## ✨ Features

- **🧑 Skin Tone Analysis**: Uses MediaPipe face mesh to detect skin regions and classify skin tone (Fair to Deep) with undertone detection (Warm/Cool/Neutral)
- **👗 Outfit Color Extraction**: K-means clustering to identify dominant colors in clothing images
- **🎨 Color Harmony Scoring**: Rule-based compatibility scoring (0-100%) between skin tone and outfit colors
- **💄 AI Styling Recommendations**: Gemini-powered suggestions for:
  - Makeup (foundation, lips, eyes, blush)
  - Hairstyles and hair color
  - Accessories (jewelry, bags, shoes)
  - Alternative outfit colors and combinations

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Computer Vision**: OpenCV, MediaPipe
- **Color Analysis**: scikit-learn (K-means), webcolors
- **AI**: Google Gemini 1.5 Flash
- **Frontend**: HTML5, CSS3, JavaScript

## 📦 Installation

1. **Create virtual environment** (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Gemini API key** (optional but recommended):
```bash
set GEMINI_API_KEY=your_api_key_here  # Windows
# or
export GEMINI_API_KEY=your_api_key_here  # Mac/Linux
```

Get your free API key at: https://makersuite.google.com/app/apikey

## 🚀 Running the App

```bash
python main.py
```

Then open **http://localhost:8000** in your browser.

## 📸 How to Use

1. **Upload a Selfie**: Clear face photo for skin tone analysis
2. **Upload an Outfit**: Photo of the clothing you want to analyze
3. **Select Occasion**: Choose the context (casual, formal, business, party, date)
4. **Select Season/Weight**: Light, medium, or heavy clothing
5. **Click Analyze**: Get your personalized style report!

## 🧬 How It Works

### Skin Tone Detection
1. MediaPipe Face Mesh detects 478 facial landmarks
2. Extracts pixels from cheek and forehead regions
3. Calculates ITA (Individual Typology Angle) for skin tone classification
4. Analyzes RGB ratios for undertone detection

### Color Extraction
1. Preprocesses outfit image to remove background noise
2. Applies K-means clustering with 5 clusters
3. Returns dominant color with percentage and color name

### Harmony Calculation
1. Uses color theory rules mapped to skin tone + undertone combinations
2. Checks outfit color against best/good/avoid lists
3. Adjusts score based on saturation and contrast
4. Generates explanation and alternatives

### AI Recommendations
1. Compiles analysis into structured prompt
2. Sends to Gemini API for personalized suggestions
3. Falls back to rule-based recommendations if API unavailable

## 📁 Project Structure

```
GlamCam/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── modules/
│   ├── __init__.py
│   ├── skin_analyzer.py   # Skin tone detection
│   ├── outfit_analyzer.py # Color extraction
│   ├── harmony_engine.py  # Compatibility scoring
│   └── stylist_ai.py      # Gemini integration
├── templates/
│   └── index.html         # Web UI template
└── static/
    ├── style.css          # Styling
    └── script.js          # Frontend logic
```

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/analyze` | POST | Full style analysis |
| `/analyze-skin-only` | POST | Only skin analysis |
| `/analyze-outfit-only` | POST | Only outfit analysis |
| `/health` | GET | Health check |

## 🔧 Configuration

The app works with or without a Gemini API key:
- **With API key**: Full AI-powered recommendations
- **Without API key**: Rule-based fallback recommendations

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Acknowledgments

- MediaPipe for face mesh detection
- Google Gemini for AI recommendations
- Color theory resources for harmony rules
