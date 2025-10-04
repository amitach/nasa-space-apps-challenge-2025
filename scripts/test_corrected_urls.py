import requests
import json

def validate_image_url(url, timeout=10):
    """
    Validate that an image URL is accessible and returns a valid image.
    Returns True if accessible, False otherwise.
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            # Check if it's an image
            if content_type.startswith('image/'):
                return True
        return False
    except Exception as e:
        print(f"URL validation failed for {url}: {e}")
        return False

# Test with corrected URLs using uppercase JPG
test_urls = [
    "https://images-assets.nasa.gov/image/JSC-20160920-PH_JNB01_0001/JSC-20160920-PH_JNB01_0001~orig.JPG",
    "https://images-assets.nasa.gov/image/JSC-20160920-PH_JNB01_0002/JSC-20160920-PH_JNB01_0002~orig.JPG",
    "https://images-assets.nasa.gov/image/JSC-20160920-PH_JNB01_0003/JSC-20160920-PH_JNB01_0003~orig.JPG"
]

print("Testing corrected URL validation...")
for url in test_urls:
    print(f"Testing: {url}")
    is_valid = validate_image_url(url)
    print(f"Result: {'✓ Valid' if is_valid else '✗ Invalid'}")
    print()
