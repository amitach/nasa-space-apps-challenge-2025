import requests
import json
import time
import sys

def test_image_url(url, timeout=5):
    """Test if an image URL returns 200 and is accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except Exception as e:
        return False

def get_working_url(nasa_id):
    """Get the working URL for a NASA ID by testing both cases"""
    base_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~orig"
    
    # Test lowercase .jpg first (seems to be more common)
    jpg_url = base_url + ".jpg"
    if test_image_url(jpg_url):
        return jpg_url
    
    # If .jpg doesn't work, try .JPG
    JPG_url = base_url + ".JPG"
    if test_image_url(JPG_url):
        return JPG_url
    
    return None

def mass_fetch_nbl_images(max_results=5000, results_per_page=100):
    """Fetch as many NBL images as possible with proper URL validation"""
    images = {}
    page = 1
    total_fetched = 0
    consecutive_errors = 0
    max_consecutive_errors = 5
    retry_delay = 5
    consecutive_empty_pages = 0
    max_empty_pages = 3

    print(f"Starting mass fetch of NBL images (target: {max_results})...")
    print("Testing both .jpg and .JPG cases for each image...")
    print("=" * 70)
    
    while total_fetched < max_results and consecutive_empty_pages < max_empty_pages:
        try:
            url = (
                f"https://images-api.nasa.gov/search"
                f"?q=nbl&media_type=image"
                f"&year_start=1920&year_end=2025"
                f"&page_size={results_per_page}&page={page}"
            )
            
            print(f"Fetching page {page}...")
            resp = requests.get(url, timeout=30)
            
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
                consecutive_empty_pages += 1
                print(f"No items found on page {page} (empty pages: {consecutive_empty_pages})")
                if consecutive_empty_pages >= max_empty_pages:
                    print("Reached end of results.")
                    break
                page += 1
                continue
            
            # Reset empty pages counter
            consecutive_empty_pages = 0
            
            page_images_added = 0
            for item in items:
                nasa_id = item['data'][0]['nasa_id']
                description = item['data'][0].get('description', '')
                
                # Skip if we already have this image
                if nasa_id in images:
                    continue
                
                print(f"  Testing {nasa_id[:40]:<40} ", end="")
                
                # Get working URL
                working_url = get_working_url(nasa_id)
                
                if working_url:
                    images[nasa_id] = {
                        "nasa_id": nasa_id,
                        "description": description,
                        "image_url": working_url
                    }
                    total_fetched += 1
                    page_images_added += 1
                    print("✓ WORKING")
                else:
                    print("✗ FAILED")
                
                if total_fetched >= max_results:
                    break
            
            print(f"Page {page}: Added {page_images_added} new images (Total: {total_fetched})")
            
            # Reset error counter on successful request
            consecutive_errors = 0
            
            # Save progress every 5 pages
            if page % 5 == 0:
                unique_images = list(images.values())
                with open('nbl_images_mass.json', 'w') as f:
                    json.dump(unique_images, f, indent=2)
                print(f"Progress saved: {len(unique_images)} images so far")
            
            page += 1
            
            # Small delay to be respectful to the API
            time.sleep(0.3)
            
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
    with open('nbl_images_mass.json', 'w') as f:
        json.dump(unique_images, f, indent=2)
    
    print("=" * 70)
    print(f"Final results: Saved {len(unique_images)} unique NBL images to nbl_images_mass.json")
    print(f"Total pages processed: {page - 1}")
    print(f"Success rate: {len(unique_images)}/{page * results_per_page} images found and validated")
    
    return unique_images

if __name__ == "__main__":
    # Start with a reasonable target, can be increased
    get_nbl_images = mass_fetch_nbl_images(2000)  # Target 2000 images
