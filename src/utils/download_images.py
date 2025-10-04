import requests
import json
import os
from urllib.parse import urlparse
import time

def download_image(url, filepath, timeout=30):
    """Download a single image from URL to filepath"""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def download_images_from_json(json_file, output_dir, image_type):
    """Download all images from a JSON file to a directory"""
    print(f"Loading {image_type} images from {json_file}...")
    
    with open(json_file, 'r') as f:
        images = json.load(f)
    
    print(f"Found {len(images)} {image_type} images to download")
    print(f"Downloading to: {output_dir}")
    print("=" * 60)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    successful_downloads = 0
    failed_downloads = 0
    
    for i, image in enumerate(images, 1):
        nasa_id = image['nasa_id']
        url = image['image_url']
        
        # Get file extension from URL
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1]
        
        # Create filename: nasa_id + extension
        filename = f"{nasa_id}{file_extension}"
        filepath = os.path.join(output_dir, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"{i:4d}. {nasa_id[:40]:<40} ✓ ALREADY EXISTS")
            successful_downloads += 1
            continue
        
        print(f"{i:4d}. {nasa_id[:40]:<40} ", end="")
        
        if download_image(url, filepath):
            print("✓ DOWNLOADED")
            successful_downloads += 1
        else:
            print("✗ FAILED")
            failed_downloads += 1
        
        # Small delay to be respectful to the server
        time.sleep(0.1)
        
        # Progress update every 50 images
        if i % 50 == 0:
            print(f"Progress: {i}/{len(images)} ({i/len(images)*100:.1f}%)")
    
    print("=" * 60)
    print(f"{image_type.upper()} DOWNLOAD COMPLETE:")
    print(f"  Successful: {successful_downloads}")
    print(f"  Failed: {failed_downloads}")
    print(f"  Total: {len(images)}")
    print(f"  Success rate: {successful_downloads/len(images)*100:.1f}%")
    
    return successful_downloads, failed_downloads

def main():
    """Download all images from both JSON files"""
    print("Starting image download process...")
    print("=" * 60)
    
    # Download Cupola images
    cupola_success, cupola_failed = download_images_from_json(
        'cupola_images.json', 
        'images/cupola', 
        'cupola'
    )
    
    print("\n" + "=" * 60)
    
    # Download NBL images
    nbl_success, nbl_failed = download_images_from_json(
        'nbl_images_mass.json', 
        'images/nbl', 
        'nbl'
    )
    
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY:")
    print(f"  Cupola images: {cupola_success} successful, {cupola_failed} failed")
    print(f"  NBL images: {nbl_success} successful, {nbl_failed} failed")
    print(f"  Total successful: {cupola_success + nbl_success}")
    print(f"  Total failed: {cupola_failed + nbl_failed}")
    print(f"  Total images: {cupola_success + cupola_failed + nbl_success + nbl_failed}")

if __name__ == "__main__":
    main()
