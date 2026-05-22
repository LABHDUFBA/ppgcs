"""
Debug script to see the exact structure of the bars in the ecg div
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_ecg():
    # Use the URL we found from the previous test
    profile_url = "https://scholar.google.com/citations?user=AkhzcawAAAAJ&hl=en&oi=ao"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    
    response = session.get(profile_url)
    print(f"Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for the ecg div
    ecg_div = soup.find('div', id='gsc_ecg')
    if ecg_div:
        print("=== gsc_ecg found ===")
        print(f"Element: {ecg_div}")
        
        # Look for all spans inside
        spans = ecg_div.find_all('span')
        print(f"\nFound {len(spans)} spans:")
        for i, span in enumerate(spans):
            classes = ' '.join(span.get('class', []))
            text = span.get_text().strip()
            if text:
                print(f"  Span {i}: class='{classes}' text='{text}'")
        
        # Look for divs inside (some versions use divs for bars)
        divs = ecg_div.find_all('div')
        print(f"\nFound {len(divs)} divs:")
        for i, div in enumerate(divs):
            classes = ' '.join(div.get('class', []))
            text = div.get_text().strip()
            if text:
                print(f"  Div {i}: class='{classes}' text='{text}'")
        
        # Check the style attributes which might contain the height
        print("\nChecking for style attributes:")
        for i, span in enumerate(spans):
            style = span.get('style', '')
            if style:
                print(f"  Span {i} style: {style}")
        for i, div in enumerate(divs):
            style = div.get('style', '')
            if style:
                print(f"  Div {i} style: {style}")
    else:
        print("gsc_ecg div NOT found")
        
        # Look for any element with ecg in id
        print("\nLooking for any element with 'ecg' in id:")
        for elem in soup.find_all(id=re.compile('ecg')):
            print(f"  Found: id='{elem.get('id')}' tag={elem.name}")
        
        # Look for canvas or svg that might contain the chart
        print("\nLooking for canvas/svg:")
        for elem in soup.find_all(['canvas', 'svg']):
            print(f"  Found: {elem.name} with id='{elem.get('id')}' class='{' '.join(elem.get('class', []))}'")

if __name__ == "__main__":
    debug_ecg()