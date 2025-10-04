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

def test_both_cases():
    """Test both .JPG and .jpg cases and update the JSON with working URLs"""
    with open('nbl_images.json', 'r') as f:
        images = json.load(f)
    
    working_count = 0
    total_count = len(images)
    updated_images = []
    
    print(f"Testing {total_count} NBL image URLs with both .JPG and .jpg cases...")
    print("=" * 70)
    
    for i, image in enumerate(images, 1):
        nasa_id = image['nasa_id']
        base_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~orig"
        
        # Test both cases
        jpg_url = base_url + ".jpg"
        JPG_url = base_url + ".JPG"
        
        print(f"{i:2d}. {nasa_id[:30]:<30} ", end="")
        
        # Test lowercase .jpg first
        if test_image_url(jpg_url):
            print("✓ WORKING (.jpg)")
            image['image_url'] = jpg_url
            working_count += 1
        # If .jpg doesn't work, try .JPG
        elif test_image_url(JPG_url):
            print("✓ WORKING (.JPG)")
            image['image_url'] = JPG_url
            working_count += 1
        else:
            print("✗ FAILED (both cases)")
        
        updated_images.append(image)
        
        # Small delay to be respectful to the server
        time.sleep(0.1)
    
    # Save the updated JSON with working URLs
    with open('nbl_images.json', 'w') as f:
        json.dump(updated_images, f, indent=2)
    
    print("=" * 70)
    print(f"Results: {working_count}/{total_count} images are working ({working_count/total_count*100:.1f}%)")
    print("Updated nbl_images.json with working URLs")
    
    return working_count, total_count

if __name__ == "__main__":
    test_both_cases()
