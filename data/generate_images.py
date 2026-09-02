import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_images():
    output_dir = os.path.join(os.path.dirname(__file__), "sample_images")
    os.makedirs(output_dir, exist_ok=True)

    images = {
        "solar_panel_clean.jpg": {"title": "Clean Panel Array", "status": "Clean", "color": "#1e40af", "defect": None},
        "solar_panel_cracked.jpg": {"title": "Micro-Crack Anomaly", "status": "Crack Defect", "color": "#1e3a8a", "defect": "crack"},
        "solar_panel_dusty.jpg": {"title": "Heavy Soiling Accumulation", "status": "Dust Defect", "color": "#78350f", "defect": "dust"},
        "solar_panel_hotspot.jpg": {"title": "Thermal Hotspot Anomaly", "status": "Hotspot Defect", "color": "#991b1b", "defect": "hotspot"},
        "solar_panel_debris.jpg": {"title": "Bird Debris Obstruction", "status": "Debris Defect", "color": "#374151", "defect": "debris"},
    }

    width, height = 600, 450

    for filename, info in images.items():
        img = Image.new("RGB", (width, height), color="#f1f5f9")
        draw = ImageDraw.Draw(img)

        # Draw Solar Panel Frame
        margin = 30
        draw.rectangle([margin, margin, width - margin, height - margin], fill="#0f172a", outline="#94a3b8", width=4)

        # Draw Grid Cells (3x4 solar cells)
        rows, cols = 3, 4
        cell_w = (width - 2 * margin - 20) / cols
        cell_h = (height - 2 * margin - 20) / rows

        for r in range(rows):
            for c in range(cols):
                x1 = margin + 10 + c * cell_w + 3
                y1 = margin + 10 + r * cell_h + 3
                x2 = x1 + cell_w - 6
                y2 = y1 + cell_h - 6
                
                # Base panel cell blue
                draw.rectangle([x1, y1, x2, y2], fill="#1e3a8a", outline="#60a5fa", width=1)
                
                # Draw solar gridlines
                draw.line([(x1 + x2)/2, y1, (x1 + x2)/2, y2], fill="#93c5fd", width=1)
                draw.line([x1, (y1 + y2)/2, x2, (y1 + y2)/2], fill="#93c5fd", width=1)

        # Overlay specific defects visually
        if info["defect"] == "crack":
            # Draw crack lines
            cx, cy = width / 2, height / 2
            draw.line([cx - 80, cy - 40, cx + 20, cy + 10], fill="#f87171", width=3)
            draw.line([cx + 20, cy + 10, cx + 90, cy + 60], fill="#ef4444", width=3)
            draw.line([cx + 20, cy + 10, cx + 50, cy - 30], fill="#f87171", width=2)
            draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline="#ef4444", width=2)

        elif info["defect"] == "dust":
            # Draw brownish translucent dust layer
            draw.rectangle([margin + 40, margin + 40, width - margin - 40, height - margin - 40], fill="#b4530980", outline="#d97706")
            for i in range(margin + 50, width - margin - 50, 15):
                for j in range(margin + 50, height - margin - 50, 15):
                    draw.ellipse([i, j, i+4, j+4], fill="#78350f")

        elif info["defect"] == "hotspot":
            # Draw bright red glowing thermal hotspot
            cx, cy = width * 0.6, height * 0.4
            draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill="#dc2626")
            draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill="#f59e0b")
            draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill="#fef08a")

        elif info["defect"] == "debris":
            # Draw white/gray debris spots
            draw.polygon([(200, 150), (230, 140), (250, 170), (210, 180)], fill="#e2e8f0", outline="#94a3b8")
            draw.polygon([(340, 260), (370, 250), (380, 280), (350, 290)], fill="#cbd5e1", outline="#64748b")

        # Top banner text label
        draw.rectangle([0, 0, width, 36], fill="#ffffff")
        draw.text((15, 8), f"DRONE CAM 04 | {info['title']}", fill="#0f172a")

        filepath = os.path.join(output_dir, filename)
        img.save(filepath, quality=95)
        print(f"Generated sample image: {filepath}")

if __name__ == "__main__":
    generate_sample_images()
