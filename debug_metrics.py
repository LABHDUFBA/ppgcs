"""
Debug script to see the actual HTML structure of the metrics section
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_metrics():
    # Use the URL we found from the previous test
    profile_url = "https://scholar.google.com/citations?user=AkhzcawAAAAJ&hl=en&oi=ao"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    
    response = session.get(profile_url)
    print(f"Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for the gsc_rsb_scc div
    scc = soup.find('div', id='gsc_rsb_scc')
    if scc:
        print("\n=== gsc_rsb_scc content ===")
        print(scc.prettify()[:2000])  # First 2000 chars
        
        # Look for all divs inside
        print("\n=== All divs in gsc_rsb_scc ===")
        for i, div in enumerate(scc.find_all('div', recursive=False)):
            classes = ' '.join(div.get('class', []))
            text = div.get_text().strip()
            print(f"Div {i}: class='{classes}' text='{text}'")
            
            # Look for children
            for j, child in enumerate(div.find_all('div', recursive=False)):
                child_classes = ' '.join(child.get('class', []))
                child_text = child.get_text().strip()
                if child_text:
                    print(f"  Child {j}: class='{child_classes}' text='{child_text}'")
    else:
        print("gsc_rsb_scc not found")
        
        # Let's see what we DO have
        print("\n=== Looking for gsc_rsb elements ===")
        for elem in soup.find_all(class_=re.compile(r'gsc_rsb')):
            classes = ' '.join(elem.get('class', []))
            text = elem.get_text().strip()
            if text and len(text) < 100:  # Only show short meaningful text
                print(f"Class: {classes} -> Text: '{text}'")
    
    # Look for the metrics table
    print("\n=== Looking for stats table ===")
    stats_table = soup.find('table', id='gsc_ftb')
    if stats_table:
        print("Stats table found:")
        print(stats_table.prettify())
    else:
        print("Stats table NOT found")
        
        # Look for any table
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables total")
        for i, table in enumerate(tables):
            if table.get('id'):
                print(f"  Table {i}: id='{table.get('id')}'")
            if table.get('class'):
                print(f"  Table {i}: class='{' '.join(table.get('class', []))}'")

if __name__ == "__main__":
    debug_metrics()