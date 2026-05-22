"""
Final working Google Scholar scraper.
Based on the debug output, we can see:
- Year spans: class="gsc_g_t" 
- Value spans: class="gsc_g_al"
- Stats table: table with id="gsc_rsb_st" (this is what we need to parse)
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
from urllib.parse import quote_plus, urljoin
import random

class GoogleScholarScholar:
    def __init__(self, cache_dir=None, delay_range=(2, 4)):
        """
        Initialize the scraper.
        
        Args:
            cache_dir: Directory to cache responses (if None, no caching)
            delay_range: Tuple of (min_delay, max_delay) in seconds between requests
        """
        self.session = requests.Session()
        # Set a realistic user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.delay_range = delay_range
        self.cache_dir = cache_dir
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_delay(self):
        """Return a random delay within the configured range."""
        return random.uniform(*self.delay_range)
    
    def _get_cache_path(self, url):
        """Generate a cache file path for a URL."""
        if not self.cache_dir:
            return None
        # Create a safe filename from the URL
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.html")
    
    def _get_from_cache(self, url):
        """Retrieve cached response if exists and not expired."""
        cache_path = self._get_cache_path(url)
        if cache_path and os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        return None
    
    def _save_to_cache(self, url, content):
        """Save response to cache."""
        cache_path = self._get_cache_path(url)
        if cache_path:
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception:
                pass
    
    def _make_request(self, url, use_cache=True):
        """
        Make a GET request with rate limiting and caching.
        
        Returns:
            tuple: (success: bool, content: str or None)
        """
        if use_cache:
            cached = self._get_from_cache(url)
            if cached is not None:
                return True, cached
        
        # Apply delay before request
        time.sleep(self._get_delay())
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            if use_cache:
                self._save_to_cache(url, content)
            
            return True, content
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return False, None
    
    def search_profile(self, name, affiliation=""):
        """
        Search for a professor's Google Scholar profile.
        
        Args:
            name: Full name of the professor
            affiliation: Affiliation to include in search (e.g., "UFBA")
            
        Returns:
            dict: Profile information or None if not found
        """
        # Construct search query
        query_parts = [f'"{name}"']
        if affiliation:
            query_parts.append(affiliation)
        query = " ".join(query_parts)
        
        # Google Scholar search URL
        search_url = f"https://scholar.google.com/scholar?q={quote_plus(query)}&hl=en&as_sdt=0,5"
        
        success, html = self._make_request(search_url)
        if not success:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for the first result that looks like a profile
        # Profile links typically have /citations?user=...
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/citations?user=' in href and 'hl=en' in href:
                # Check if it's a profile link (not a search result link)
                if 'citations?view_op=' not in href and 'citations?search_site' not in href:
                    profile_url = urljoin('https://scholar.google.com', href)
                    # Fetch the profile page
                    success, profile_html = self._make_request(profile_url)
                    if success:
                        return self.parse_profile(profile_html, profile_url)
                    else:
                        return None
        
        print(f"No profile found for {name}")
        return None
    
    def parse_profile(self, html, profile_url):
        """
        Parse a Google Scholar profile page to extract metrics.
        
        Args:
            html: HTML content of the profile page
            profile_url: URL of the profile
            
        Returns:
            dict: Profile data
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract name
        name_elem = soup.find('div', id='gsc_prf_in')
        name = name_elem.get_text().strip() if name_elem else ""
        
        # Extract affiliation
        affiliation_elem = soup.find('div', class_='gsc_prf_il')
        affiliation = affiliation_elem.get_text().strip() if affiliation_elem else ""
        
        # Initialize metrics
        metrics = {
            'total_citations': 0,
            'h_index': 0,
            'i10_index': 0,
            'citations_per_year': [],
            'recent_publications': []
        }
        
        # Extract metrics from the gsc_rsb_st table
        stats_table = soup.find('table', id='gsc_rsb_st')
        if stats_table:
            rows = stats_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                # Process in pairs: label (gsc_rsb_sc1) and value (gsc_rsb_std)
                i = 0
                while i < len(cols):
                    # Look for label in current column
                    label_col = cols[i]
                    if label_col and 'gsc_rsb_sc1' in label_col.get('class', []):
                        label = label_col.get_text().strip()
                        # Look for the corresponding value in the next column
                        if i + 1 < len(cols):
                            value_col = cols[i + 1]
                            if value_col and 'gsc_rsb_std' in value_col.get('class', []):
                                value = value_col.get_text().strip()
                                # Store the value based on label
                                if label == 'Citations':
                                    try:
                                        metrics['total_citations'] = int(value)
                                    except ValueError:
                                        pass
                                elif label == 'h-index':
                                    try:
                                        metrics['h_index'] = int(value)
                                    except ValueError:
                                        pass
                                elif label == 'i10-index':
                                    try:
                                        metrics['i10_index'] = int(value)
                                    except ValueError:
                                        pass
                                # Skip the value column in next iteration
                                i += 2
                                continue
                    i += 1
        
        # Extract citations per year from the spans
        # Years: class="gsc_g_t"
        # Values: class="gsc_g_al"
        year_spans = soup.find_all('span', class_='gsc_g_t')
        value_spans = soup.find_all('span', class_='gsc_g_al')
        
        for year_span, value_span in zip(year_spans, value_spans):
            year = year_span.get_text().strip()
            value = value_span.get_text().strip()
            if year.isdigit() and value.isdigit():
                metrics['citations_per_year'].append(int(value))
        
        # Extract recent publications (optional)
        pub_table = soup.find('div', id='gsc_ors_t')
        if pub_table:
            pub_rows = pub_table.find_all('tr', class_='gsc_a_tr')
            for row in pub_rows[:5]:  # Top 5 most recent
                title_elem = row.find('a', class_='gsc_a_at')
                title = title_elem.get_text().strip() if title_elem else ""
                
                # Get authors and publication info
                info_divs = row.find_all('div', class_='gs_gray')
                authors = info_divs[0].get_text().strip() if len(info_divs) > 0 else ""
                publication_info = info_divs[1].get_text().strip() if len(info_divs) > 1 else ""
                
                # Get citation count for this publication
                cited_elem = row.find('a', class_='gsc_a_ac')
                citations_text = cited_elem.get_text().strip() if cited_elem else "0"
                try:
                    citations = int(citations_text)
                except:
                    citations = 0
                
                # Get year
                year_elem = row.find('span', class_='gsc_a_h')
                year_text = year_elem.get_text().strip() if year_elem else ""
                try:
                    year = int(year_text) if year_text.isdigit() else 0
                except:
                    year = 0
                
                if title:  # Only add if we got a title
                    metrics['recent_publications'].append({
                        'title': title,
                        'authors': authors,
                        'publication_info': publication_info,
                        'year': year,
                        'citations': citations
                    })
        
        # Prepare result
        result = {
            'profile_url': profile_url,
            'name': name,
            'affiliation': affiliation,
            'h_index': metrics['h_index'],
            'i10_index': metrics['i10_index'],
            'total_citations': metrics['total_citations'],
            'citations_per_year': metrics['citations_per_year'],
            'recent_publications': metrics['recent_publications'],
            'last_updated': time.strftime('%Y-%m-%d')
        }
        
        return result

def test_scraper():
    """Test the scraper with a known professor."""
    scraper = GoogleScholarScholar(cache_dir='./scholar_cache')
    
    # Test with a professor from our list
    test_name = "Ana Rodrigues Cavalcanti Alves"
    test_affiliation = "UFBA"
    
    print(f"Searching for: {test_name}")
    result = scraper.search_profile(test_name, test_affiliation)
    
    if result:
        print("Success! Profile data:")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to retrieve profile.")
    
    return result

if __name__ == "__main__":
    test_scraper()