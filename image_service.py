"""
Image & Design Service Engine
Generates e-commerce promotional badges, banners, and product canvas templates using Pillow.
"""
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os

def create_promo_badge(badge_text: str = "عرض خاص", badge_type: str = "ribbon", color_theme: str = "gold") -> dict:
    """
    Generates a high-resolution marketing badge image as base64 data URI.
    """
    width, height = 400, 140
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    colors = {
        "gold": {"bg": (212, 175, 55, 245), "border": (255, 215, 0, 255), "text": (255, 255, 255, 255)},
        "red": {"bg": (220, 38, 38, 245), "border": (239, 68, 68, 255), "text": (255, 255, 255, 255)},
        "green": {"bg": (16, 185, 129, 245), "border": (52, 211, 153, 255), "text": (255, 255, 255, 255)},
        "blue": {"bg": (37, 99, 235, 245), "border": (96, 165, 250, 255), "text": (255, 255, 255, 255)}
    }
    
    theme = colors.get(color_theme, colors["gold"])
    
    # Draw rounded badge rectangle
    rect_box = [15, 15, width - 15, height - 15]
    draw.rounded_rectangle(rect_box, radius=20, fill=theme["bg"], outline=theme["border"], width=3)
    
    # Inner border for luxury look
    inner_box = [22, 22, width - 22, height - 22]
    draw.rounded_rectangle(inner_box, radius=14, fill=None, outline=(255, 255, 255, 180), width=1)
    
    # Simple centered text representation
    # Drawing decorative stars
    draw.text((35, 50), "★", fill=(255, 255, 255, 230))
    draw.text((width - 55, 50), "★", fill=(255, 255, 255, 230))
    
    # Approximate text drawing
    draw.text((width // 4, height // 3), badge_text, fill=theme["text"])
    
    # Save to buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    return {
        "success": True,
        "width": width,
        "height": height,
        "format": "image/png",
        "data_uri": f"data:image/png;base64,{b64_str}",
        "message": f"تم توليد شارة '{badge_text}' التسويقية بنجاح بجودة عالية."
    }

def create_store_canvas(width: int = 1080, height: int = 1080, store_name: str = "متجر النخبة") -> dict:
    """
    Generates clean e-commerce square canvas with border and subtle watermark.
    """
    img = Image.new("RGB", (width, height), (250, 250, 252))
    draw = ImageDraw.Draw(img)
    
    # Outer frame
    draw.rectangle([10, 10, width - 10, height - 10], outline=(220, 225, 230), width=4)
    draw.rectangle([25, 25, width - 25, height - 25], outline=(235, 238, 242), width=1)
    
    # Header & Footer watermarks
    draw.text((50, height - 60), f"مجهز للمتجر: {store_name}", fill=(160, 170, 180))
    draw.text((width - 250, height - 60), "جودة عالية 1080x1080", fill=(160, 170, 180))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    return {
        "success": True,
        "width": width,
        "height": height,
        "format": "image/jpeg",
        "data_uri": f"data:image/jpeg;base64,{b64_str}",
        "message": "تم إنشاء قالب المتجر المربع بنجاح."
    }
