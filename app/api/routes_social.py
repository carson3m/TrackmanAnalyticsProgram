from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import os
import PIL
from PIL import UnidentifiedImageError

LOGO_PATH = os.path.join(os.path.dirname(__file__), '../static/moundvision_logo.png')

router = APIRouter()

# Helper to center text (move to top so it's defined before use)
def draw_centered_text(draw, text, y, font, fill, panel_size, offset_x=0):
    w, h = draw.textbbox((0, 0), text, font=font)[2:]
    x = offset_x + (panel_size[0] - w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return h

@router.post("/generate-graphic")
async def generate_graphic(
    mode: str = Form(...),
    title: str = Form(...),
    subtitle: str = Form(...),
    stat_labels: List[str] = Form(...),  # e.g., ["Exit Velocity", ...]
    stat_values: List[str] = Form(...),  # e.g., ["99", ...]
    accent_color: Optional[str] = Form(None),
    aspect: str = Form('square'),
    hashtag: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),  # Team logo
    player_image: Optional[UploadFile] = File(None),  # Player image
):
    print(f"[DEBUG] mode={mode}, title={title}, subtitle={subtitle}, stat_labels={stat_labels}, stat_values={stat_values}, accent_color={accent_color}, aspect={aspect}, hashtag={hashtag}, logo={logo.filename if logo else None}")
    print(f"[DEBUG] Pillow version: {PIL.__version__}")

    # Read files ONCE and log info
    logo_bytes = await logo.read() if logo else None
    player_bytes = await player_image.read() if player_image else None
    if logo:
        print(f"[DEBUG] logo type: {type(logo)}, content_type: {getattr(logo, 'content_type', None)}, filename: {logo.filename}")
        print(f"[DEBUG] logo length: {len(logo_bytes) if logo_bytes else 0}")
        print(f"[DEBUG] logo first 100 bytes: {logo_bytes[:100] if logo_bytes else b''}")
    else:
        print("[DEBUG] No logo uploaded.")
    if player_image:
        print(f"[DEBUG] player_image type: {type(player_image)}, content_type: {getattr(player_image, 'content_type', None)}, filename: {player_image.filename}")
        print(f"[DEBUG] player_image length: {len(player_bytes) if player_bytes else 0}")
        print(f"[DEBUG] player_image first 100 bytes: {player_bytes[:100] if player_bytes else b''}")
    else:
        print("[DEBUG] No player_image uploaded.")

    # Image size
    if aspect == 'portrait':
        size = (1080, 1350)
    elif aspect == 'landscape':
        size = (1280, 720)
    else:
        size = (1080, 1080)

    # Create base image (white background)
    img = Image.new('RGB', size, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Helper to convert hex color to RGBA tuple
    def hex_to_rgba(hex_color, alpha=64):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return (r, g, b, alpha)
        return (30, 144, 255, alpha)  # fallback to blue

    # Use bundled DejaVuSans-Bold.ttf for all text
    font_path = os.path.join(os.path.dirname(__file__), '../static/DejaVuSans-Bold.ttf')
    try:
        font_title = ImageFont.truetype(font_path, 90)
        font_subtitle = ImageFont.truetype(font_path, 48)
        font_stat = ImageFont.truetype(font_path, 64)
        font_hashtag = ImageFont.truetype(font_path, 36)
    except Exception as e:
        print(f"[DEBUG] Font load error: {e}")
        font_title = font_subtitle = font_stat = font_hashtag = ImageFont.load_default()
    print(f"[DEBUG] font_title object: {font_title}")

    # --- Modern Social Graphic Layout ---
    # Panel sizes
    left_w = size[0] // 2
    right_w = size[0] - left_w
    panel_h = size[1]

    # Draw left panel: player image or solid color (center-crop, no stretch)
    def crop_center(img, target_w, target_h):
        w, h = img.size
        aspect = target_w / target_h
        img_aspect = w / h
        if img_aspect > aspect:
            # Crop width
            new_w = int(h * aspect)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            # Crop height
            new_h = int(w / aspect)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        return img.resize((target_w, target_h), Image.LANCZOS)

    if player_bytes:
        try:
            player_img = Image.open(io.BytesIO(player_bytes)).convert('RGB')
            player_img = crop_center(player_img, left_w, panel_h)
            # Add border/shadow to player image
            border_size = 8
            bordered_img = Image.new('RGB', (left_w, panel_h), (30, 30, 30))
            bordered_img.paste(player_img, (0, 0))
            img.paste(bordered_img, (0, 0))
        except Exception as e:
            print(f"[DEBUG] Error loading player image: {e}")
            left_color = hex_to_rgba(accent_color or '#1e90ff', alpha=255)
            left_panel = Image.new('RGB', (left_w, panel_h), left_color[:3])
            img.paste(left_panel, (0, 0))
    else:
        left_color = hex_to_rgba(accent_color or '#1e90ff', alpha=255)
        left_panel = Image.new('RGB', (left_w, panel_h), left_color[:3])
        img.paste(left_panel, (0, 0))

    # Draw right panel background
    right_color = (245, 245, 245)
    right_panel = Image.new('RGB', (right_w, panel_h), right_color)
    img.paste(right_panel, (left_w, 0))
    # Add semi-transparent overlay for readability
    overlay = Image.new('RGBA', (right_w, panel_h), (255,255,255,180))
    img.paste(overlay, (left_w, 0), overlay)
    draw = ImageDraw.Draw(img)

    # Title and subtitle with modern style
    rx = left_w
    y = 70
    # Draw title with shadow
    def draw_text_with_shadow(draw, text, pos, font, fill, shadow_color=(0,0,0), shadow_offset=(2,2)):
        x, y = pos
        draw.text((x+shadow_offset[0], y+shadow_offset[1]), text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=fill)
    title_font_size = 110
    subtitle_font_size = 60
    try:
        font_title = ImageFont.truetype(font_path, title_font_size)
        font_subtitle = ImageFont.truetype(font_path, subtitle_font_size)
    except Exception:
        font_title = font_subtitle = ImageFont.load_default()
    # Centered title
    title_w, title_h = draw.textbbox((0,0), title, font=font_title)[2:]
    title_x = rx + (right_w - title_w) // 2
    draw_text_with_shadow(draw, title, (title_x, y), font_title, 'black', shadow_color=(200,200,200), shadow_offset=(4,4))
    y += title_h + 20
    # Centered subtitle
    subtitle_w, subtitle_h = draw.textbbox((0,0), subtitle, font=font_subtitle)[2:]
    subtitle_x = rx + (right_w - subtitle_w) // 2
    draw_text_with_shadow(draw, subtitle, (subtitle_x, y), font_subtitle, '#1e90ff', shadow_color=(200,200,200), shadow_offset=(3,3))
    y += subtitle_h + 40

    # Stat boxes - modern style
    stat_box_h = 90
    stat_box_w = right_w - 120
    stat_box_x = rx + 60
    stat_y = y
    stat_box_color = (255,255,255,240)
    stat_shadow_color = (200,200,200,80)
    stat_label_color = (60,60,60)
    stat_value_color = accent_color or '#1e90ff'
    for label, value in zip(stat_labels, stat_values):
        # Draw drop shadow
        shadow_rect = [stat_box_x+6, stat_y+6, stat_box_x+stat_box_w+6, stat_y+stat_box_h+6]
        draw.rounded_rectangle(shadow_rect, radius=22, fill=stat_shadow_color)
        # Draw box
        draw.rounded_rectangle([stat_box_x, stat_y, stat_box_x+stat_box_w, stat_y+stat_box_h], radius=22, fill=stat_box_color)
        # Draw stat label (left, bold)
        try:
            font_stat_label = ImageFont.truetype(font_path, 38)
        except Exception:
            font_stat_label = ImageFont.load_default()
        draw.text((stat_box_x+30, stat_y+28), label, font=font_stat_label, fill=stat_label_color)
        # Draw stat value (right, large, bold, accent color)
        try:
            font_stat_value = ImageFont.truetype(font_path, 60)
        except Exception:
            font_stat_value = ImageFont.load_default()
        value_w, _ = draw.textbbox((0,0), str(value), font=font_stat_value)[2:]
        draw.text((stat_box_x+stat_box_w-60-value_w, stat_y+18), str(value), font=font_stat_value, fill=stat_value_color)
        stat_y += stat_box_h + 28
    branding_y = size[1] - 120

    # Hashtag/social handle at bottom, bold and readable
    if hashtag:
        try:
            font_hashtag = ImageFont.truetype(font_path, 44)
        except Exception:
            font_hashtag = ImageFont.load_default()
        hashtag_w, _ = draw.textbbox((0,0), hashtag, font=font_hashtag)[2:]
        hashtag_x = rx + (right_w - hashtag_w) // 2
        draw_text_with_shadow(draw, hashtag, (hashtag_x, branding_y), font_hashtag, accent_color or '#1e90ff', shadow_color=(200,200,200), shadow_offset=(2,2))
        branding_y -= 50

    # Logo in top right with shadow/overlay
    if logo_bytes and len(logo_bytes) >= 10:
        try:
            logo_img = Image.open(io.BytesIO(logo_bytes)).convert('RGBA')
            logo_size = (120, 120)
            logo_img.thumbnail(logo_size, Image.LANCZOS)
            logo_overlay = Image.new('RGBA', logo_img.size, (255,255,255,80))
            logo_img = Image.alpha_composite(logo_img, logo_overlay)
            lx = rx + right_w - logo_img.width - 30
            ly = 30
            # Draw shadow
            shadow = Image.new('RGBA', logo_img.size, (0,0,0,60))
            img.paste(shadow, (lx+4, ly+4), shadow)
            img.paste(logo_img, (lx, ly), logo_img)
        except Exception as e:
            print(f"[DEBUG] Error drawing logo: {e}")
    else:
        # fallback: draw MoundVision text
        try:
            font_brand = ImageFont.truetype(font_path, 36)
        except Exception:
            font_brand = ImageFont.load_default()
        draw_text_with_shadow(draw, "MoundVision", (rx+right_w-260, 40), font_brand, '#1e90ff', shadow_color=(200,200,200), shadow_offset=(2,2))

    # Watermark: semi-transparent diagonal 'MoundVision' in bottom right
    try:
        font_watermark = ImageFont.truetype(font_path, 60)
    except Exception:
        font_watermark = ImageFont.load_default()
    watermark_text = "MoundVision"
    watermark_img = Image.new('RGBA', (right_w, 120), (255,255,255,0))
    watermark_draw = ImageDraw.Draw(watermark_img)
    watermark_draw.text((right_w-520, 40), watermark_text, font=font_watermark, fill=(30,144,255,80))
    watermark_img = watermark_img.rotate(-20, expand=1)
    img.paste(watermark_img, (rx, size[1]-160), watermark_img)

    # Save to bytes
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type='image/png') 