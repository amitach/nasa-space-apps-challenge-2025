import requests
import json
import time
import sys

def get_cupola_images(max_results=1000):
    images = {}
    page = 1
    results_per_page = 100
    total_fetched = 0
    consecutive_errors = 0
    max_consecutive_errors = 5
    retry_delay = 5  # seconds

    print(f"Starting to fetch cupola images (target: {max_results})...")
    
    while total_fetched < max_results:
        try:
            url = (
                f"https://images-api.nasa.gov/search"
                f"?q=cupola%20images&media_type=image"
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
                # Find original image asset
                orig_url = ''
                for link in item.get('links', []):
                    if link['rel'] == 'preview':
                        preview_url = link['href']
                    # Attempt to get the ~orig.jpg manually
                    base_url = f"https://images-assets.nasa.gov/image/{nasa_id}/{nasa_id}~orig.jpg"
                    orig_url = base_url
                
                # Use NASA ID as unique key to ensure no duplicates
                if nasa_id not in images:
                    images[nasa_id] = {
                        "nasa_id": nasa_id,
                        "description": description,
                        "image_url": orig_url
                    }
                    total_fetched += 1
                    page_images_added += 1
                    if total_fetched >= max_results:
                        break
            
            print(f"Page {page}: Added {page_images_added} new images (Total: {total_fetched})")
            
            # Reset error counter on successful request
            consecutive_errors = 0
            
            # Save progress every 10 pages
            if page % 10 == 0:
                unique_images = list(images.values())
                with open('cupola_images.json', 'w') as f:
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
    with open('cupola_images.json', 'w') as f:
        json.dump(unique_images, f, indent=2)
    
    print(f"\nFinal results: Saved {len(unique_images)} unique cupola images to cupola_images.json")
    print(f"Total pages processed: {page - 1}")
    return unique_images

get_cupola_images(1000)