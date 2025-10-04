import requests
import json
import time

def test_image_url(url, timeout=5):
    """Test if an image URL returns 200 and is accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except Exception as e:
        return False

def test_all_nbl_images():
    """Test all image URLs in nbl_images.json"""
    with open('nbl_images.json', 'r') as f:
        images = json.load(f)
    
    working_count = 0
    total_count = len(images)
    
    print(f"Testing {total_count} NBL image URLs...")
    print("=" * 60)
    
    for i, image in enumerate(images, 1):
        nasa_id = image['nasa_id']
        url = image['image_url']
        
        print(f"{i:2d}. {nasa_id[:30]:<30} ", end="")
        
        is_working = test_image_url(url)
        
        if is_working:
            print("✓ WORKING")
            working_count += 1
        else:
            print("✗ FAILED")
        
        # Small delay to be respectful to the server
        time.sleep(0.1)
    
    print("=" * 60)
    print(f"Results: {working_count}/{total_count} images are working ({working_count/total_count*100:.1f}%)")
    
    return working_count, total_count

if __name__ == "__main__":
    test_all_nbl_images()
