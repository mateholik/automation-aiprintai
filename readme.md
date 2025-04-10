# AUTOMATION Files Project

This project automates the processing of images and the creation of products in WooCommerce.

## Prerequisites
1. Install Python 3.x.
2. Install the following required Python libraries:
   ```bash
   pip install python-dotenv Pillow woocommerce requests
   ```
3. Create a `.env` file in the project root with the following variables:
   ```env
   WC_URL=<your_woocommerce_url>
   WC_CONSUMER_KEY=<your_consumer_key>
   WC_CONSUMER_SECRET=<your_consumer_secret>
   WP_ADMIN_USERNAME=<your_wp_admin_username>
   WP_APPLICATION_PASSWORD=<your_wp_application_password>
   ```

## Usage
1. Prepare your input images in a folder.
2. Run the script with the following command:
   ```bash
   python3 init.py --input <path_to_input_folder> --categories <category_ids>
   ```
   - Replace `<path_to_input_folder>` with the path to your folder containing images.
   - Replace `<category_ids>` with space-separated WooCommerce category IDs.

## Output
- Processed images and previews will be saved in the `out/` folder.
- Products will be created in WooCommerce with the processed images.

## Notes
- Ensure the `static/mockup.jpg` and `static/watermark.png` files are correctly configured for your use case.
- Do not commit the `.env` file or sensitive data to version control.

## EXAMPLE
```
python3 init.py --input "/Users/mateholik/Desktop/ai_printai/aiprintai_2025_midjourney_sets/gyvunai" --categories 267
  ```