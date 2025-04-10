from PIL import Image
import os
import logging

# ====== CONFIG ======
TARGET_KEYWORD = "water"
SAVE_QUALITY = 90
# =====================

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

start_path = "/Users/mateholik/Desktop/ai_printai/aiprintai_2025_midjourney_sets/2025_3_Giedre_geles/ready"  # current directory

try:
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
                        logging.info(f"✅ Optimized: {file_path}")
                except Exception as e:
                    logging.error(f"❌ Failed to optimize {file_path}: {e}")
except FileNotFoundError as fnf_error:
    logging.error(f"❌ Directory not found: {fnf_error}")
except PermissionError as perm_error:
    logging.error(f"❌ Permission denied: {perm_error}")
except Exception as e:
    logging.error(f"❌ An unexpected error occurred: {e}")

logging.info("🎉 All matching 'Group' images optimized recursively from current folder.")
