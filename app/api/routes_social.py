from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import os

LOGO_PATH = os.path.join(os.path.dirname(__file__), '../static/moundvision_logo.png')

router = APIRouter()

def hex_to_rgba(hex_color, alpha=255):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, alpha)
    return (30, 144, 255, alpha)

def crop_center(img, target_w, target_h):
    w, h = img.size
    aspect = target_w / target_h
    img_aspect = w / h
    if img_aspect > aspect:
        new_w = int(h * aspect)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / aspect)
        top = 0
        img = img.crop((0, top, w, top + new_h))
    return img.resize((target_w, target_h))

@router.post("/generate-graphic")
async def generate_graphic(
    mode: str = Form(...),
    title: str = Form(...),
    subtitle: str = Form(...),
    stat_labels: List[str] = Form(...),
    stat_values: List[str] = Form(...),
    accent_color: Optional[str] = Form(None),
    aspect: str = Form('square'),
    hashtag: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    player_image: Optional[UploadFile] = File(None),
):
    logo_bytes = await logo.read() if logo else None
    player_bytes = await player_image.read() if player_image else None

    if aspect == 'portrait':
        size = (1080, 1350)
    elif aspect == 'landscape':
        size = (1280, 720)
    else:
        size = (1080, 1080)

    img = Image.new('RGB', size, (255, 255, 255))

    font_path = os.path.join(os.path.dirname(__file__), '../static/DejaVuSans-Bold.ttf')
    try:
        font_title = ImageFont.truetype(font_path, 80)
        font_subtitle = ImageFont.truetype(font_path, 50)
        font_stat_label = ImageFont.truetype(font_path, 36)
        font_stat_value = ImageFont.truetype(font_path, 64)
        font_hashtag = ImageFont.truetype(font_path, 30)
    except Exception as e:
        print(f"[DEBUG] Font load error: {e}")
        font_title = font_subtitle = font_stat_label = font_stat_value = font_hashtag = ImageFont.load_default()

    if player_bytes:
        try:
            player_img = Image.open(io.BytesIO(player_bytes)).convert('RGB')
            bg_img = crop_center(player_img, size[0], size[1])
            blurred_bg = bg_img.filter(ImageFilter.GaussianBlur(10))
            img.paste(blurred_bg)
            overlay = Image.new('RGBA', size, (0,0,0,80))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
        except Exception as e:
            print(f"[DEBUG] Player image error: {e}")

    draw = ImageDraw.Draw(img)

    banner_height = int(size[1] * 0.12)
    banner = Image.new('RGBA', (size[0], banner_height), hex_to_rgba(accent_color or '#1e90ff', 255))
    banner_draw = ImageDraw.Draw(banner)
    banner_draw.rectangle([0, 0, size[0], banner_height], fill=hex_to_rgba(accent_color or '#1e90ff', 255))
    img.paste(banner, (0, 0))

    # Pitcher Report text (centered)
    draw.text((size[0]//2, banner_height//2 - 10), "PITCHER REPORT", font=font_title, fill=(255,255,255,255), anchor='mm')

    # Player name under Pitcher Report (centered)
    draw.text((size[0]//2, banner_height + 10), subtitle, font=font_subtitle, fill=(255,255,255,255), anchor='ma')

    # Logo in banner with padding
    if logo_bytes and len(logo_bytes) > 10:
        try:
            logo_img = Image.open(io.BytesIO(logo_bytes)).convert('RGBA')
            max_logo_h = banner_height - 30
            logo_img.thumbnail((max_logo_h, max_logo_h), Image.Resampling.LANCZOS)
            img.paste(logo_img, (size[0] - logo_img.width - 20, 15), logo_img)
        except Exception as e:
            print(f"[DEBUG] Logo load error: {e}")

    stat_start_y = banner_height + font_subtitle.size + 50
    stat_box_w = int(size[0] * 0.85)
    stat_box_h = 90
    stat_x = (size[0] - stat_box_w) // 2
    spacing = 30

    for i, (label, value) in enumerate(zip(stat_labels, stat_values)):
        y = stat_start_y + i * (stat_box_h + spacing)
        if "spin rate" in label.lower():
            label = "MAX SPIN RATE"
        elif "pitch speed" in label.lower():
            label = "MAX PITCH SPEED"

        # Simple stat box (no rounded corners)
        card = Image.new('RGBA', (stat_box_w, stat_box_h), (255,255,255,200))
        card_draw = ImageDraw.Draw(card)
        card_draw.rectangle([0,0,stat_box_w,stat_box_h], fill=(255,255,255,200), outline=hex_to_rgba(accent_color or '#1e90ff', 180), width=3)
        card_draw.text((30, 20), label.upper(), font=font_stat_label, fill=(40,40,60,255))
        card_draw.text((stat_box_w - 30, 10), str(value), font=font_stat_value, fill=hex_to_rgba(accent_color or '#1e90ff', 255), anchor='ra')
        img.paste(card, (stat_x, y), card)

    if hashtag:
        draw.text((size[0]-30, size[1]-40), hashtag, font=font_hashtag, fill=hex_to_rgba(accent_color or '#1e90ff', 220), anchor='rd')

    buf = io.BytesIO()
    img.convert('RGB').save(buf, format='PNG')
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type='image/png')