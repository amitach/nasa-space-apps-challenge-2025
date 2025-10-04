import json
import re
from datetime import datetime

def analyze_iss_relevance(description, nasa_id):
    """Analyze how relevant an image is for ISS 25th Anniversary Apps challenge"""
    score = 0
    keywords = []
    
    # ISS-specific keywords (high value)
    iss_keywords = [
        'international space station', 'iss', 'space station', 'orbital outpost',
        'expedition', 'crew', 'astronaut', 'cosmonaut', 'spacewalk', 'eva',
        'cupola', 'module', 'docking', 'space shuttle', 'soyuz', 'progress',
        'canadarm', 'robotic arm', 'space robotics', 'earth observation',
        'microgravity', 'zero gravity', 'space science', 'space research'
    ]
    
    # Anniversary/Historical keywords
    anniversary_keywords = [
        '25th', '25 years', 'anniversary', 'milestone', 'celebration',
        'first', 'inaugural', 'pioneer', 'historic', 'landmark',
        'achievement', 'accomplishment', 'breakthrough', 'innovation'
    ]
    
    # Earth observation keywords (popular for ISS apps)
    earth_keywords = [
        'earth', 'earth observation', 'earth view', 'earth from space',
        'planet', 'atmosphere', 'clouds', 'ocean', 'continent', 'city',
        'night lights', 'aurora', 'sunrise', 'sunset', 'horizon'
    ]
    
    # Technology/Engineering keywords
    tech_keywords = [
        'technology', 'engineering', 'innovation', 'science', 'research',
        'experiment', 'laboratory', 'facility', 'equipment', 'hardware',
        'software', 'data', 'monitoring', 'control', 'operation'
    ]
    
    # Convert description to lowercase for analysis
    desc_lower = description.lower()
    
    # Check for ISS-specific terms
    for keyword in iss_keywords:
        if keyword in desc_lower:
            score += 3
            keywords.append(keyword)
    
    # Check for anniversary/historical terms
    for keyword in anniversary_keywords:
        if keyword in desc_lower:
            score += 4
            keywords.append(keyword)
    
    # Check for Earth observation terms
    for keyword in earth_keywords:
        if keyword in desc_lower:
            score += 2
            keywords.append(keyword)
    
    # Check for technology terms
    for keyword in tech_keywords:
        if keyword in desc_lower:
            score += 1
            keywords.append(keyword)
    
    # Bonus for Cupola images (very iconic for ISS)
    if 'cupola' in desc_lower:
        score += 5
        keywords.append('cupola')
    
    # Bonus for specific ISS modules
    iss_modules = ['zvezda', 'zarya', 'unity', 'destiny', 'harmony', 'tranquility', 'columbus', 'kibo']
    for module in iss_modules:
        if module in desc_lower:
            score += 3
            keywords.append(module)
    
    # Bonus for spacewalks (very visual and popular)
    if any(term in desc_lower for term in ['spacewalk', 'eva', 'extravehicular']):
        score += 4
        keywords.append('spacewalk')
    
    # Bonus for crew activities
    if any(term in desc_lower for term in ['crew', 'astronaut', 'cosmonaut']):
        score += 2
        keywords.append('crew')
    
    # Check for recent dates (more relevant for 25th anniversary)
    year_match = re.search(r'(19|20)\d{2}', description)
    if year_match:
        year = int(year_match.group())
        if year >= 2010:  # Recent ISS operations
            score += 2
        if year >= 2020:  # Very recent
            score += 3
    
    return score, list(set(keywords))

def select_best_images():
    """Select the best images for ISS 25th Anniversary Apps challenge"""
    
    # Load Cupola images
    with open('cupola_images.json', 'r') as f:
        cupola_images = json.load(f)
    
    # Load NBL images
    with open('nbl_images_mass.json', 'r') as f:
        nbl_images = json.load(f)
    
    print("Analyzing images for ISS 25th Anniversary Apps challenge...")
    print("=" * 70)
    
    # Analyze all images
    all_images = []
    
    # Analyze Cupola images (these are highly relevant)
    print(f"Analyzing {len(cupola_images)} Cupola images...")
    for img in cupola_images:
        score, keywords = analyze_iss_relevance(img['description'], img['nasa_id'])
        all_images.append({
            'nasa_id': img['nasa_id'],
            'description': img['description'],
            'image_url': img['image_url'],
            'source': 'cupola',
            'score': score,
            'keywords': keywords
        })
    
    # Analyze NBL images (filter for ISS-related ones)
    print(f"Analyzing {len(nbl_images)} NBL images...")
    iss_related_nbl = 0
    for img in nbl_images:
        score, keywords = analyze_iss_relevance(img['description'], img['nasa_id'])
        # Only include NBL images that are ISS-related
        if score > 0 or any(term in img['description'].lower() for term in ['iss', 'space station', 'astronaut', 'crew']):
            all_images.append({
                'nasa_id': img['nasa_id'],
                'description': img['description'],
                'image_url': img['image_url'],
                'source': 'nbl',
                'score': score,
                'keywords': keywords
            })
            iss_related_nbl += 1
    
    print(f"Found {iss_related_nbl} ISS-related NBL images")
    
    # Sort by score (highest first)
    all_images.sort(key=lambda x: x['score'], reverse=True)
    
    # Select top images
    top_images = all_images[:50]  # Top 50 images
    
    print(f"\nTop {len(top_images)} images for ISS 25th Anniversary Apps:")
    print("=" * 70)
    
    for i, img in enumerate(top_images, 1):
        print(f"{i:2d}. {img['nasa_id']:<25} Score: {img['score']:2d} Source: {img['source']}")
        print(f"    Keywords: {', '.join(img['keywords'][:5])}")
        print(f"    Description: {img['description'][:100]}...")
        print()
    
    # Save selected images
    selected_data = []
    for img in top_images:
        selected_data.append({
            'nasa_id': img['nasa_id'],
            'description': img['description'],
            'image_url': img['image_url'],
            'source': img['source'],
            'relevance_score': img['score'],
            'keywords': img['keywords']
        })
    
    with open('selected_iss_images.json', 'w') as f:
        json.dump(selected_data, f, indent=2)
    
    print(f"Selected images saved to 'selected_iss_images.json'")
    
    # Statistics
    cupola_count = sum(1 for img in top_images if img['source'] == 'cupola')
    nbl_count = sum(1 for img in top_images if img['source'] == 'nbl')
    
    print(f"\nSelection Summary:")
    print(f"  Cupola images: {cupola_count}")
    print(f"  NBL images: {nbl_count}")
    print(f"  Total selected: {len(top_images)}")
    
    return selected_data

if __name__ == "__main__":
    select_best_images()
