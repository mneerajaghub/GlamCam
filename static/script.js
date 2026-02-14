/**
 * GlamCam — Clean & Chic JavaScript
 */

// DOM Elements
const analyzeForm = document.getElementById('analyzeForm');
const selfieInput = document.getElementById('selfieInput');
const outfitInput = document.getElementById('outfitInput');
const selfiePreview = document.getElementById('selfiePreview');
const outfitPreview = document.getElementById('outfitPreview');
const selfieArea = document.getElementById('selfieArea');
const outfitArea = document.getElementById('outfitArea');
const analyzeBtn = document.getElementById('analyzeBtn');

const uploadSection = document.getElementById('uploadSection');
const loadingState = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');

// Loading steps
const steps = ['step1', 'step2', 'step3', 'step4'];

// ============================================
// File Upload Handling
// ============================================

function handleFileSelect(input, preview, area) {
    input.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                preview.src = event.target.result;
                area.classList.add('has-file');
            };
            reader.readAsDataURL(file);
        }
    });
}

// Initialize file handlers
handleFileSelect(selfieInput, selfiePreview, selfieArea);
handleFileSelect(outfitInput, outfitPreview, outfitArea);

// Drag and drop enhancement
[selfieArea, outfitArea].forEach(area => {
    area.addEventListener('dragover', (e) => {
        e.preventDefault();
        area.classList.add('dragover');
    });
    
    area.addEventListener('dragleave', () => {
        area.classList.remove('dragover');
    });
    
    area.addEventListener('drop', (e) => {
        area.classList.remove('dragover');
    });
});

// ============================================
// Loading Animation
// ============================================

function showLoading() {
    uploadSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    loadingState.classList.remove('hidden');
    
    // Animate steps
    let currentStep = 0;
    const stepInterval = setInterval(() => {
        if (currentStep > 0) {
            document.getElementById(steps[currentStep - 1]).classList.remove('active');
            document.getElementById(steps[currentStep - 1]).classList.add('done');
        }
        if (currentStep < steps.length) {
            document.getElementById(steps[currentStep]).classList.add('active');
            currentStep++;
        } else {
            clearInterval(stepInterval);
        }
    }, 800);
}

function hideLoading() {
    loadingState.classList.add('hidden');
    // Reset steps
    steps.forEach(step => {
        const el = document.getElementById(step);
        el.classList.remove('active', 'done');
    });
}

// ============================================
// Error Handling
// ============================================

function showError(message) {
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
    
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

// ============================================
// Form Submission
// ============================================

analyzeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(analyzeForm);
    
    // Validate files
    if (!selfieInput.files[0] || !outfitInput.files[0]) {
        showError('Please upload both a selfie and an outfit image');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }
        
        const data = await response.json();
        hideLoading();
        displayResults(data);
        
    } catch (error) {
        hideLoading();
        uploadSection.classList.remove('hidden');
        showError(error.message || 'An error occurred during analysis');
    }
});

// ============================================
// Display Results
// ============================================

function displayResults(data) {
    resultsSection.classList.remove('hidden');
    
    const skin = data.skin_analysis || {};
    const outfit = data.outfit_analysis || {};
    const harmony = data.harmony || {};
    const recs = data.recommendations || {};
    
    // Debug log
    console.log('Received data:', data);
    
    // Season Hero
    const seasonBadge = document.getElementById('seasonBadge');
    const seasonDescription = document.getElementById('seasonDescription');
    seasonBadge.textContent = skin.season || 'Unknown Season';
    
    // Season descriptions
    const seasonDescs = {
        'Light Spring': 'Warm, light, and bright. You glow in soft peachy tones and gentle corals.',
        'True Spring': 'Pure warmth with brightness. Your palette is fresh, golden, and vibrant.',
        'Bright Spring': 'High contrast with warm undertones. Bold, clear colors make you shine.',
        'Light Summer': 'Cool, light, and soft. Delicate pastels and dusty roses suit you best.',
        'True Summer': 'Pure coolness with soft elegance. Muted, romantic colors flatter you.',
        'Soft Summer': 'Cool and muted. Gentle, greyed tones create beautiful harmony.',
        'Soft Autumn': 'Warm and muted. Earthy, soft colors bring out your natural warmth.',
        'True Autumn': 'Pure warmth with rich depth. Spicy, burnished colors are your signature.',
        'Dark Autumn': 'Warm and deep. Rich, luxurious colors with golden undertones suit you.',
        'Dark Winter': 'Cool and deep. Dramatic, rich colors create stunning contrast.',
        'True Winter': 'Pure coolness with high contrast. Icy, vivid colors are your power palette.',
        'Bright Winter': 'Cool with maximum brightness. Electric, jewel tones make you radiant.'
    };
    seasonDescription.textContent = seasonDescs[skin.season] || 'A unique combination of undertone and depth.';
    
    // Render season palette
    renderSeasonPalette(skin.season);
    
    // Skin Analysis - map backend field names correctly
    // rgb_values is {r, g, b} object from backend
    const rgbObj = skin.rgb_values || {};
    const skinRGB = [rgbObj.r || 200, rgbObj.g || 170, rgbObj.b || 150];
    document.getElementById('skinColorSwatch').style.background = 
        `rgb(${skinRGB[0]}, ${skinRGB[1]}, ${skinRGB[2]})`;
    document.getElementById('skinTone').textContent = skin.skin_tone || 'Detected';
    document.getElementById('skinRGB').textContent = `RGB(${skinRGB.join(', ')})`;
    document.getElementById('undertone').textContent = capitalizeFirst(skin.undertone || '—');
    
    // Season dimensions - map from color_dimensions
    const dims = skin.color_dimensions || {};
    document.getElementById('dimTemperature').textContent = capitalizeFirst(dims.temperature || '—');
    document.getElementById('dimValue').textContent = capitalizeFirst(dims.value || '—');
    document.getElementById('dimChroma').textContent = capitalizeFirst(dims.chroma || '—');
    
    // Monk Scale
    const monkRow = document.getElementById('monkScaleRow');
    const monkScaleEl = document.getElementById('monkScale');
    if (skin.monk_scale) {
        monkRow.style.display = 'flex';
        const monk = skin.monk_scale;
        monkScaleEl.textContent = `${monk.code || monk.scale || ''} — ${monk.name || monk.tone || ''}`;
    } else {
        monkRow.style.display = 'none';
    }
    
    // DeepFace ML Analysis
    const deepfaceRow = document.getElementById('deepfaceRow');
    const deepfaceEl = document.getElementById('deepfaceResult');
    let detectedGender = 'Woman';  // Default
    
    if (skin.deepface) {
        deepfaceRow.style.display = 'flex';
        const df = skin.deepface;
        
        // Store detected gender
        if (df.gender) {
            detectedGender = df.gender;
            console.log('🔍 DeepFace detected gender:', detectedGender);
        }
        
        // Show race info
        deepfaceEl.textContent = `${capitalizeFirst(df.dominant_race)} (${df.confidence}%)`;
    } else {
        deepfaceRow.style.display = 'none';
        console.log('⚠️ No DeepFace data, using default gender:', detectedGender);
    }
    
    // Update Makeup/Grooming section based on gender
    console.log('📋 Updating makeup section for gender:', detectedGender);
    updateMakeupSection(detectedGender);
    
    // Outfit Analysis - map backend field names correctly
    const outfitRGB = outfit.color_rgb || [100, 100, 100];
    document.getElementById('outfitColorSwatch').style.background = 
        `rgb(${outfitRGB[0]}, ${outfitRGB[1]}, ${outfitRGB[2]})`;
    document.getElementById('outfitColor').textContent = outfit.dominant_color || 'Detected';
    document.getElementById('outfitHex').textContent = outfit.color_hex || rgbToHex(outfitRGB);
    document.getElementById('colorFamily').textContent = capitalizeFirst(outfit.color_family || '—');
    document.getElementById('colorTemp').textContent = capitalizeFirst(outfit.color_temperature || '—');
    
    // Season affinity
    const affinity = outfit.season_affinity || [];
    document.getElementById('seasonAffinity').textContent = 
        affinity.slice(0, 2).join(', ') || '—';
    
    // Confidence - match_confidence is already 0-100 from backend
    const confidence = outfit.match_confidence;
    document.getElementById('matchConfidence').textContent = 
        confidence ? `${Math.round(confidence)}%` : '—';
    
    // Harmony Score
    const score = harmony.score || 0;
    document.getElementById('harmonyScore').textContent = Math.round(score);
    
    // Animate score ring
    const circumference = 2 * Math.PI * 45; // r=45
    const offset = circumference - (score / 100) * circumference;
    document.getElementById('scoreRing').style.strokeDashoffset = offset;
    
    // Set ring color based on score
    const ring = document.getElementById('scoreRing');
    if (score >= 80) {
        ring.style.stroke = '#2D7A4F';
    } else if (score >= 60) {
        ring.style.stroke = '#B8860B';
    } else {
        ring.style.stroke = '#C4841D';
    }
    
    // Harmony rating
    let rating = 'Needs Work';
    if (score >= 85) rating = 'Excellent Match';
    else if (score >= 70) rating = 'Great Harmony';
    else if (score >= 55) rating = 'Good Pairing';
    document.getElementById('harmonyRating').textContent = rating;
    document.getElementById('harmonyExplanation').textContent = 
        harmony.explanation || 'Your outfit and skin tone combination has been analyzed.';
    
    // Recommendations
    populateRecommendations(recs);
}

// ============================================
// Populate Recommendations
// ============================================

function populateRecommendations(recs) {
    console.log('=== RECOMMENDATIONS DEBUG ===');
    console.log('Full recs object:', JSON.stringify(recs, null, 2));
    
    // Extract nested objects
    const makeup = recs.makeup || {};
    const hairstyle = recs.hairstyle || {};
    const accessories = recs.accessories || {};
    const alternateOutfits = recs.alternate_outfits || {};
    
    console.log('Makeup:', makeup);
    console.log('Hairstyle:', hairstyle);
    console.log('Accessories:', accessories);
    console.log('Alternate outfits:', alternateOutfits);
    
    // Makeup
    document.getElementById('foundationTip').textContent = makeup.foundation_tip || '—';
    document.getElementById('lipColors').textContent = 
        Array.isArray(makeup.lip_colors) ? makeup.lip_colors.join(', ') : (makeup.lip_colors || '—');
    document.getElementById('eyeMakeup').textContent = makeup.eye_makeup || '—';
    document.getElementById('blush').textContent = makeup.blush || '—';
    
    // Hair
    document.getElementById('hairstyleSuggestion').textContent = hairstyle.style_suggestion || '—';
    document.getElementById('hairColorTips').textContent = hairstyle.hair_color_tips || '—';
    
    // Accessories
    document.getElementById('jewelryMetal').textContent = accessories.jewelry_metal || '—';
    document.getElementById('jewelryStyle').textContent = accessories.jewelry_style || '—';
    document.getElementById('bagColor').textContent = accessories.bag_color || '—';
    document.getElementById('shoes').textContent = accessories.shoes || '—';
    
    // Colors - from alternate_outfits
    const betterColors = document.getElementById('betterColors');
    betterColors.innerHTML = '';
    const colors = alternateOutfits.better_colors || [];
    colors.slice(0, 6).forEach(color => {
        const tag = document.createElement('span');
        tag.className = 'color-tag';
        tag.innerHTML = `<span class="color-tag-swatch" style="background:${getColorHex(color)}"></span>${color}`;
        betterColors.appendChild(tag);
    });
    
    // Color combos
    const colorCombos = document.getElementById('colorCombos');
    colorCombos.innerHTML = '';
    const combos = alternateOutfits.color_combinations || [];
    combos.slice(0, 3).forEach(combo => {
        const li = document.createElement('li');
        li.innerHTML = `<span>Combo:</span><span>${combo}</span>`;
        colorCombos.appendChild(li);
    });
    
    // Patterns - from alternate_outfits
    const patterns = alternateOutfits.patterns;
    document.getElementById('patterns').textContent = 
        Array.isArray(patterns) ? patterns.join(', ') : (patterns || '—');
    
    // Overall tip
    document.getElementById('overallTip').textContent = recs.overall_tip || 'Express your unique style with confidence!';
    
    // Outfit Suggestions
    populateOutfitSuggestions(alternateOutfits.suggested_outfits || []);
    
    // Curated Accessories
    populateCuratedAccessories(accessories.curated_items || []);
}

// ============================================
// Populate Outfit Suggestions
// ============================================

function populateOutfitSuggestions(outfits) {
    const grid = document.getElementById('outfitSuggestionsGrid');
    const section = document.getElementById('outfitSuggestionsSection');
    const subtitle = document.getElementById('outfitSubtitle');
    
    if (!outfits || outfits.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    
    // Get current occasion from the form
    const occasionSelect = document.getElementById('occasion');
    const occasion = occasionSelect ? occasionSelect.value : 'casual';
    
    // Update subtitle based on occasion
    const occasionLabels = {
        'casual': 'Comfortable everyday looks',
        'formal': 'Polished professional attire',
        'business': 'Sharp corporate style',
        'party': 'Glamorous celebration wear',
        'date': 'Romantic & charming outfits',
        'traditional': 'Classic Indian ethnic wear',
        'wedding': 'Grand celebration attire'
    };
    subtitle.textContent = occasionLabels[occasion] || 'Perfect outfits for your occasion';
    
    // Outfit emojis by type
    const outfitEmojis = {
        'saree': '🥻', 'lehenga': '👗', 'anarkali': '💃', 'kurta': '🧥',
        'suit': '🤵', 'sherwani': '🎭', 'dress': '👗', 'blazer': '🧥',
        'gown': '👗', 'salwar': '👘', 'dhoti': '🪔', 'mundu': '🪔',
        'default_woman': '👗', 'default_man': '🧥'
    };
    
    grid.innerHTML = '';
    
    outfits.forEach(outfit => {
        const card = document.createElement('div');
        card.className = 'outfit-card';
        
        // Determine emoji
        let emoji = outfitEmojis.default_woman;
        const outfitLower = outfit.outfit.toLowerCase();
        for (const [key, value] of Object.entries(outfitEmojis)) {
            if (outfitLower.includes(key)) {
                emoji = value;
                break;
            }
        }
        
        card.innerHTML = `
            <div class="outfit-card-header">
                <span class="outfit-emoji">${emoji}</span>
                <span class="outfit-name">${outfit.outfit}</span>
            </div>
            <p class="outfit-description">${outfit.description}</p>
            <div class="outfit-colors">
                <span class="outfit-colors-label">Suggested Colors</span>
                <span class="outfit-colors-value">${outfit.colors}</span>
            </div>
            ${outfit.recommended_colors ? `
                <div class="outfit-recommended">
                    <span class="outfit-recommended-label">For Your Undertone</span>
                    <span class="outfit-recommended-value">${outfit.recommended_colors}</span>
                </div>
            ` : ''}
        `;
        
        grid.appendChild(card);
    });
}

// ============================================
// Populate Curated Accessories
// ============================================

function populateCuratedAccessories(items) {
    const grid = document.getElementById('accessoriesGrid');
    const section = document.getElementById('accessoriesSection');
    
    if (!items || items.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    grid.innerHTML = '';
    
    items.forEach(item => {
        const card = document.createElement('a');
        card.className = 'accessory-card';
        card.href = item.link || '#';
        card.target = '_blank';
        card.rel = 'noopener noreferrer';
        
        // Color match badge
        const matchBadge = item.color_match ? 
            `<span class="color-match-badge ${item.color_match}">${item.color_match === 'matching' ? '🎨 Match' : item.color_match === 'complementary' ? '✨ Complement' : '💫 Neutral'}</span>` : '';
        
        // Color note
        const colorNote = item.color_note ? 
            `<div class="color-note">${item.color_note}</div>` : '';
        
        card.innerHTML = `
            <div class="accessory-image-container">
                ${matchBadge}
                <img class="accessory-image" src="${item.image}" alt="${item.name}" 
                     onerror="this.src='https://via.placeholder.com/200x140?text=${encodeURIComponent(item.type)}'">
            </div>
            <div class="accessory-info">
                <div class="accessory-name">${item.name}</div>
                <div class="accessory-type">${item.type}</div>
                ${colorNote}
                <div class="accessory-price">${item.price_range || ''}</div>
                <div class="accessory-cta">
                    Shop Now
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M7 17L17 7M17 7H7M17 7V17"/>
                    </svg>
                </div>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// ============================================
// Update Makeup/Grooming Section Based on Gender
// ============================================

function updateMakeupSection(gender) {
    const icon = document.getElementById('makeupIcon');
    const title = document.getElementById('makeupTitle');
    const foundationLabel = document.getElementById('foundationLabel');
    const lipsLabel = document.getElementById('lipsLabel');
    const eyesLabel = document.getElementById('eyesLabel');
    const blushLabel = document.getElementById('blushLabel');
    
    if (gender === 'Man') {
        icon.textContent = '🧔';
        title.textContent = 'Grooming';
        foundationLabel.textContent = 'Skincare:';
        lipsLabel.textContent = 'Lip Care:';
        eyesLabel.textContent = 'Beard:';
        blushLabel.textContent = 'Face:';
    } else {
        icon.textContent = '💄';
        title.textContent = 'Makeup';
        foundationLabel.textContent = 'Foundation:';
        lipsLabel.textContent = 'Lips:';
        eyesLabel.textContent = 'Eyes:';
        blushLabel.textContent = 'Blush:';
    }
}

// ============================================
// Reset Analysis
// ============================================

function resetAnalysis() {
    // Hide results
    resultsSection.classList.add('hidden');
    
    // Show upload
    uploadSection.classList.remove('hidden');
    
    // Reset form
    analyzeForm.reset();
    
    // Reset previews
    selfiePreview.src = '';
    outfitPreview.src = '';
    selfieArea.classList.remove('has-file');
    outfitArea.classList.remove('has-file');
    
    // Reset score ring
    document.getElementById('scoreRing').style.strokeDashoffset = 283;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// Utility Functions
// ============================================

function capitalizeFirst(str) {
    if (!str) return '—';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ============================================
// Season Palette Data & Rendering
// ============================================

const SEASON_PALETTES = {
    "Bright Spring": {
        best: ["coral", "turquoise", "yellow", "warm pink", "orange red", "periwinkle", "teal", "grass green"],
        good: ["ivory", "light navy", "bright blue", "mango", "apricot", "clear red"],
        avoid: ["black", "dark brown", "burgundy", "charcoal", "olive"]
    },
    "True Spring": {
        best: ["golden yellow", "coral", "peach", "warm green", "aqua", "orange", "salmon", "camel"],
        good: ["light gold", "warm beige", "cream", "turquoise", "apricot", "warm pink"],
        avoid: ["black", "pure white", "cool gray", "burgundy", "dark purple"]
    },
    "Light Spring": {
        best: ["peach", "light coral", "warm pink", "light aqua", "cream", "camel", "powder blue", "mint"],
        good: ["ivory", "champagne", "blush", "light sage", "warm gray"],
        avoid: ["black", "dark navy", "charcoal", "pure white", "neon"]
    },
    "Light Summer": {
        best: ["powder blue", "soft pink", "lavender", "light gray", "rose", "mauve", "periwinkle", "dusty rose"],
        good: ["soft white", "light navy", "cocoa", "soft teal", "stone"],
        avoid: ["orange", "gold", "bright yellow", "black", "rust"]
    },
    "True Summer": {
        best: ["rose", "raspberry", "soft blue", "blue gray", "plum", "watermelon", "cocoa", "mauve"],
        good: ["soft white", "lavender", "powder pink", "soft navy", "burgundy"],
        avoid: ["orange", "gold", "warm yellow", "camel", "rust"]
    },
    "Soft Summer": {
        best: ["dusty rose", "soft blue", "sage green", "mauve", "cocoa", "blue gray", "soft teal", "stone"],
        good: ["charcoal", "dusty lavender", "taupe", "soft white", "rose brown"],
        avoid: ["orange", "bright yellow", "black", "pure white", "hot pink"]
    },
    "Soft Autumn": {
        best: ["soft teal", "dusty pink", "sage", "terracotta", "warm gray", "soft coral", "camel", "olive"],
        good: ["cream", "soft brown", "dusty rose", "jade", "warm beige"],
        avoid: ["black", "pure white", "neon", "icy blue", "silver"]
    },
    "True Autumn": {
        best: ["rust", "olive", "terracotta", "gold", "teal", "warm brown", "burnt orange", "moss green"],
        good: ["cream", "camel", "bronze", "mustard", "coffee", "coral"],
        avoid: ["black", "pure white", "pink", "silver", "icy colors"]
    },
    "Dark Autumn": {
        best: ["olive", "rust", "terracotta", "teal", "bronze", "warm brown", "deep gold", "burgundy"],
        good: ["cream", "coffee", "pumpkin", "moss", "copper", "mahogany"],
        avoid: ["pastels", "light pink", "powder blue", "silver", "gray"]
    },
    "Dark Winter": {
        best: ["black", "pure white", "burgundy", "dark teal", "charcoal", "deep purple", "true red", "emerald"],
        good: ["navy", "dark brown", "ice gray", "icy pink", "magenta"],
        avoid: ["orange", "gold", "warm yellow", "camel", "rust"]
    },
    "True Winter": {
        best: ["black", "pure white", "true red", "royal blue", "hot pink", "emerald", "ice blue", "deep purple"],
        good: ["navy", "charcoal", "bright pink", "icy violet", "silver"],
        avoid: ["orange", "gold", "warm tones", "muted colors", "beige"]
    },
    "Bright Winter": {
        best: ["hot pink", "royal blue", "emerald", "pure white", "true red", "violet", "bright yellow", "turquoise"],
        good: ["black", "ice blue", "fuchsia", "lime", "electric blue"],
        avoid: ["muted tones", "dusty colors", "warm brown", "beige", "rust"]
    }
};

function renderSeasonPalette(season) {
    const palette = SEASON_PALETTES[season];
    if (!palette) {
        document.querySelector('.palette-section').style.display = 'none';
        return;
    }
    
    document.querySelector('.palette-section').style.display = 'block';
    
    // Clear existing
    document.getElementById('bestColorsPalette').innerHTML = '';
    document.getElementById('goodColorsPalette').innerHTML = '';
    document.getElementById('avoidColorsPalette').innerHTML = '';
    
    // Render best colors
    palette.best.forEach(color => {
        const swatch = createPaletteSwatch(color);
        document.getElementById('bestColorsPalette').appendChild(swatch);
    });
    
    // Render good colors
    palette.good.forEach(color => {
        const swatch = createPaletteSwatch(color);
        document.getElementById('goodColorsPalette').appendChild(swatch);
    });
    
    // Render avoid colors
    palette.avoid.forEach(color => {
        const swatch = createPaletteSwatch(color);
        document.getElementById('avoidColorsPalette').appendChild(swatch);
    });
}

function createPaletteSwatch(colorName) {
    const swatch = document.createElement('div');
    swatch.className = 'palette-swatch';
    swatch.style.backgroundColor = getColorHex(colorName);
    swatch.setAttribute('data-name', colorName);
    swatch.title = colorName;
    return swatch;
}

function rgbToHex(rgb) {
    if (!Array.isArray(rgb) || rgb.length < 3) return '#000000';
    return '#' + rgb.map(c => {
        const hex = Math.max(0, Math.min(255, Math.round(c))).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    }).join('');
}

function getColorHex(colorName) {
    const colorMap = {
        // Neutrals
        'white': '#FFFFFF', 'pure white': '#FFFFFF', 'soft white': '#FAF9F6',
        'ivory': '#FFFFF0', 'cream': '#FFFDD0', 'champagne': '#F7E7CE',
        'beige': '#F5F5DC', 'warm beige': '#E8D4B8', 'taupe': '#483C32',
        'gray': '#808080', 'light gray': '#D3D3D3', 'warm gray': '#8B8589',
        'blue gray': '#6699CC', 'cool gray': '#8C92AC', 'ice gray': '#C4C4C4',
        'charcoal': '#36454F', 'black': '#000000', 'stone': '#928E85',
        
        // Reds & Pinks
        'red': '#E53935', 'true red': '#DC143C', 'clear red': '#FF0000',
        'crimson': '#DC143C', 'burgundy': '#800020', 'wine': '#722F37',
        'coral': '#FF7F50', 'soft coral': '#F88379', 'bright coral': '#FF6F61',
        'salmon': '#FA8072', 'pink': '#FFC0CB', 'soft pink': '#F4C2C2',
        'warm pink': '#FF69B4', 'hot pink': '#FF69B4', 'bright pink': '#FF007F',
        'rose': '#FF007F', 'dusty rose': '#DCAE96', 'rose brown': '#BC8F8F',
        'blush': '#DE5D83', 'mauve': '#E0B0FF', 'raspberry': '#E30B5C',
        'watermelon': '#FD4659', 'fuchsia': '#FF00FF', 'magenta': '#FF00FF',
        'icy pink': '#F8BBD9',
        
        // Oranges & Browns
        'orange': '#FF9800', 'bright orange': '#FF7F00', 'light orange': '#FFB347',
        'orange red': '#FF4500', 'burnt orange': '#CC5500',
        'peach': '#FFCBA4', 'peachy pink': '#FFCBA4',
        'apricot': '#FBCEB1', 'mango': '#FF8243',
        'terracotta': '#E2725B', 'rust': '#B7410E', 
        'brown': '#795548', 'warm brown': '#964B00', 'soft brown': '#A67B5B',
        'dark brown': '#654321', 'light brown': '#C4A484',
        'tan': '#D2B48C', 'caramel': '#FFD59A', 'chocolate': '#7B3F00',
        'camel': '#C19A6B', 'coffee': '#6F4E37', 'cocoa': '#D2691E',
        'mahogany': '#C04000', 'pumpkin': '#FF7518', 'burnt sienna': '#E97451',
        'copper': '#B87333', 'bronze': '#CD7F32',
        
        // Yellows & Golds
        'yellow': '#FFEB3B', 'bright yellow': '#FFFF00', 'soft yellow': '#FFFACD',
        'warm yellow': '#FFDF00', 'golden yellow': '#FFD700', 'pale yellow': '#FFFACD',
        'gold': '#FFD700', 'light gold': '#F5E6A0', 'deep gold': '#DAA520',
        'muted gold': '#C5B358', 'medium gold': '#D4AF37',
        'mustard': '#FFDB58', 'honey': '#EB9605', 'amber': '#FFBF00',
        
        // Greens
        'green': '#4CAF50', 'warm green': '#8DB600', 'grass green': '#7CFC00',
        'olive': '#808000', 'soft olive': '#9CAD6C',
        'sage': '#BCB88A', 'sage green': '#BCB88A', 'light sage': '#C8D5BB',
        'mint': '#98FF98', 'seafoam': '#71EEB8',
        'emerald': '#50C878', 'forest': '#228B22', 'forest green': '#228B22',
        'teal': '#008080', 'soft teal': '#80B3A8', 'dark teal': '#014d4e',
        'deep teal': '#367588', 'light teal': '#7FDBDA',
        'jade': '#00A86B', 'soft jade': '#5F9EA0',
        'moss': '#8A9A5B', 'moss green': '#8A9A5B',
        'khaki': '#C3B091', 'light khaki': '#F0E68C',
        'lime': '#32CD32',
        
        // Blues
        'blue': '#2196F3', 'soft blue': '#AFDAFC', 'bright blue': '#0096FF',
        'navy': '#000080', 'light navy': '#3D5A80', 'soft navy': '#4E5D78',
        'cobalt': '#0047AB', 'royal': '#4169E1', 'royal blue': '#4169E1',
        'sky': '#87CEEB', 'sky blue': '#87CEEB',
        'powder': '#B0E0E6', 'powder blue': '#B0E0E6',
        'ice blue': '#99FFFF', 'icy blue': '#99FFFF',
        'periwinkle': '#CCCCFF', 'slate': '#708090',
        'denim': '#1560BD', 'electric blue': '#7DF9FF',
        'aqua': '#00FFFF', 'light aqua': '#7FFFD4',
        'turquoise': '#40E0D0',
        'smoky blue': '#5D89A8',
        
        // Purples
        'purple': '#9C27B0', 'deep purple': '#673AB7', 'dark purple': '#4B0082',
        'lavender': '#E6E6FA', 'dusty lavender': '#B4A7C7',
        'lilac': '#C8A2C8', 'light plum': '#DDA0DD',
        'plum': '#DDA0DD', 'muted plum': '#8E4585',
        'eggplant': '#614051', 'violet': '#EE82EE', 'icy violet': '#E0B0FF',
        'orchid': '#DA70D6', 'berry': '#8E4585',
        
        // Metals
        'silver': '#C0C0C0',
        
        // Misc
        'icy colors': '#E0FFFF', 'warm tones': '#DAA520',
        'muted tones': '#A89F91', 'muted colors': '#A89F91',
        'dusty colors': '#9A9A9A', 'neon': '#39FF14'
    };
    
    const normalizedName = colorName.toLowerCase().trim();
    return colorMap[normalizedName] || '#888888';
}

// Make resetAnalysis globally available
window.resetAnalysis = resetAnalysis;
