#!/usr/bin/env python3
"""
Enhance faculty data with Google Scholar metrics (fixed version).
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add the current directory to path to import our scraper
sys.path.append(str(Path(__file__).parent))

from google_scholar_scraper import GoogleScholarScholar

def load_faculty_data(filepath: str) -> List[Dict[str, Any]]:
    """Load the existing faculty data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_faculty_data(data: List[Dict[str, Any]], filepath: str):
    """Save the faculty data."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def enhance_faculty_with_scholar(faculty_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance each faculty member with Google Scholar data.
    
    Args:
        faculty_data: List of faculty dictionaries from Lattes data
        
    Returns:
        Enhanced faculty data with Google Scholar metrics
    """
    scraper = GoogleScholarScholar(cache_dir='./scholar_cache')
    enhanced_data = []
    
    print(f"Processing {len(faculty_data)} faculty members...")
    
    for i, faculty in enumerate(faculty_data, 1):
        name = faculty.get('name', '')
        if not name:
            print(f"Skipping entry {i}: No name found")
            enhanced_data.append(faculty)
            continue
            
        print(f"[{i}/{len(faculty_data)}] Processing: {name}")
        
        # Try to get Google Scholar data
        try:
            scholar_data = scraper.search_profile(name, "UFBA")
            
            if scholar_data:
                # Add Google Scholar data to the faculty record
                faculty['google_scholar'] = {
                    'profile_url': scholar_data.get('profile_url', ''),
                    'name_gs': scholar_data.get('name', ''),
                    'affiliation_gs': scholar_data.get('affiliation', ''),
                    'h_index': scholar_data.get('h_index', 0),
                    'i10_index': scholar_data.get('i10_index', 0),
                    'total_citations': scholar_data.get('total_citations', 0),
                    'citations_per_year': scholar_data.get('citations_per_year', []),
                    'last_updated': scholar_data.get('last_updated', '')
                }
                print(f"  ✓ Found: {scholar_data.get('total_citations')} citations, h-index {scholar_data.get('h_index')}")
            else:
                # Add empty Google Scholar data structure
                faculty['google_scholar'] = {
                    'profile_url': '',
                    'name_gs': '',
                    'affiliation_gs': '',
                    'h_index': 0,
                    'i10_index': 0,
                    'total_citations': 0,
                    'citations_per_year': [],
                    'last_updated': ''
                }
                print(f"  ✗ No profile found")
                
        except Exception as e:
            print(f"  ✗ Error processing {name}: {e}")
            # Add empty Google Scholar data structure on error
            faculty['google_scholar'] = {
                'profile_url': '',
                'name_gs': '',
                'affiliation_gs': '',
                'h_index': 0,
                'i10_index': 0,
                'total_citations': 0,
                'citations_per_year': [],
                'last_updated': ''
            }
        
        # Add the faculty (either enhanced or original) to the result
        enhanced_data.append(faculty)
        
        # Be respectful to Google Scholar - add delay between requests
        if i < len(faculty_data):
            time.sleep(1)  # 1 second delay between requests (reduced from 3)
    
    return enhanced_data

def main():
    """Main function."""
    print("=" * 60)
    print("Enhancing Faculty Data with Google Scholar Metrics")
    print("=" * 60)
    
    # Paths
    input_file = Path('data/processed/faculty_data.json')
    output_file = Path('data/processed/faculty_data_enhanced.json')
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        print("Please run process_lattes_first.py first to generate the base data.")
        return 1
    
    # Load existing data
    print(f"Loading faculty data from: {input_file}")
    faculty_data = load_faculty_data(str(input_file))
    print(f"Loaded {len(faculty_data)} faculty members")
    
    # Enhance with Google Scholar data
    enhanced_data = enhance_faculty_with_scholar(faculty_data)
    
    # Save enhanced data
    print(f"\nSaving enhanced data to: {output_file}")
    output_file.parent.mkdir(exist_ok=True)
    save_faculty_data(enhanced_data, str(output_file))
    
    # Print summary
    print("\n" + "=" * 60)
    print("ENHANCEMENT COMPLETE")
    print("=" * 60)
    print(f"Enhanced data saved to: {output_file}")
    
    # Count successful matches
    successful = sum(1 for f in enhanced_data if f.get('google_scholar', {}).get('total_citations', 0) > 0)
    print(f"Successfully matched {successful}/{len(enhanced_data)} faculty members on Google Scholar")
    
    # Show some stats
    if enhanced_data:
        total_citations = sum(f.get('google_scholar', {}).get('total_citations', 0) for f in enhanced_data)
        avg_h_index = sum(f.get('google_scholar', {}).get('h_index', 0) for f in enhanced_data) / len(enhanced_data)
        print(f"Total citations across faculty: {total_citations}")
        print(f"Average h-index: {avg_h_index:.1f}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())