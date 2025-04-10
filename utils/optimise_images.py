from PIL import Image
import os

# ====== CONFIG ======
TARGET_KEYWORD = "water"
SAVE_QUALITY = 90
# =====================

start_path = "/Users/mateholik/Desktop/ai_printai/aiprintai_2025_midjourney_sets/2025_3_Giedre_geles/ready"  # current directory

for root, dirs, files in os.walk(start_path):
    for file in files:
        if TARGET_KEYWORD.lower() in file.lower() and file.lower().endswith((".jpg", ".jpeg", ".png")):
            file_path = os.path.join(root, file)

            try:
                with Image.open(file_path) as img:
                    img = img.convert("RGB")
                    img.save(
                        file_path,
                        format="JPEG",
                        quality=SAVE_QUALITY,
                        optimize=True,
                        progressive=True
                    )
                    print(f"✅ Optimized: {file_path}")
            except Exception as e:
                print(f"❌ Failed to optimize {file_path}: {e}")

print("🎉 All matching 'Group' images optimized recursively from current folder.")
