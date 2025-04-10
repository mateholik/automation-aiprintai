import os
import argparse
import requests
from PIL import Image
from woocommerce import API
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import shutil

load_dotenv()

# ====== STATIC CONFIG ======
WATERMARK_PATH = "static/watermark.png"
MOCKUP_PATH = "static/mockup.jpg"
OUTPUT_FOLDER = "out"

WATERMARK_RELATIVE_WIDTH = 0.8
WATERMARK_OPACITY = 200
MOCKUP_PASTE_COORDS = (372, 270)
MOCKUP_TARGET_SIZE = (277, 277)
OUTPUT_IMAGE_SIZE = (1024, 1024)

WC_URL = os.getenv("WC_URL")
WC_CONSUMER_KEY = os.getenv("WC_CONSUMER_KEY")
WC_CONSUMER_SECRET = os.getenv("WC_CONSUMER_SECRET")
WP_ADMIN_USERNAME = os.getenv("WP_ADMIN_USERNAME")
WP_APPLICATION_PASSWORD = os.getenv("WP_APPLICATION_PASSWORD")

STATIC_CATEGORY = {"id": 327}

with open("static/description.html", "r", encoding="utf-8") as f:
    DESCRIPTION_TEXT = f.read()
# ============================

if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)

def process_images(input_folder):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        name = os.path.splitext(filename)[0]
        img_path = os.path.join(input_folder, filename)
        product_folder = os.path.join(OUTPUT_FOLDER, name)
        os.makedirs(product_folder, exist_ok=True)

        original = Image.open(img_path).convert("RGBA")

        original.convert("RGB").save(
            os.path.join(product_folder, f"{name}_original.jpg"), quality=95, subsampling=0
        )

        watermark = Image.open(WATERMARK_PATH).convert("RGBA")
        ratio = (original.width * WATERMARK_RELATIVE_WIDTH) / watermark.width
        new_size = (int(watermark.width * ratio), int(watermark.height * ratio))
        watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)

        r, g, b, a = watermark.split()
        a = a.point(lambda p: int(p * (WATERMARK_OPACITY / 255)))
        watermark = Image.merge("RGBA", (r, g, b, a))

        pos = (
            (original.width - watermark.width) // 2,
            (original.height - watermark.height) // 2
        )

        watermarked = original.copy()
        watermarked.paste(watermark, pos, watermark)
        watermarked = watermarked.convert("RGB").resize(OUTPUT_IMAGE_SIZE, Image.Resampling.LANCZOS)
        watermarked.save(os.path.join(product_folder, f"{name}_watermarked.jpg"), quality=90)

        mockup = Image.open(MOCKUP_PATH).convert("RGBA")
        art_resized = original.resize(MOCKUP_TARGET_SIZE, Image.Resampling.LANCZOS)
        mockup.paste(art_resized, MOCKUP_PASTE_COORDS, art_resized if art_resized.mode == "RGBA" else None)
        preview = mockup.convert("RGB").resize(OUTPUT_IMAGE_SIZE, Image.Resampling.LANCZOS)
        preview.save(os.path.join(product_folder, f"{name}_preview.jpg"), quality=90)

        print(f"✅ Processed: {filename}")


def upload_image(image_path):
    url = f"{WC_URL}/wp-json/wp/v2/media"
    filename = os.path.basename(image_path)
    with open(image_path, 'rb') as img:
        files = {'file': (filename, img, 'image/jpeg')}
        headers = {'User-Agent': 'curl/7.64.1'}
        res = requests.post(url, files=files, headers=headers,
                            auth=HTTPBasicAuth(WP_ADMIN_USERNAME, WP_APPLICATION_PASSWORD))
    res.raise_for_status()
    return res.json().get('id')


def create_product(name, main_image_id, gallery_image_id, extra_categories):

    categories = [STATIC_CATEGORY] + [{"id": int(cid)} for cid in extra_categories]

    wcapi = API(
        url=WC_URL,
        consumer_key=WC_CONSUMER_KEY,
        consumer_secret=WC_CONSUMER_SECRET,
        version="wc/v3"
    )

    product_data = {
        "name": name,
        "type": "simple",
        "description": DESCRIPTION_TEXT,
        "status": "publish",
        "regular_price": "0.00",
        "categories": categories,
        "images": [
            {"id": main_image_id},
            {"id": gallery_image_id}
        ]
    }

    res = wcapi.post("products", product_data)
    res.raise_for_status()
    return res.json()


def main(input_folder, extra_categories):
    process_images(input_folder)

    for folder in os.listdir(OUTPUT_FOLDER):
        folder_path = os.path.join(OUTPUT_FOLDER, folder)
        if os.path.isdir(folder_path):
            print(f"\n📦 Creating product: {folder}")
            watermarked_img = os.path.join(folder_path, f"{folder}_watermarked.jpg")
            preview_img = os.path.join(folder_path, f"{folder}_preview.jpg")

            if os.path.exists(watermarked_img) and os.path.exists(preview_img):
                try:
                    main_id = upload_image(watermarked_img)
                    preview_id = upload_image(preview_img)
                    product = create_product(folder, main_id, preview_id, extra_categories)
                    print(f"✅ Created product '{folder}' (ID: {product['id']})")
                except Exception as e:
                    print(f"❌ Failed for '{folder}': {e}")
            else:
                print(f"⚠️ Skipped '{folder}' — images missing.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to image input folder")
    parser.add_argument("--categories", nargs='*', type=int, default=[])
    args = parser.parse_args()
    main(args.input, args.categories)
