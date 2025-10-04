import requests
import json
import time
import sys
from urllib.parse import urlparse

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

def get_nbl_images(max_results=1000):
    images = {}
    page = 1
    results_per_page = 100
    total_fetched = 0
    consecutive_errors = 0
    max_consecutive_errors = 5
    retry_delay = 5  # seconds

    print(f"Starting to fetch NBL images (target: {max_results})...")
    
    while total_fetched < max_results:
        try:
            url = (
                f"https://images-api.nasa.gov/search"
                f"?q=nbl&media_type=image"
                f"&year_start=1920&year_end=2025"
                f"&page_size={results_per_page}&page={page}"
            )
            
            print(f"Fetching page {page}...")
            resp = requests.get(url, timeout=30)
            
            # Check for HTTP errors
            if resp.status_code != 200:
                print(f"HTTP Error {resp.status_code}: {resp.reason}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print(f"Too many consecutive errors ({consecutive_errors}). Stopping.")
                    break
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            
            data = resp.json()
            items = data.get('collection', {}).get('items', [])
            
            if not items:
                print("No more items found. Reached end of results.")
                break
            
            page_images_added = 0
            for item in items:
                nasa_id = item['data'][0]['nasa_id']
                description = item['data'][0].get('description', '')
                
                # Try to find the best available image URL
                orig_url = None
                
                # First, try to get the original image URL from links
                for link in item.get('links', []):
                    if link['rel'] == 'canonical':
                        # Use the canonical link which should be the original
                        orig_url = link['href']
                        break
                    elif link['rel'] == 'preview':
                        preview_url = link['href']
                        # Convert preview URL to original URL with correct case
                        if '~medium.jpg' in preview_url:
                            orig_url = preview_url.replace('~medium.jpg', '~orig.JPG')
                        elif '~small.jpg' in preview_url:
                            orig_url = preview_url.replace('~small.jpg', '~orig.JPG')
                        elif '~thumb.jpg' in preview_url:
                            orig_url = preview_url.replace('~thumb.jpg', '~orig.JPG')
                        elif '~large.jpg' in preview_url:
                            orig_url = preview_url.replace('~large.jpg', '~orig.JPG')
                        break
                
                # If no link found, construct the URL manually with correct case
                if not orig_url:
                    orig_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~orig.JPG"
                
                # Validate the URL before adding to our collection
                if nasa_id not in images:
                    print(f"Validating URL for {nasa_id}...")
                    if validate_image_url(orig_url):
                        images[nasa_id] = {
                            "nasa_id": nasa_id,
                            "description": description,
                            "image_url": orig_url
                        }
                        total_fetched += 1
                        page_images_added += 1
                        print(f"✓ Valid image added: {nasa_id}")
                    else:
                        print(f"✗ Invalid image URL skipped: {nasa_id}")
                    
                    if total_fetched >= max_results:
                        break
            
            print(f"Page {page}: Added {page_images_added} new images (Total: {total_fetched})")
            
            # Reset error counter on successful request
            consecutive_errors = 0
            
            # Save progress every 10 pages
            if page % 10 == 0:
                unique_images = list(images.values())
                with open('nbl_images.json', 'w') as f:
                    json.dump(unique_images, f, indent=2)
                print(f"Progress saved: {len(unique_images)} images so far")
            
            page += 1
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            consecutive_errors += 1
            print(f"Request error: {e}")
            if consecutive_errors >= max_consecutive_errors:
                print(f"Too many consecutive errors ({consecutive_errors}). Stopping.")
                break
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            
        except json.JSONDecodeError as e:
            consecutive_errors += 1
            print(f"JSON decode error: {e}")
            if consecutive_errors >= max_consecutive_errors:
                print(f"Too many consecutive errors ({consecutive_errors}). Stopping.")
                break
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            
        except KeyboardInterrupt:
            print("\nInterrupted by user. Saving current progress...")
            break
            
        except Exception as e:
            consecutive_errors += 1
            print(f"Unexpected error: {e}")
            if consecutive_errors >= max_consecutive_errors:
                print(f"Too many consecutive errors ({consecutive_errors}). Stopping.")
                break
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    # Convert dictionary to list for JSON output
    unique_images = list(images.values())
    
    # Save final results to JSON file
    with open('nbl_images.json', 'w') as f:
        json.dump(unique_images, f, indent=2)
    
    print(f"\nFinal results: Saved {len(unique_images)} unique NBL images to nbl_images.json")
    print(f"Total pages processed: {page - 1}")
    return unique_images

if __name__ == "__main__":
    get_nbl_images(1000)
