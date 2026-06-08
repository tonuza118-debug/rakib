"""Cloudinary integration test — upload, get metadata, transform."""
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Step 1 — Configure Cloudinary with your credentials
cloudinary.config(
    cloud_name="dwcazkqlm",
    api_key="112936847494325",
    api_secret="RuGdHTx9EZVYpASgkt0UJub8504",
)

# Step 2 — Upload a sample image from Cloudinary's demo collection
print("Uploading sample image...")
upload_result = cloudinary.uploader.upload(
    "https://res.cloudinary.com/demo/image/upload/sample.jpg",
    public_id="portfolio_test_sample",
    overwrite=True,
)
print("[OK] Upload successful!")
print(f"   Public ID: {upload_result['public_id']}")
print(f"   Secure URL: {upload_result['secure_url']}")

# Step 3 — Get image details (metadata)
print("\nFetching image metadata...")
resource = cloudinary.api.resource("portfolio_test_sample")
print("[OK] Image metadata:")
print(f"   Width: {resource['width']}px")
print(f"   Height: {resource['height']}px")
print(f"   Format: {resource['format']}")
print(f"   File size: {resource['bytes']} bytes")

# Step 4 — Generate a transformed image URL
# f_auto = automatic format selection (serves WebP/AVIF to supported browsers)
# q_auto = automatic quality (reduces file size without visible quality loss)
transformed_url = cloudinary.CloudinaryImage("portfolio_test_sample").build_url(
    fetch_format="f_auto",
    quality="q_auto",
    width=400,
    crop="fill",
)

print(f"\n[OK] Transformed URL:")
print(f"   {transformed_url}")
print(f"\nDone! Click the link above to see the optimized version of the image.")
print(f"Check the size and format — it should be smaller and possibly WebP/AVIF.")
