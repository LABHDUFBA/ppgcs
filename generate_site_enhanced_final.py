#!/usr/bin/env python3
"""
Generate static faculty site from ENHANCED processed Lattes data (with Google Scholar).
Outputs to docs/ directory for GitHub Pages.
"""

import json
import os
from pathlib import Path
from urllib.parse import quote
import html

def generate_site():
    """Generate the static site."""
    print("=" * 50)
    print("Generating ENHANCED PPGCS Faculty Site")
    print("=" * 50)

    # Load ENHANCED processed data (includes Google Scholar data)
    data_path = Path('data/processed/faculty_data_enhanced.json')
    if not data_path.exists():
        print(f"Error: {data_path} not found. Run enhance_with_scholar_fixed.py first.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        faculty_data = json.load(f)

    print(f"Loaded {len(faculty_data)} faculty members")

    # Create output directory
    output_dir = Path('docs')
    output_dir.mkdir(exist_ok=True)

    # Create assets directory
    assets_dir = output_dir / 'assets'
    assets_dir.mkdir(exist_ok=True)
    (assets_dir / 'css').mkdir(exist_ok=True)
    (assets_dir / 'js').mkdir(exist_ok=True)
    (assets_dir / 'images').mkdir(exist_ok=True)

    # Generate CSS - read from existing or create basic
    original_css_path = Path('assets/css/style.css')
    if original_css_path.exists():
        with open(original_css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
    else:
        # Fallback to basic CSS if original not found
        css_content = """
        /* Basic fallback CSS */
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .faculty-card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
        """
    
    # Write CSS
    css_path = assets_dir / 'css' / 'style.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print(f"✓ Generated CSS: {css_path}")

    # Generate index.html
    current_date = __import__('datetime').datetime.now().strftime('%B %Y')
    current_year = __import__('datetime').datetime.now().year
    
    # Start building index.html
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PGPHCS Faculty - LABHDUFBA</title>
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="container">
            <h1>PGPHCS Faculty</h1>
            <p>Programa de Pós-Graduação em Ciências Sociais - UFBA</p>
        </div>
    </header>

    <main>
        <div class="container">
            <div class="faculty-grid">
"""

    # Add faculty cards
    for faculty in faculty_data:
        # Create a slug for the faculty member
        name = faculty.get('name', 'Unknown')
        slug = quote(name.lower().replace(' ', '-'))
        
        # Determine title/position from summary or professional address
        title = "Professor"
        summary = faculty.get('summary', '')
        if "Adjunta" in summary:
            title = "Adjunct Professor"
        elif "Associado" in summary:
            title = "Associate Professor"
        elif "Titular" in summary:
            title = "Full Professor"
        elif "Assistente" in summary:
            title = "Assistant Professor"
        
        # Get summary (truncated)
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        # Get statistics
        stats = faculty.get('statistics', {})
        pubs = stats.get('journal_articles', 0) + stats.get('books', 0) + stats.get('book_chapters', 0)
        sup = stats.get('completed_supervisions', 0)
        
        # Get Google Scholar data
        gs_data = faculty.get('google_scholar', {})
        gs_citations = gs_data.get('total_citations', 0)
        gs_h_index = gs_data.get('h_index', 0)
        gs_i10_index = gs_data.get('i10_index', 0)
        
        # Build the faculty card HTML
        card_html = f"""                <div class="faculty-card">
                    <div class="faculty-card-image">
                        <img src="/assets/images/placeholder.png" alt="{html.escape(name)}">
                    </div>
                    <div class="faculty-card-content">
                        <h2>{html.escape(name)}</h2>
                        <div class="title">{html.escape(title)}</div>
                        <p class="summary">{html.escape(summary)}</p>
                        
                        <!-- Google Scholar Metrics -->
                        <div class="gs-metrics" style="background: #f8f9fa; padding: 1rem; border-radius: 4px; margin: 1rem 0;">
                            <h3 style="margin-top: 0; color: #2563eb;">Google Scholar Impact</h3>
                            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 1rem;">
                                <div class="stat">
                                    <span class="stat-value">{gs_citations:,}</span>
                                    <span class="stat-label">Citations</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-value">{gs_h_index}</span>
                                    <span class="stat-label">h-index</span>
                                </div>
                                <div class="stat">
                                    <span class="stat-value">{gs_i10_index}</span>
                                    <span class="stat-label">i10-index</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="stats">
                            <div class="stat">
                                <span class="stat-value">{pubs}</span>
                                <span class="stat-label">Publications</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{sup}</span>
                                <span class="stat-label">Supervisions</span>
                            </div>
                        </div>
                        
                        <a href="faculty/{slug}.html" class="btn">View Profile</a>
                    </div>
                </div>
"""
        index_html += card_html
    
    # Finish index.html
    index_html += """            </div>
        </div>
    </main>

    <footer>
        <div class="container">
            <p>Data sourced from Lattes CVs and Google Scholar. Last updated: """ + current_date + """</p>
            <p>&copy; """ + str(current_year) + """ LABHDUFBA - UFBA</p>
        </div>
    </footer>
</body>
</html>"""

    # Write index.html
    index_path = output_dir / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"✓ Generated index.html: {index_path}")

    # Generate individual faculty pages
    faculty_dir = output_dir / 'faculty'
    faculty_dir.mkdir(exist_ok=True)
    
    for faculty in faculty_data:
        name = faculty.get('name', 'Unknown')
        slug = quote(name.lower().replace(' ', '-'))
        
        # Get Google Scholar data
        gs_data = faculty.get('google_scholar', {})
        
        # Build faculty page
        faculty_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(name)} - PGPHCS Faculty</title>
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="container">
            <h1>{html.escape(name)}</h1>
            <p>Programa de Pós-Graduação em Ciências Sociais - UFBA</p>
        </div>
    </header>

    <main>
        <div class="container">
            <div class="faculty-detail">
                <div class="faculty-detail-header">
                    <h1>{html.escape(name)}</h1>
                    <div class="title">Professor of Sociology</div>
                    <div class="image">
                        <img src="/assets/images/placeholder.png" alt="{html.escape(name)}">
                    </div>
                </div>
                
                <div class="faculty-detail-content">
                    <div class="section">
                        <h2>Academic Background</h2>
                        <p>{html.escape(faculty.get('summary', 'No summary available'))}</p>
                    </div>
                    
                    <div class="section">
                        <h2>Lattes CV Statistics</h2>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <span class="stat-value">{faculty.get('statistics', {}).get('journal_articles', 0)}</span>
                                <span class="stat-label">Journal Articles</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-value">{faculty.get('statistics', {}).get('books', 0)}</span>
                                <span class="stat-label">Books</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-value">{faculty.get('statistics', {}).get('book_chapters', 0)}</span>
                                <span class="stat-label">Book Chapters</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-value">{faculty.get('statistics', {}).get('completed_supervisions', 0)}</span>
                                <span class="stat-label">Completed Supervisions</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Google Scholar Impact Metrics</h2>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <span class="stat-value">{gs_data.get('total_citations', 0):,}</span>
                                <span class="stat-label">Total Citations</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-value">{gs_data.get('h_index', 0)}</span>
                                <span class="stat-label">h-index</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-value">{gs_data.get('i10_index', 0)}</span>
                                <span class="stat-label">i10-index</span>
                            </div>
                        </div>
                        
                        <h3>Citations Per Year</h3>
                        <div class="citations-chart">
                            <div style="height: 200px; background: #f8f9fa; border-radius: 4px; padding: 1rem; position: relative;">
"""
        
        # Add gradient based on citation data
        citation_years = gs_data.get('citations_per_year', [])
        if citation_years:
            max_cite = max(citation_years) if citation_years else 1
            gradient_stops = []
            for i, count in enumerate(citation_years[-10:]):  # Last 10 years
                if i < 10:
                    position = (i / 9) * 100
                    intensity = count / max_cite if max_cite > 0 else 0
                    color_val = int(255 * intensity)
                    gradient_stops.append(f"rgb({color_val}, 100, 200) {position}%")
            if gradient_stops:
                css_grad = ", ".join(gradient_stops)
                faculty_html += css_grad
            else:
                faculty_html += "rgb(100, 100, 200) 0%, rgb(100, 100, 200) 100%"
        else:
            faculty_html += "rgb(100, 100, 200) 0%, rgb(100, 100, 200) 100%"
        
        faculty_html += """);">
                            </div>
                        </div>
                        
                        <h3>Recent Publications</h3>
                        <div class="content-grid">
"""
        
        # Add recent publications from Google Scholar if available
        recent_pubs = gs_data.get('recent_publications', [])
        if recent_pubs:
            for pub in recent_pubs[:5]:  # Show top 5
                faculty_html += f"""                            <div class="card">
                                <h4>{html.escape(pub.get('title', 'Untitled'))}</h4>
                                <p><strong>Authors:</strong> {html.escape(pub.get('authors', ''))}</p>
                                <p><strong>Published:</strong> {html.escape(pub.get('publication_info', ''))} ({pub.get('year', 'N/A')})</p>
                                <p><strong>Citations:</strong> {pub.get('citations', 0)}</p>
                            </div>
"""
        else:
            faculty_html += """                            <p>No recent publication data available from Google Scholar.</p>
"""
        
        faculty_html += """                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>External Links</h2>
                        <div class="content-grid">
"""
                        # Add Lattes link
                        lattes_url = faculty.get('lattes_url', '')
                        if lattes_url:
                            faculty_html += f"""                            <div class="card">
                                <h4>Lattes CV</h4>
                                <p><a href="{html.escape(lattes_url)}" target="_blank">View Lattes Curriculum Vitae</a></p>
                            </div>
"""
                        
                        # Add Google Scholar link
                        gs_url = gs_data.get('profile_url', '')
                        if gs_url:
                            faculty_html += f"""                            <div class="card">
                                <h4>Google Scholar Profile</h4>
                                <p><a href="{html.escape(gs_url)}" target="_blank">View Google Scholar Profile</a></p>
                            </div>
"""
                        
                        faculty_html += """                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; """ + str(current_year) + """ LABHDUFBA - UFBA</p>
        </div>
    </footer>
</body>
</html>"""

        faculty_path = faculty_dir / f'{slug}.html'
        with open(faculty_path, 'w', encoding='utf-8') as f:
            f.write(faculty_html)
        print(f"✓ Generated faculty page: {faculty_path}")

    print("\n" + "=" * 50)
    print("ENHANCED SITE GENERATION COMPLETE")
    print("=" * 50)
    print(f"Site generated in: {output_dir.absolute()}")
    print(f"Main page: {index_path}")
    print(f"Faculty profiles: {faculty_dir}")

if __name__ == '__main__':
    generate_site()