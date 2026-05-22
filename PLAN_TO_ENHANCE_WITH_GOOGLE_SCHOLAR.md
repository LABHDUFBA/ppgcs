# Plan to Enhance Faculty Site with Google Scholar Data

## Current State
- We have 23 faculty members from PPGCS Sociology (UFBA)
- Data extracted from Lattes CVs via `process_lattes_final.py`
- Site generated via `generate_site.py` and deployed to GitHub Pages
- Current data includes: personal info, education, professional experience, publications (articles, books, chapters), supervision, projects

## Enhancement Goal
Add Google Scholar data to enrich each faculty profile with:
- h-index
- i10-index
- Total citations
- Citations per year (last 5 years)
- Recent publications (from GS)
- Research metrics visualization

## Implementation Plan

### Phase 1: Data Collection Enhancement
1. **Create Google Scholar scraper** (`scholar_scraper.py`)
   - Search by name + affiliation ("UFBA" + "Sociology")
   - Handle name variations
   - Extract profile data
   - Rate limiting and error handling
   - Cache results to avoid repeated requests

2. **Modify data processing pipeline**
   - Update `process_lattes_final.py` to:
     - Accept Lattes data as input
     - Query Google Scholar for each faculty
     - Merge GS data with Lattes data
     - Handle cases where GS profile not found
     - Output enriched JSON

### Phase 2: Data Structure Enhancement
Updated faculty data structure:
```json
{
  "id": "6506286038414113",
  "name": "Ana Rodrigues Cavalcanti Alves",
  // ... existing Lattes fields ...
  "google_scholar": {
    "profile_url": "https://scholar.google.com/citations?user=XXXX",
    "h_index": 15,
    "i10_index": 8,
    "total_citations": 450,
    "citations_last_5_years": 200,
    "citations_per_year": [45, 52, 38, 41, 24], // last 5 years
    "recent_publications": [
      {
        "title": "Article Title",
        "authors": ["Author1", "Author2"],
        "journal": "Journal Name",
        "year": 2023,
        "citations": 12
      }
    ],
    "last_updated": "2026-05-22"
  }
}
```

### Phase 3: Site Generation Updates
1. **Update `generate_site.py`** to:
   - Use enriched data
   - Add GS metrics to faculty cards
   - Create GS metrics section in individual profiles
   - Add visualization (simple bar chart for citations per year)
   - Add "View Google Scholar Profile" link

### Phase 4: Visualization & UI Enhancements
1. **Add simple CSS/JS for metrics visualization**
   - Citation trend sparkline
   - H-index badge
   - Citation count display

### Phase 5: Deployment
1. Test locally
2. Commit changes
3. Push to GitHub
4. Verify GitHub Pages update

## Technical Considerations

### Google Scholar Scraping Challenges
- No official API (must scrape)
- Rate limiting (be respectful)
- CSS selectors may change
- Need to handle CAPTCHA (rare but possible)
- Use user-agent rotation
- Implement exponential backoff

### Alternative Approaches
1. **Use SerpAPI** (if available) - more reliable but costs
2. **Use Google Scholar API via scholarly package** - Python library
3. **Hybrid approach** - try scholarly, fallback to scraping

### Data Freshness
- GS data changes frequently (citations update daily)
- Consider caching strategy:
  - Daily updates for active profiles
  - Weekly for stable profiles
  - Manual refresh option

## Implementation Details

### File Structure Changes
```
/home/hermes/ppgcs/
├── scholar_scraper.py              # New: Google Scholar scraper
├── process_lattes_enhanced.py      # Updated: combines Lattes + GS
├── generate_site.py                # Updated: uses enriched data
├── data/
│   ├── json/                       # Original Lattes JSONs
│   └── processed/
│       ├── faculty_data.json       # Lattes only (backup)
│       └── faculty_data_enriched.json # Lattes + GS
├── docs/                           # Generated site
└── assets/
    ├── css/
    │   └── style.css               # Updated: GS styles
    └── js/
        └── scholar-metrics.js      # New: visualization
```

### Dependencies to Check
- requests
- beautifulsoup4
- lxml
- scholarly (optional)
- pandas (for data manipulation, optional)

## Timeline Estimate
- Phase 1: 2-3 hours
- Phase 2: 1-2 hours
- Phase 3: 2-3 hours
- Phase 4: 1-2 hours
- Phase 5: 30 minutes
- **Total**: 6-10 hours

## Next Steps
1. Check if scholarly package is available or implement scraper
2. Create scholar_scraper.py
3. Test with 1-2 faculty members
4. Scale to all 23
5. Update site generation
6. Deploy

Let me know if you want me to proceed with this plan or if you have modifications.