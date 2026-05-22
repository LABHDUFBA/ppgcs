"""
Debug script to examine the Google Scholar profile HTML structure
"""

import requests
from bs4 import BeautifulSoup
import json

def debug_profile():
    # Use the URL we found from the previous test
    profile_url = "https://scholar.google.com/citations?user=AkhzcawAAAAJ&hl=en&oi=ao"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    
    response = session.get(profile_url)
    print(f"Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for the stats table
    stats_table = soup.find('table', id='gsc_ftb')
    print(f"Stats table found: {stats_table is not None}")
    
    if stats_table:
        print("\nStats table rows:")
        rows = stats_table.find_all('tr')
        for i, row in enumerate(rows):
            cols = row.find_all('td')
            col_texts = [col.get_text().strip() for col in cols]
            print(f"  Row {i}: {col_texts}")
            
            # Also check for any spans or other elements inside
            for j, col in enumerate(cols):
                spans = col.find_all('span')
                if spans:
                    span_texts = [s.get_text().strip() for s in spans]
                    print(f"    Col {j} spans: {span_texts}")
    
    # Look for the gsc_rsb_scc div which often contains the metrics
    rsb_scc = soup.find('div', id='gsc_rsb_scc')
    print(f"\ngsc_rsb_scc found: {rsb_scc is not None}")
    if rsb_scc:
        print(f"Content: {rsb_scc.get_text()[:200]}")
        
        # Look for the metrics inside
        metrics_divs = rsb_scc.find_all('div', class_='gsc_rsb_std')
        print(f"Found {len(metrics_divs)} metric divs:")
        for i, div in enumerate(metrics_divs):
            text = div.get_text().strip()
            print(f"  Metric {i}: '{text}'")
    
    # Look for all elements with class containing 'gsc_rsb'
    print("\nAll gsc_rsb elements:")
    for elem in soup.find_all(class_=lambda x: x and 'gsc_rsb' in x):
        classes = ' '.join(elem.get('class', []))
        text = elem.get_text().strip()
        if text:
            print(f"  {classes}: {text[:100]}")

if __name__ == "__main__":
    debug_profile()