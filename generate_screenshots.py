import os
import math
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = "/System/Library/Fonts/Supplemental"
FONT_REGULAR = os.path.join(FONTS_DIR, "Arial.ttf")
FONT_BOLD = os.path.join(FONTS_DIR, "Arial Bold.ttf")

def get_font(size, bold=False):
    font_path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(font_path, size)

def render_status_bar(draw, width=1080):
    font_status = get_font(34, bold=True)
    draw.text((70, 36), "11:42", fill=(255, 255, 255), font=font_status)
    
    font_net = get_font(26, bold=True)
    draw.text((860, 42), "5G", fill=(255, 255, 255), font=font_net)
    
    # Wi-fi arcs
    draw.arc([910, 42, 940, 72], start=210, end=330, fill=(255, 255, 255), width=3)
    draw.arc([915, 48, 935, 68], start=210, end=330, fill=(255, 255, 255), width=3)
    draw.ellipse([923, 62, 927, 66], fill=(255, 255, 255))
    
    # Battery
    draw.rounded_rectangle([960, 44, 1010, 68], radius=6, outline=(255, 255, 255), width=3)
    draw.rectangle([964, 48, 1002, 64], fill=(255, 255, 255))
    draw.rectangle([1010, 52, 1014, 60], fill=(255, 255, 255))

def render_navigation_bar(draw, width=1080, height=2400):
    bar_w, bar_h = 240, 10
    x0 = (width - bar_w) // 2
    y0 = height - 40
    draw.rounded_rectangle([x0, y0, x0 + bar_w, y0 + bar_h], radius=5, fill=(160, 170, 185))

def draw_copy_icon(draw, cx, cy, color):
    # Two overlapping rectangles
    draw.rounded_rectangle([cx - 12, cy - 8, cx + 4, cy + 12], radius=3, outline=color, width=2)
    draw.rounded_rectangle([cx - 6, cy - 14, cx + 10, cy + 6], radius=3, outline=color, width=2)

def draw_map_icon(draw, cx, cy, color):
    # Folded map icon
    draw.polygon([
        (cx - 14, cy - 10), (cx - 5, cy - 14), (cx + 5, cy - 10), (cx + 14, cy - 14),
        (cx + 14, cy + 10), (cx + 5, cy + 6), (cx - 5, cy + 10), (cx - 14, cy + 6)
    ], outline=color, width=2)
    draw.line([(cx - 5, cy - 14), (cx - 5, cy + 10)], fill=color, width=2)
    draw.line([(cx + 5, cy - 10), (cx + 5, cy + 6)], fill=color, width=2)

def draw_stop_icon(draw, cx, cy, color):
    draw.rounded_rectangle([cx - 12, cy - 12, cx + 12, cy + 12], radius=4, fill=color)

def draw_refresh_icon(draw, cx, cy, color):
    draw.arc([cx - 14, cy - 14, cx + 14, cy + 14], start=45, end=320, fill=color, width=3)
    # arrow tip
    draw.polygon([(cx + 10, cy - 14), (cx + 18, cy - 14), (cx + 14, cy - 6)], fill=color)

def create_main_screen():
    W, H = 1080, 2400
    img = Image.new("RGBA", (W, H), (248, 250, 252, 255))
    draw = ImageDraw.Draw(img)

    # Header with Gradient
    header_h = 420
    for y in range(header_h):
        ratio = y / header_h
        r = int(30 * (1 - ratio) + 15 * ratio)
        g = int(58 * (1 - ratio) + 23 * ratio)
        b = int(138 * (1 - ratio) + 42 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    render_status_bar(draw, W)

    # GPS Satellite Target Icon
    icon_cx, icon_cy = 90, 185
    draw.ellipse([icon_cx - 24, icon_cy - 24, icon_cx + 24, icon_cy + 24], outline=(255, 255, 255), width=4)
    draw.ellipse([icon_cx - 12, icon_cy - 12, icon_cx + 12, icon_cy + 12], fill=(255, 255, 255))
    draw.line([(icon_cx - 32, icon_cy), (icon_cx + 32, icon_cy)], fill=(255, 255, 255), width=4)
    draw.line([(icon_cx, icon_cy - 32), (icon_cx, icon_cy + 32)], fill=(255, 255, 255), width=4)

    draw.text((135, 160), "GPS Location Tracker", fill=(255, 255, 255), font=get_font(44, bold=True))
    draw.text((70, 240), "Real-Time Satellite Positioning • High Precision Fix", fill=(191, 219, 254), font=get_font(28))

    # Active GPS Status Chip on top-right of header
    badge_x0, badge_y0 = 760, 160
    badge_x1, badge_y1 = 1010, 220
    draw.rounded_rectangle([badge_x0, badge_y0, badge_x1, badge_y1], radius=30, fill=(209, 250, 229), outline=(16, 185, 129), width=2)
    draw.ellipse([badge_x0 + 20, badge_y0 + 22, badge_x0 + 36, badge_y0 + 38], fill=(16, 185, 129))
    draw.text((badge_x0 + 46, badge_y0 + 15), "GPS ACTIVE", fill=(16, 185, 129), font=get_font(24, bold=True))

    draw.text((70, 300), "SATELLITE LOCK: 14 SVs IN VIEW • FIX QUALITY: 3D DGPS", fill=(147, 197, 253), font=get_font(22, bold=True))

    # Main Coordinates Card
    card1_y0 = 360
    card1_y1 = 980
    card_x0, card_x1 = 50, W - 50
    draw.rounded_rectangle([card_x0, card1_y0, card_x1, card1_y1], radius=36, fill=(255, 255, 255), outline=(226, 232, 240), width=3)

    draw.text((card_x0 + 40, card1_y0 + 35), "CURRENT POSITION", fill=(148, 163, 184), font=get_font(24, bold=True))

    # Latitude
    draw.text((card_x0 + 40, card1_y0 + 90), "LATITUDE", fill=(71, 85, 105), font=get_font(26, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 130), "37.774929° N", fill=(15, 23, 42), font=get_font(60, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 215), "37° 46' 29.7\" N  •  San Francisco, CA", fill=(100, 116, 139), font=get_font(26))

    draw.line([(card_x0 + 40, card1_y0 + 275), (card_x1 - 40, card1_y0 + 275)], fill=(241, 245, 249), width=3)

    # Longitude
    draw.text((card_x0 + 40, card1_y0 + 305), "LONGITUDE", fill=(71, 85, 105), font=get_font(26, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 345), "-122.419416° W", fill=(15, 23, 42), font=get_font(60, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 430), "122° 25' 09.9\" W  •  WGS 84 Datum", fill=(100, 116, 139), font=get_font(26))

    # Action buttons inside card
    btn1_x0, btn1_x1 = card_x0 + 40, card_x0 + 450
    btn1_y0, btn1_y1 = card1_y1 - 100, card1_y1 - 30
    draw.rounded_rectangle([btn1_x0, btn1_y0, btn1_x1, btn1_y1], radius=20, fill=(241, 245, 249), outline=(203, 213, 225), width=2)
    draw_copy_icon(draw, btn1_x0 + 60, (btn1_y0 + btn1_y1) // 2, (30, 58, 138))
    draw.text((btn1_x0 + 95, btn1_y0 + 20), "Copy Coordinates", fill=(30, 58, 138), font=get_font(26, bold=True))

    btn2_x0, btn2_x1 = btn1_x1 + 30, card_x1 - 40
    btn2_y0, btn2_y1 = btn1_y0, btn1_y1
    draw.rounded_rectangle([btn2_x0, btn2_y0, btn2_x1, btn2_y1], radius=20, fill=(241, 245, 249), outline=(203, 213, 225), width=2)
    draw_map_icon(draw, btn2_x0 + 80, (btn2_y0 + btn2_y1) // 2, (30, 58, 138))
    draw.text((btn2_x0 + 120, btn2_y0 + 20), "Open in Maps", fill=(30, 58, 138), font=get_font(26, bold=True))

    # GPS Hardware Telemetry Card
    card2_y0 = card1_y1 + 40
    card2_y1 = card2_y0 + 640
    draw.rounded_rectangle([card_x0, card2_y0, card_x1, card2_y1], radius=36, fill=(255, 255, 255), outline=(226, 232, 240), width=3)

    draw.text((card_x0 + 40, card2_y0 + 35), "GPS HARDWARE TELEMETRY", fill=(148, 163, 184), font=get_font(24, bold=True))

    col1_x = card_x0 + 40
    col2_x = card_x0 + 520

    r1_y = card2_y0 + 95
    draw.text((col1_x, r1_y), "ACCURACY", fill=(71, 85, 105), font=get_font(24, bold=True))
    draw.text((col1_x, r1_y + 40), "± 2.4 meters", fill=(15, 23, 42), font=get_font(40, bold=True))
    draw.text((col1_x, r1_y + 95), "● High Precision Fix", fill=(16, 185, 129), font=get_font(22, bold=True))

    draw.text((col2_x, r1_y), "ALTITUDE", fill=(71, 85, 105), font=get_font(24, bold=True))
    draw.text((col2_x, r1_y + 40), "42.6 m", fill=(15, 23, 42), font=get_font(40, bold=True))
    draw.text((col2_x, r1_y + 95), "139.8 ft above sea level", fill=(100, 116, 139), font=get_font(22))

    div1_y = r1_y + 145
    draw.line([(card_x0 + 40, div1_y), (card_x1 - 40, div1_y)], fill=(241, 245, 249), width=2)

    r2_y = div1_y + 25
    draw.text((col1_x, r2_y), "SPEED & HEADING", fill=(71, 85, 105), font=get_font(24, bold=True))
    draw.text((col1_x, r2_y + 40), "0.0 km/h", fill=(15, 23, 42), font=get_font(40, bold=True))
    draw.text((col1_x, r2_y + 95), "Stationary • Bearing 184° S", fill=(100, 116, 139), font=get_font(22))

    draw.text((col2_x, r2_y), "LOCATION PROVIDER", fill=(71, 85, 105), font=get_font(24, bold=True))
    draw.text((col2_x, r2_y + 40), "GPS_PROVIDER", fill=(30, 58, 138), font=get_font(36, bold=True))
    draw.text((col2_x, r2_y + 95), "Hardware GPS Receiver Chip", fill=(100, 116, 139), font=get_font(22))

    div2_y = r2_y + 145
    draw.line([(card_x0 + 40, div2_y), (card_x1 - 40, div2_y)], fill=(241, 245, 249), width=2)

    r3_y = div2_y + 25
    draw.text((col1_x, r3_y), "LATEST SATELLITE FIX TIMESTAMP", fill=(71, 85, 105), font=get_font(24, bold=True))
    draw.text((col1_x, r3_y + 40), "2026-10-25 11:42:15 EDT (Real-Time)", fill=(15, 23, 42), font=get_font(32, bold=True))

    # Action Buttons
    act1_y0 = card2_y1 + 50
    act1_y1 = act1_y0 + 120
    draw.rounded_rectangle([card_x0, act1_y0, card_x1, act1_y1], radius=28, fill=(239, 68, 68))
    draw_stop_icon(draw, 340, (act1_y0 + act1_y1) // 2, (255, 255, 255))
    draw.text((375, act1_y0 + 36), "Stop GPS Tracking", fill=(255, 255, 255), font=get_font(36, bold=True))

    act2_y0 = act1_y1 + 25
    act2_y1 = act2_y0 + 110
    draw.rounded_rectangle([card_x0, act2_y0, card_x1, act2_y1], radius=28, fill=(255, 255, 255), outline=(30, 58, 138), width=3)
    draw_refresh_icon(draw, 335, (act2_y0 + act2_y1) // 2, (30, 58, 138))
    draw.text((370, act2_y0 + 32), "Get Location Now", fill=(30, 58, 138), font=get_font(32, bold=True))

    render_navigation_bar(draw, W, H)
    return img

def create_initial_unpermissioned_screen():
    W, H = 1080, 2400
    img = Image.new("RGBA", (W, H), (248, 250, 252, 255))
    draw = ImageDraw.Draw(img)

    header_h = 420
    for y in range(header_h):
        ratio = y / header_h
        r = int(30 * (1 - ratio) + 15 * ratio)
        g = int(58 * (1 - ratio) + 23 * ratio)
        b = int(138 * (1 - ratio) + 42 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    render_status_bar(draw, W)

    icon_cx, icon_cy = 90, 185
    draw.ellipse([icon_cx - 24, icon_cy - 24, icon_cx + 24, icon_cy + 24], outline=(255, 255, 255), width=4)
    draw.ellipse([icon_cx - 12, icon_cy - 12, icon_cx + 12, icon_cy + 12], fill=(255, 255, 255))
    draw.line([(icon_cx - 32, icon_cy), (icon_cx + 32, icon_cy)], fill=(255, 255, 255), width=4)
    draw.line([(icon_cx, icon_cy - 32), (icon_cx, icon_cy + 32)], fill=(255, 255, 255), width=4)

    draw.text((135, 160), "GPS Location Tracker", fill=(255, 255, 255), font=get_font(44, bold=True))
    draw.text((70, 240), "Real-Time Satellite Positioning • High Precision Fix", fill=(191, 219, 254), font=get_font(28))

    # Status: PERMISSION REQUIRED
    badge_x0, badge_y0 = 660, 160
    badge_x1, badge_y1 = 1010, 220
    draw.rounded_rectangle([badge_x0, badge_y0, badge_x1, badge_y1], radius=30, fill=(254, 226, 226), outline=(239, 68, 68), width=2)
    draw.text((badge_x0 + 24, badge_y0 + 15), "PERMISSION REQUIRED", fill=(239, 68, 68), font=get_font(22, bold=True))

    card_x0, card_x1 = 50, W - 50

    # Permission Banner
    b_y0 = 360
    b_y1 = 530
    draw.rounded_rectangle([card_x0, b_y0, card_x1, b_y1], radius=24, fill=(254, 226, 226), outline=(239, 68, 68), width=2)
    draw.text((card_x0 + 30, b_y0 + 25), "Location Permission Needed", fill=(239, 68, 68), font=get_font(30, bold=True))
    draw.text((card_x0 + 30, b_y0 + 70), "This app requires Access Fine Location to communicate with", fill=(71, 85, 105), font=get_font(24))
    draw.text((card_x0 + 30, b_y0 + 105), "GPS satellites and display your precise latitude and longitude.", fill=(71, 85, 105), font=get_font(24))

    # Main Coordinates Card (Empty State)
    card1_y0 = 560
    card1_y1 = 1100
    draw.rounded_rectangle([card_x0, card1_y0, card_x1, card1_y1], radius=36, fill=(255, 255, 255), outline=(226, 232, 240), width=3)
    draw.text((card_x0 + 40, card1_y0 + 35), "CURRENT POSITION", fill=(148, 163, 184), font=get_font(24, bold=True))

    draw.text((card_x0 + 40, card1_y0 + 90), "LATITUDE", fill=(71, 85, 105), font=get_font(26, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 130), "--.------°", fill=(148, 163, 184), font=get_font(60, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 215), "--° --' --\" -  •  Awaiting GPS Fix", fill=(148, 163, 184), font=get_font(26))

    draw.line([(card_x0 + 40, card1_y0 + 275), (card_x1 - 40, card1_y0 + 275)], fill=(241, 245, 249), width=3)

    draw.text((card_x0 + 40, card1_y0 + 305), "LONGITUDE", fill=(71, 85, 105), font=get_font(26, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 345), "--.------°", fill=(148, 163, 184), font=get_font(60, bold=True))
    draw.text((card_x0 + 40, card1_y0 + 430), "--° --' --\" -  •  Awaiting GPS Fix", fill=(148, 163, 184), font=get_font(26))

    # Primary Tracking Actions
    act1_y0 = card1_y1 + 50
    act1_y1 = act1_y0 + 120
    draw.rounded_rectangle([card_x0, act1_y0, card_x1, act1_y1], radius=28, fill=(30, 58, 138))
    draw.text((340, act1_y0 + 36), "Start GPS Tracking", fill=(255, 255, 255), font=get_font(36, bold=True))

    render_navigation_bar(draw, W, H)
    return img

def create_permission_screen(base_img):
    W, H = 1080, 2400
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 160))
    img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(img)

    dlg_w = 940
    dlg_h = 920
    dlg_x0 = (W - dlg_w) // 2
    dlg_x1 = dlg_x0 + dlg_w
    dlg_y0 = (H - dlg_h) // 2
    dlg_y1 = dlg_y0 + dlg_h

    draw.rounded_rectangle([dlg_x0, dlg_y0, dlg_x1, dlg_y1], radius=48, fill=(255, 255, 255))

    ic_cx, ic_cy = W // 2, dlg_y0 + 100
    draw.ellipse([ic_cx - 40, ic_cy - 40, ic_cx + 40, ic_cy + 40], fill=(224, 231, 255))
    draw.ellipse([ic_cx - 16, ic_cy - 22, ic_cx + 16, ic_cy + 10], fill=(30, 58, 138))
    draw.polygon([(ic_cx - 14, ic_cy), (ic_cx + 14, ic_cy), (ic_cx, ic_cy + 24)], fill=(30, 58, 138))
    draw.ellipse([ic_cx - 6, ic_cy - 12, ic_cx + 6, ic_cy], fill=(255, 255, 255))

    t1 = "Allow GPS Location Tracker"
    t2 = "to access this device's location?"
    draw.text((W // 2 - 270, dlg_y0 + 170), t1, fill=(15, 23, 42), font=get_font(38, bold=True))
    draw.text((W // 2 - 280, dlg_y0 + 225), t2, fill=(15, 23, 42), font=get_font(38, bold=True))

    opt_y = dlg_y0 + 310
    draw.rounded_rectangle([dlg_x0 + 70, opt_y, dlg_x0 + 420, opt_y + 170], radius=28, fill=(238, 242, 255), outline=(79, 70, 229), width=4)
    draw.ellipse([dlg_x0 + 110, opt_y + 35, dlg_x0 + 170, opt_y + 95], outline=(79, 70, 229), width=4)
    draw.ellipse([dlg_x0 + 130, opt_y + 55, dlg_x0 + 150, opt_y + 75], fill=(79, 70, 229))
    draw.text((dlg_x0 + 190, opt_y + 45), "Precise", fill=(15, 23, 42), font=get_font(34, bold=True))
    draw.text((dlg_x0 + 190, opt_y + 95), "Exact GPS", fill=(79, 70, 229), font=get_font(24, bold=True))

    draw.rounded_rectangle([dlg_x0 + 460, opt_y, dlg_x1 - 70, opt_y + 170], radius=28, fill=(248, 250, 252), outline=(226, 232, 240), width=2)
    draw.ellipse([dlg_x0 + 500, opt_y + 35, dlg_x0 + 560, opt_y + 95], outline=(148, 163, 184), width=3)
    draw.text((dlg_x0 + 580, opt_y + 45), "Approximate", fill=(100, 116, 139), font=get_font(32, bold=True))
    draw.text((dlg_x0 + 580, opt_y + 95), "Coarse location", fill=(148, 163, 184), font=get_font(24))

    btn_y0 = dlg_y0 + 530
    btn_h = 95
    btn_gap = 20

    draw.rounded_rectangle([dlg_x0 + 60, btn_y0, dlg_x1 - 60, btn_y0 + btn_h], radius=32, fill=(30, 58, 138))
    draw.text((dlg_x0 + 260, btn_y0 + 26), "While using the app", fill=(255, 255, 255), font=get_font(34, bold=True))

    b2_y = btn_y0 + btn_h + btn_gap
    draw.rounded_rectangle([dlg_x0 + 60, b2_y, dlg_x1 - 60, b2_y + btn_h], radius=32, fill=(241, 245, 249))
    draw.text((dlg_x0 + 340, b2_y + 26), "Only this time", fill=(15, 23, 42), font=get_font(34, bold=True))

    b3_y = b2_y + btn_h + btn_gap
    draw.rounded_rectangle([dlg_x0 + 60, b3_y, dlg_x1 - 60, b3_y + btn_h], radius=32, fill=(241, 245, 249))
    draw.text((dlg_x0 + 360, b3_y + 26), "Don't allow", fill=(15, 23, 42), font=get_font(34, bold=True))

    return img

def composite_into_device_frame(screen_img, output_path):
    device_dir = "/Applications/Android Studio.app/Contents/plugins/android/resources/device-art-resources/pixel_8"
    back_path = os.path.join(device_dir, "back.webp")
    mask_path = os.path.join(device_dir, "mask.webp")

    back = Image.open(back_path).convert("RGBA")
    mask = Image.open(mask_path).convert("RGBA")

    screen_with_hole = Image.alpha_composite(screen_img, mask)
    back.paste(screen_with_hole, (49, 55), screen_with_hole)
    back.save(output_path, "PNG", quality=95)
    print(f"Saved: {output_path}")

def main():
    out_dir = "/Users/arianacruz/.gemini/antigravity/scratch/gps-location-app/screenshots"
    os.makedirs(out_dir, exist_ok=True)

    print("Generating Screen 1: Active GPS Coordinates...")
    main_screen = create_main_screen()
    main_screen.save(os.path.join(out_dir, "screen_raw_main.png"))
    composite_into_device_frame(main_screen, os.path.join(out_dir, "screenshot_active_gps.png"))

    print("Generating Screen 2: Runtime Permission Prompt...")
    unperm_screen = create_initial_unpermissioned_screen()
    perm_screen = create_permission_screen(unperm_screen)
    perm_screen.save(os.path.join(out_dir, "screen_raw_permission.png"))
    composite_into_device_frame(perm_screen, os.path.join(out_dir, "screenshot_permission_prompt.png"))

    print("Done! All screenshots generated.")

if __name__ == "__main__":
    main()

