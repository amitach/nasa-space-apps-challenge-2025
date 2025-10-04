import json
import re

def find_iss_training_images():
    """Find NBL images that show ISS training and preparation"""
    
    with open('nbl_images_mass.json', 'r') as f:
        nbl_images = json.load(f)
    
    iss_training_images = []
    
    # Keywords that indicate ISS training/preparation
    iss_training_keywords = [
        'iss', 'international space station', 'space station', 'astronaut', 'crew',
        'eva', 'spacewalk', 'extravehicular', 'training', 'preparation',
        'expedition', 'mission', 'space', 'orbital', 'microgravity'
    ]
    
    for img in nbl_images:
        desc_lower = img['description'].lower()
        
        # Check if it's ISS-related training
        if any(keyword in desc_lower for keyword in iss_training_keywords):
            # Calculate relevance score
            score = 0
            keywords = []
            
            if 'iss' in desc_lower or 'international space station' in desc_lower:
                score += 5
                keywords.append('iss')
            
            if 'eva' in desc_lower or 'spacewalk' in desc_lower:
                score += 4
                keywords.append('spacewalk')
            
            if 'astronaut' in desc_lower or 'crew' in desc_lower:
                score += 3
                keywords.append('crew')
            
            if 'training' in desc_lower:
                score += 2
                keywords.append('training')
            
            if 'expedition' in desc_lower:
                score += 2
                keywords.append('expedition')
            
            iss_training_images.append({
                'nasa_id': img['nasa_id'],
                'description': img['description'],
                'image_url': img['image_url'],
                'source': 'nbl',
                'score': score,
                'keywords': keywords
            })
    
    # Sort by score
    iss_training_images.sort(key=lambda x: x['score'], reverse=True)
    
    return iss_training_images[:20]  # Top 20 ISS training images

def create_final_selection():
    """Create the final selection of best images for ISS 25th Anniversary Apps"""
    
    # Load the top Cupola images
    with open('selected_iss_images.json', 'r') as f:
        cupola_images = json.load(f)
    
    # Get top ISS training images from NBL
    nbl_iss_images = find_iss_training_images()
    
    print("ISS Training Images from NBL:")
    print("=" * 50)
    for i, img in enumerate(nbl_iss_images, 1):
        print(f"{i:2d}. {img['nasa_id']:<25} Score: {img['score']:2d}")
        print(f"    Keywords: {', '.join(img['keywords'])}")
        print(f"    Description: {img['description'][:80]}...")
        print()
    
    # Combine and create final selection
    final_images = []
    
    # Add top 30 Cupola images (most relevant)
    final_images.extend(cupola_images[:30])
    
    # Add top 10 NBL ISS training images
    final_images.extend(nbl_iss_images[:10])
    
    # Save final selection
    with open('final_iss_images.json', 'w') as f:
        json.dump(final_images, f, indent=2)
    
    print(f"Final selection saved: {len(final_images)} images")
    print(f"  - Cupola images: 30")
    print(f"  - NBL ISS training images: 10")
    
    return final_images

if __name__ == "__main__":
    create_final_selection()
