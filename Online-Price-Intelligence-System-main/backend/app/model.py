import tensorflow as tf
from tensorflow.keras.applications.efficientnet import EfficientNetB0, decode_predictions
import numpy as np
import re
import os
import io
import hashlib
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

# Load model globally to avoid reloading on every request
print("Loading EfficientNetB0 model...")
model = EfficientNetB0(weights='imagenet')
print("Model loaded successfully. Warming up...")
# Warmup: Run a dummy prediction so the first user request is fast
model.predict(np.zeros((1, 224, 224, 3)))
print("Model warmup complete.")


# ────────────────────────────────────────────────────────────────
# Mapping: ImageNet class name → human-friendly product search term
# ────────────────────────────────────────────────────────────────
IMAGENET_TO_PRODUCT = {
    # Phones & Tablets
    "cellular_telephone": "Apple iPhone",
    "phone": "Apple iPhone",
    "mobile_phone": "Apple iPhone",
    "hand-held_computer": "Apple iPhone",
    "handheld_computer": "Apple iPhone",
    "pager": "Smartphone",
    "iPod": "Apple iPhone",
    "ipod": "Apple iPhone",
    "tablet_computer": "iPad Tablet",
    "remote_control": "Smartphone", # VERY COMMON MISIDENTIFICATION FOR IPHONES
    "dial_telephone": "Telephone",

    # Computers & Peripherals
    "laptop": "Premium Laptop",
    "notebook": "Slim Laptop",
    "desktop_computer": "Desktop Computer",
    "personal_computer": "Desktop Computer",
    "computer_keyboard": "Mechanical Keyboard",
    "keyboard": "Mechanical Keyboard",
    "computer_mouse": "Wireless Mouse",
    "mouse": "Wireless Mouse",
    "monitor": "Computer Monitor",
    "screen": "Computer Monitor",
    "printer": "Inkjet Printer",
    "modem": "Router",

    # Audio / Video
    "loudspeaker": "Smartphone", # COMMON MISIDENTIFICATION FOR IPHONES
    "speaker": "Bluetooth Speaker",
    "microphone": "Studio Microphone",
    "headphone": "Headphones",
    "headphones": "Headphones",
    "earphone": "Wireless Earbuds",
    "earphones": "Earbuds",
    "digital_camera": "Digital Camera",
    "camera": "Digital Camera",
    "reflex_camera": "Digital Camera",
    "camcorder": "Video Camera",
    "television": "Smart TV",
    "tv": "Smart TV",
    "home_theater": "Home Theater System",
    "projector": "HD Projector",

    # Wearables
    "wristwatch": "Smartwatch",
    "watch": "Smartwatch",
    "sunglasses": "Sunglasses",
    "backpack": "Laptop Backpack",
    "running_shoe": "Running Shoes",
    "shoe": "Sports Shoes",
    "sneaker": "Sneakers",

    # Gaming
    "joystick": "Gaming Controller",
    "game_controller": "Gaming Controller",
    "space_invaders": "Gaming Console",

    # Home Appliances
    "refrigerator": "Refrigerator",
    "washing_machine": "Washing Machine",
    "dishwasher": "Dishwasher",
    "vacuum": "Robot Vacuum Cleaner",
    "vacuum_cleaner": "Vacuum Cleaner",
    "blender": "Kitchen Blender",
    "coffee_maker": "Coffee Machine",
    "toaster": "Pop-up Toaster",
    "microwave": "Microwave Oven",
    "iron": "Steam Iron",
    "air_conditioner": "Air Conditioner",
    "ceiling_fan": "Ceiling Fan",

    # Misc gadgets / Beauty
    "power_drill": "Power Drill",
    "electric_fan": "Table Fan",
    "table_lamp": "Table Lamp",
    "wallet": "Leather Wallet",
    "handbag": "Handbag",
    "perfume": "Premium Perfume",
    "lipstick": "Matte Lipstick",
    "hair_dryer": "Hair Dryer",
    "electric_razor": "Electric Shaver",
    "sunglass": "Sunglasses",
    "sunscreen": "Sunscreen Serum",
    "pill_bottle": "Sunscreen / Skincare",
    "lotion": "Sunscreen / Body Lotion",
    "soap_dispenser": "Face Wash / Skincare",
    "vial": "Skincare Serum",
    "medicine_chest": "Skincare Products",
    "shampoo": "Hair Care / Shampoo",
    "cream": "Face Cream",
    "bottle": "Skincare Bottle",
    "petri_dish": "Beauty Sample",
    "beaker": "Skincare Bottle",
    "water_bottle": "Water Bottle",
    "barrel": "Industrial Product",
    "pot": "Cream Jar",
    "vase": "Decorative Item",
}

# Skincare/Bottle Keywords for Heuristics
SKINCARE_KEYWORDS = {
    "pill_bottle", "lotion", "soap_dispenser", "vial", "shampoo", 
    "perfume", "lipstick", "hair_dryer", "electric_razor", "bottle",
    "beaker", "petri_dish", "pot", "sunscreen"
}


def _clean_label(raw_label: str) -> str:
    """
    Converts a raw ImageNet label (with underscores) to a clean product search term.
    1. Check direct mapping first.
    2. Try prefix / substring match.
    3. Fall back to title-cased, underscore-stripped label.
    """
    # Exact match
    if raw_label in IMAGENET_TO_PRODUCT:
        return IMAGENET_TO_PRODUCT[raw_label]

    # Lowercase match
    lower = raw_label.lower()
    if lower in IMAGENET_TO_PRODUCT:
        return IMAGENET_TO_PRODUCT[lower]

    # Substring / partial match
    for key, product in IMAGENET_TO_PRODUCT.items():
        if key.lower() in lower or lower in key.lower():
            return product

    # Generic fallback: replace underscores with spaces and title-case
    return raw_label.replace("_", " ").title()

try:
    import pytesseract
    # Common Tesseract paths for Windows
    TESSERACT_PATHS = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Users\nilay\AppData\Local\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]
    for p in TESSERACT_PATHS:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break
except ImportError:
    pytesseract = None

import os
from PIL import Image
import io

# Initialize thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

# Simple in-memory cache for prediction results
prediction_cache = {}

def _get_image_hash(image_bytes: bytes) -> str:
    """Generate SHA256 hash for image bytes to use as cache key."""
    return hashlib.sha256(image_bytes).hexdigest()

def _run_ocr(raw_bytes: bytes) -> str:
    """Helper to run OCR in a separate thread with optimized resizing."""
    if not pytesseract or not raw_bytes:
        return ""
    try:
        img = Image.open(io.BytesIO(raw_bytes))
        
        # Resize for faster OCR if image is very large
        max_dim = 1024
        if max(img.size) > max_dim:
            scale = max_dim / max(img.size)
            new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        print(f"OCR Background Error: {e}")
        return ""

def predict_image(processed_image: np.ndarray, top_k: int = 3, raw_bytes: bytes = None) -> list:
    """
    Runs prediction on the preprocessed image.
    Uses parallel execution for OCR and Model prediction.
    Implements caching to avoid redundant analysis.
    """
    try:
        # 1. Check Cache
        img_hash = None
        if raw_bytes:
            img_hash = _get_image_hash(raw_bytes)
            if img_hash in prediction_cache:
                print(f"Using cached prediction for image {img_hash[:8]}...")
                return prediction_cache[img_hash]

        # 2. Parallel Execution: Start OCR in background
        ocr_future = executor.submit(_run_ocr, raw_bytes)

        # 3. Model Prediction (Main Thread)
        predictions = model.predict(processed_image)
        decoded = decode_predictions(predictions, top=top_k)[0]

        results = []
        for _, label, score in decoded:
            results.append({
                "label": label,
                "search_query": _clean_label(label),
                "confidence": float(score)
            })

        # 4. Wait for OCR result (if it wasn't too fast)
        extracted_text = ""
        try:
            extracted_text = ocr_future.result(timeout=10) # 10s timeout safeguard
            if extracted_text:
                print(f"OCR Extracted: {extracted_text[:50]}...")
        except Exception as e:
            print(f"OCR timeout or error: {e}")

        # ────────────────────────────────────────────────────────────────
        # Heuristics & Contextual Boosting
        # ────────────────────────────────────────────────────────────────
        labels_lower = {r["label"].lower() for r in results if isinstance(r.get("label"), str)}
        
        # 1. Skincare Enhancement:
        # If any skincare/bottle-like item is in top-3, and top prediction is a 
        # generic rectangular object (monitor, screen), prioritize skincare.
        is_skincare_likely = any(kw in labels_lower for kw in SKINCARE_KEYWORDS)
        top_label = results[0]["label"].lower()
        
        if is_skincare_likely and top_label in {"monitor", "screen", "television", "tv"}:
            # Find the best skincare prediction in the list
            for r in results:
                if r["label"].lower() in SKINCARE_KEYWORDS:
                    # Boost it to the front
                    results.insert(0, {
                        "label": r["label"],
                        "search_query": r["search_query"] if "Sunscreen" in r["search_query"] else "Sunscreen Skincare",
                        "confidence": r["confidence"],
                        "boosted": True
                    })
                    break

        # 2. Stationery Enhancement
        if any(x in labels_lower for x in {"rubber_eraser", "pencil_box", "pencil_sharpener"}):
            best_conf = max((r.get("confidence", 0.0) for r in results), default=0.0)
            results.insert(0, {"label": "pencil", "search_query": "Pencil", "confidence": float(best_conf)})

        # 3. OCR Boosting (Sunscreen / Brand Detection)
        if extracted_text:
            text_lower = extracted_text.lower()
            # If the user mentioned sunscreen/lotion keywords or if specific brand names are detected
            sunscreen_keywords = {"sunscreen", "spf", "sunblock", "uv", "lotion", "cream", "aloe"}
            
            detected_brand = ""
            # Simple brand detection heuristic (could be expanded)
            common_brands = {"neutrogena", "nivea", "lakme", "biore", "cetaphil", "pupa", "mamaearth", "wow"}
            for brand in common_brands:
                if brand in text_lower:
                    detected_brand = brand.title()
                    break

            if any(kw in text_lower for kw in sunscreen_keywords):
                search_prefix = f"{detected_brand} " if detected_brand else ""
                results.insert(0, {
                    "label": "OCR_DETECTION",
                    "search_query": f"{search_prefix}Sunscreen".strip(),
                    "confidence": 0.95, # High confidence for OCR match
                    "boosted": True,
                    "reason": "Text detected in image"
                })
            elif detected_brand:
                # If brand detected but no sunscreen keyword, still boost with brand name
                results.insert(0, {
                    "label": "OCR_DETECTION",
                    "search_query": f"{detected_brand} {results[0]['search_query']}",
                    "confidence": 0.90,
                    "boosted": True
                })

        # 5. Save to Cache
        if img_hash:
            # Keep cache size manageable
            if len(prediction_cache) > 100:
                prediction_cache.clear()
            prediction_cache[img_hash] = results

        return results
    except Exception as e:
        print(f"Prediction error: {e}")
        return []
