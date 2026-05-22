"""
Comprehensive debug to see the full structure of the page around the citations chart
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_full_structure():
    # Use the URL we found from the previous test
    profile_url = "https://scholar.google.com/citations?user=AkhzcawAAAAJ&hl=en&oi=ao"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    
    response = session.get(profile_url)
    print(f"Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Save the entire HTML for inspection
    with open('/tmp/profile_debug.html', 'w') as f:
        f.write(response.text)
    print("Saved full HTML to /tmp/profile_debug.html")
    
    # Look for any elements that might contain the yearly data
    print("\n=== Looking for elements with 'gsc_g' in class ===")
    for elem in soup.find_all(class_=re.compile(r'gsc_g')):
        classes = ' '.join(elem.get('class', []))
        text = elem.get_text().strip()
        if text:
            print(f"  Class: {classes} -> Text: '{text}'")
    
    # Look for any elements that might contain years
    print("\n=== Looking for elements that might contain years ===")
    for elem in soup.find_all(text=re.compile(r'^\d{4}$')):
        parent = elem.parent
        classes = ' '.join(parent.get('class', []))
        print(f"  Found year '{elem.strip()}' in element with class: '{classes}'")
    
    # Look for any elements that might contain numbers (citation counts)
    print("\n=== Looking for elements that might contain citation counts ===")
    for elem in soup.find_all(text=re.compile(r'^\d+$')):
        text = elem.strip()
        # Only consider reasonable citation counts (0-1000)
        if text.isdigit() and 0 <= int(text) <= 1000:
            parent = elem.parent
            classes = ' '.join(parent.get('class', []))
            # Avoid counting the same thing multiple times by checking if we've seen this parent recently
            # But for now, just show a few examples
            if len(classes) < 50:  # Limit output
                print(f"  Found count '{text}' in element with class: '{classes}'")
    
    # Look for the gsc_pwl area (the print view link area which might be near the stats)
    print("\n=== Looking around gsc_pwl ===")
    pwl = soup.find('div', id='gsc_pwl')
    if pwl:
        print("Found gsc_pwl")
        # Look at siblings and nearby elements
        for elem in pwl.find_all_next('div', limit=10):
            classes = ' '.join(elem.get('class', []))
            text = elem.get_text().strip()
            if text and ('gsc_' in classes or len(text) < 50):
                print(f"  Next div: class='{classes}' text='{text}'")

if __name__ == "__main__":
    debug_full_structure()