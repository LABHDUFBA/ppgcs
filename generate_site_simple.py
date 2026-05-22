#!/usr/bin/env python3
"""
Simple script to generate site with GS data - corrected version
"""

import json
import os
from pathlib import Path
from urllib.parse import quote
import html

def generate_site():
    """Generate the site with GS data."""
    print("=" * 50)
    print("Generating PGPHCS Faculty Site with GS Data")
    print("=" * 50)

    # Load ENHANCED processed data (with Google Scholar)
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
    (output_dir / 'assets' / 'css').mkdir(exist_ok=True, parents=True)
    (output_dir / 'assets' / 'js').mkdir(exist_ok=True, parents=True)
    (output_dir / 'assets' / 'images').mkdir(exist_ok=True, parents=True)
    (output_dir / 'faculty').mkdir(exist_ok=True)

    # Copy existing CSS if available, otherwise use basic
    css_src = Path('assets/css/style.css')
    css_dst = output_dir / 'assets' / 'css' / 'style.css'
    if css_src.exists():
        with open(css_src, 'r', encoding='utf-8') as f_in, open(css_dst, 'w', encoding='utf-8') as f_out:
            f_out.write(f_in.read())
        print(f"✓ Copied CSS: {css_dst}")
    else:
        # Basic CSS
        css_content = """
        body { font-family: Arial, sans-serif; margin: 40px; background: #f8fafc; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
        header { background: #2563eb; color: white; padding: 2rem 0; text-align: center; }
        .faculty-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem; padding: 2rem 0; }
        .faculty-card { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .gs-metrics { background: #f8f9fa; padding: 1rem; margin: 1rem 0; border-radius: 4px; }
        .stats { display: flex; justify-content: space-between; margin-top: 1rem; font-size: 0.9rem; color: #666; }
        .stat { text-align: center; }
        .stat-value { display: block; font-weight: bold; }
        .stat-label { display: block; font-size: 0.8rem; text-transform: uppercase; }
        .btn { display: inline-block; background: #2563eb; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 4px; margin-top: 1rem; }
        """
        with open(css_dst, 'w', encoding='utf-8') as f:
            f.write(css_content)
        print(f"✓ Created basic CSS: {css_dst}")

    # Generate index.html
    current_date = __import__('datetime').datetime.now().strftime('%B %Y')
    current_year = __import__('datetime').datetime.now().year
    
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
        name = faculty.get('name', 'Unknown')
        slug = quote(name.lower().replace(' ', '-'))
        
        # Determine title
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
        
        # Truncate summary
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        # Get stats
        stats = faculty.get('statistics', {})
        pubs = stats.get('journal_articles', 0) + stats.get('books', 0) + stats.get('book_chapters', 0)
        sup = stats.get('completed_supervisions', 0)
        
        # Get GS data
        gs_data = faculty.get('google_scholar', {})
        gs_citations = gs_data.get('total_citations', 0)
        gs_h_index = gs_data.get('h_index', 0)
        gs_i10_index = gs_data.get('i10_index', 0)
        
        index_html += f"""                <div class="faculty-card">
                    <div class="faculty-card-image" style="height: 180px; background: #e2e8f0; display: flex; align-items: center; justify-content: center; color: #64748b; margin-bottom: 1rem;">
                        <img src="/assets/images/placeholder.png" alt="{html.escape(name)}" style="max-width: 100%; height: auto; max-height: 180px;">
                    </div>
                    <h2>{html.escape(name)}</h2>
                    <div class="title" style="color: #2563eb; font-weight: 500; margin-bottom: 0.5rem;">{html.escape(title)}</div>
                    <p class="summary" style="color: #64748b; margin-bottom: 1.5rem; line-height: 1.5;">{html.escape(summary)}</p>
                    
                    <!-- GS Metrics -->
                    <div class="gs-metrics">
                        <h3 style="margin-top: 0; color: #2563eb;">Google Scholar Impact</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 1rem; margin: 1rem 0;">
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
"""
    
    index_html += """            </div>
        </div>
    </main>

    <footer>
        <div class="container" style="text-align: center; padding: 2rem 0; color: #64748b; border-top: 1px solid #e2e8f0; margin-top: 2rem;">
            <p>Data sourced from Lattes CVs and Google Scholar. Last updated: """ + current_date + """</p>
            <p>&copy; """ + str(current_year) + """ LABHDUFBA - UFBA</p>
        </div>
    </footer>
</body>
</html>"""

    # Write index.html
    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"✓ Generated index.html")

    # Generate faculty detail pages
    for faculty in faculty_data:
        name = faculty.get('name', 'Unknown')
        slug = quote(name.lower().replace(' ', '-'))
        gs_data = faculty.get('google_scholar', {})
        
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
            <div style="display: flex; gap: 2rem; margin: 2rem 0;">
                <!-- Sidebar -->
                <div style="flex: 0 0 250px;">
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <img src="/assets/images/placeholder.png" alt="{html.escape(name)}" style="width: 200px; height: 200px; border-radius: 50%; object-fit: cover; border: 4px solid #2563eb; margin-bottom: 1rem;">
                        <h2>{html.escape(name)}</h2>
                        <div class="title" style="color: #2563eb; font-weight: 500;">Professor of Sociology</div>
                    </div>
                    
                    <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
                        <h3 style="margin-top: 0; color: #2563eb;">Lattes CV Statistics</h3>
                        <div class="stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 1rem;">
                            <div class="stat">
                                <span class="stat-value">{faculty.get('statistics', {}).get('journal_articles', 0)}</span>
                                <span class="stat-label">Journal Articles</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{faculty.get('statistics', {}).get('books', 0)}</span>
                                <span class="stat-label">Books</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{faculty.get('statistics', {}).get('book_chapters', 0)}</span>
                                <span class="stat-label">Book Chapters</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{faculty.get('statistics', {}).get('completed_supervisions', 0)}</span>
                                <span class="stat-label">Completed Supervisions</span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="margin-top: 0; color: #2563eb;">Google Scholar Impact</h3>
                        <div class="stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 1rem;">
                            <div class="stat">
                                <span class="stat-value">{gs_data.get('total_citations', 0):,}</span>
                                <span class="stat-label">Total Citations</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{gs_data.get('h_index', 0)}</span>
                                <span class="stat-label">h-index</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{gs_data.get('i10_index', 0)}</span>
                                <span class="stat-label">i10-index</span>
                            </div>
                        </div>
                        
                        <div style="margin-top: 1.5rem;">
                            <h4 style="color: #2563eb; margin-bottom: 0.5rem;">Citations Per Year</h4>
                            <div style="height: 150px; background: #f8f9fa; border-radius: 4px; position: relative; overflow: hidden;">
"""
        
        # Add simple bar chart for citations per year
        citation_years = gs_data.get('citations_per_year', [])
        if citation_years and len(citation_years) > 0:
            max_cite = max(citation_years) if max(citation_years) > 0 else 1
            bar_width = 100 / min(len(citation_years), 10)  # Show max 10 years
            faculty_html += '<div style="display: flex; height: 100%;">'
            # Show last 10 years
            for i, count in enumerate(citation_years[-10:]):
                height = (count / max_cite) * 80  # Max 80% height
                faculty_html += f'''<div style="flex: 0 0 {bar_width}%; display: flex; align-items: flex-end; justify-content: center;">
                    <div style="width: 60%; height: {height}%; background: #2563eb; border-radius: 2px 2px 0 0;"></div>
                    <div style="font-size: 0.7rem; text-align: center; width: 100%; margin-top: 0.25rem;">{2024 - (9 - i)}</div>
                </div>'''
            faculty_html += '</div>'
        else:
            faculty_html += '<p style="text-align: center; color: #64748b; padding: 2rem 0;">No yearly data available</p>'
        
        faculty_html += """                            </div>
                        </div>
                        
                        <div style="margin-top: 1.5rem;">
                            <h4 style="color: #2563eb; margin-bottom: 0.5rem;">Recent Publications</h4>
                            <div style="background: #f8f9fa; padding: 1rem; border-radius: 4px;">
"""
        
        # Add recent publications
        recent_pubs = gs_data.get('recent_publications', [])
        if recent_pubs:
            for pub in recent_pubs[:3]:  # Show top 3
                faculty_html += f'''<div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #e2e8f0;">
                    <h5 style="margin: 0 0 0.5rem 0; font-size: 0.9rem;">{html.escape(pub.get('title', 'Untitled'))}</h5>
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.8rem; color: #64748b;"><strong>Authors:</strong> {html.escape(pub.get('authors', ''))}</p>
                    <p style="margin: 0 0 0.25rem 0; font-size: 0.8rem; color: #64748b;"><strong>Published:</strong> {html.escape(pub.get('publication_info', ''))} ({pub.get('year', 'N/A')})</p>
                    <p style="margin: 0; font-size: 0.8rem; color: #2563eb;"><strong>Citations:</strong> {pub.get('citations', 0)}</p>
                </div>'''
        else:
            faculty_html += '<p style="text-align: center; color: #64748b; padding: 1rem 0;">No recent publication data available</p>'
        
        faculty_html += """                            </div>
                        </div>
                    </div>
                    
                    <!-- Main Content -->
                    <div style="flex: 1;">
                        <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                            <h2 style="margin-top: 0; color: #1e293b;">Academic Background</h2>
                            <p>{html.escape(faculty.get('summary', 'No summary available'))}</p>
                        </div>
                        
                        <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                            <h2 style="margin-top: 0; color: #1e293b;">Education</h2>
                            <div style="display: grid; gap: 1.5rem;">
"""
        
        # Education
        for edu in faculty.get('education', []):
            faculty_html += f'''<div>
                                <h3 style="margin: 0 0 0.5rem 0; color: #2563eb;">{html.escape(edu.get('type', ''))}</h3>
                                <p style="margin: 0 0 0.25rem 0; font-weight: 500;">{html.escape(edu.get('institution', ''))}</p>
                                <p style="margin: 0 0 0.25rem 0; color: #64748b;">{html.escape(edu.get('start_year', ''))} - {html.escape(edu.get('end_year', ''))}</p>
                                {f'<p style="margin: 0 0 0.5rem 0; color: #64748b; font-size: 0.9rem;">{html.escape(edu.get("description", ""))}</p>' if edu.get('description') else ''}
                            </div>'''
        
        faculty_html += """                            </div>
                        </div>
                        
                        <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                            <h2 style="margin-top: 0; color: #1e293b;">Publications</h2>
                            <div style="display: grid; gap: 1.5rem;">
"""
        
        # Publications by type
        pub_types = [
            ('journal_articles', 'Journal Articles'),
            ('books', 'Books'),
            ('book_chapters', 'Book Chapters')
        ]
        
        for pub_type, pub_type_name in pub_types:
            pubs = faculty.get('publications', {}).get(pub_type, [])
            if pubs:
                faculty_html += f'''<div>
                                    <h3 style="margin: 0 0 0.5rem 0; color: #2563eb;">{pub_type_name} ({len(pubs)})</h3>
                                    <ul style="list-style: none; padding: 0;">
"""
                for pub in pubs[:5]:  # Show first 5
                    faculty_html += f'''<li style="padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;">
                                        <strong>{html.escape(pub.get('title', ''))}</strong><br>
                                        <span style="font-size: 0.9rem; color: #64748b;">
'''
                    if pub_type == 'journal_articles':
                        journal_info = pub.get('journal', '')
                        year_info = pub.get('year', '')
                        if journal_info and year_info:
                            faculty_html += f'{journal_info}, {year_info}'
                        elif journal_info:
                            faculty_html += journal_info
                        elif year_info:
                            faculty_html += year_info
                    elif pub_type == 'books':
                        publisher_info = pub.get('publisher', '')
                        year_info = pub.get('year', '')
                        if publisher_info and year_info:
                            faculty_html += f'{publisher_info}, {year_info}'
                        elif publisher_info:
                            faculty_html += publisher_info
                        elif year_info:
                            faculty_html += year_info
                    elif pub_type == 'book_chapters':
                        book_title_info = pub.get('book_title', '')
                        publisher_info = pub.get('publisher', '')
                        year_info = pub.get('year', '')
                        if book_title_info:
                            faculty_html += f'In: {book_title_info}<br>'
                        if publisher_info and year_info:
                            faculty_html += f'{publisher_info}, {year_info}'
                        elif publisher_info:
                            faculty_html += publisher_info
                        elif year_info:
                            faculty_html += year_info
                        pages_info = pub.get('pages', '')
                        if pages_info:
                            faculty_html += f', pp. {pages_info}'
                    
                    faculty_html += '''</span>
                                    </li>'''
                
                faculty_html += '''                                    </ul>
                                    {f'<p style="text-align: center; margin-top: 1rem;"><a href="#" style="color: #2563eb;">View all {len(pubs)} items</a></p>' if len(pubs) > 5 else ''}
                                </div>'''
            else:
                faculty_html += f'''<div>
                                    <p style="text-align: center; color: #64748b; padding: 1rem 0;">No {pub_type_name.lower()} found.</p>
                                </div>'''
        
        faculty_html += """                            </div>
                        </div>
                        
                        <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                            <h2 style="margin-top: 0; color: #1e293b;">Supervision</h2>
                            <div style="display: grid; gap: 1.5rem;">
"""
        
        # Supervision
        supervised = faculty.get('supervision', {}).get('completed', [])
        if supervised:
            faculty_html += f'''<div>
                                    <h3 style="margin: 0 0 0.5rem 0; color: #2563eb;">Completed Supervisions ({len(supervised)})</h3>
                                    <ul style="list-style: none; padding: 0;">
"""
            for sup in supervised[:5]:
                faculty_html += f'''<li style="padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;">
                                    <strong>{html.escape(sup.get('title', ''))}</strong><br>
                                    <span style="font-size: 0.9rem; color: #64748b;">
                                        Student: {html.escape(sup.get('student', ''))} ({html.escape(sup.get('level', ''))})<br>
                                        Year: {html.escape(sup.get('year', ''))}
                                    </span>
                                </li>'''
            faculty_html += '''                                    </ul>
                                    {f'<p style="text-align: center; margin-top: 1rem;"><a href="#" style="color: #2563eb;">View all {len(supervised)} supervisions</a></p>' if len(supervised) > 5 else ''}
                                </div>'''
        else:
            faculty_html += '''<div>
                                    <p style="text-align: center; color: #64748b; padding: 1rem 0;">No completed supervisions found.</p>
                                </div>'''
        
        ongoing = faculty.get('supervision', {}).get('ongoing', [])
        if ongoing:
            faculty_html += f'''<div>
                                    <h3 style="margin: 0 0 0.5rem 0; color: #2563eb;">Ongoing Supervisions ({len(ongoing)})</h3>
                                    <ul style="list-style: none; padding: 0;">
"""
            for sup in ongoing[:5]:
                faculty_html += f'''<li style="padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;">
                                    <strong>{html.escape(sup.get('title', ''))}</strong><br>
                                    <span style="font-size: 0.9rem; color: #64748b;">
                                        Student: {html.escape(sup.get('student', ''))} ({html.escape(sup.get('level', ''))})<br>
                                        Since: {html.escape(sup.get('start_year', ''))}
                                    </span>
                                </li>'''
            faculty_html += '''                                    </ul>
                                    {f'<p style="text-align: center; margin-top: 1rem;"><a href="#" style="color: #2563eb;">View all {len(ongoing)} supervisions</a></p>' if len(ongoing) > 5 else ''}
                                </div>'''
        else:
            faculty_html += '''<div>
                                    <p style="text-align: center; color: #64748b; padding: 1rem 0;">No ongoing supervisions found.</p>
                                </div>'''
        
        faculty_html += """                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer>
        <div class="container" style="text-align: center; padding: 2rem 0; color: #64748b; border-top: 1px solid #e2e8f0; margin-top: 2rem;">
            <p>&copy; """ + str(current_year) + """ LABHDUFBA - UFBA</p>
        </div>
    </footer>
</body>
</html>"""

        # Write faculty page
        faculty_dir = output_dir / 'faculty'
        faculty_dir.mkdir(exist_ok=True)
        with open(faculty_dir / f'{slug}.html', 'w', encoding='utf-8') as f:
            f.write(faculty_html)
        print(f"✓ Generated faculty page: {slug}.html")
    
    # Create README
    readme_content = """# PGPHCS Faculty Site

This site showcases the academic production of PGPHCS faculty members, combining data from Lattes CVs and Google Scholar.

## Features
- Modern, responsive design
- Faculty profiles with Lattes CV statistics
- Google Scholar impact metrics (citations, h-index, i10-index)
- Publication lists
- Supervision records
- Visual citations per year chart

## Data Sources
- Lattes Platform (CNPq)
- Google Scholar

## Generated On
""" + current_date + """

## To Regenerate
1. Run `python3 enhance_with_scholar_fixed.py` to collect Google Scholar data
2. Run `python3 generate_site_simple.py` to generate the site
3. Commit the `docs/` folder to your GitHub repository
4. Enable GitHub Pages in repository settings (source: /docs folder)
"""
    
    with open(output_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ Generated README.md")
    
    print("\n" + "=" * 50)
    print("SITE GENERATION COMPLETE")
    print("=" * 50)
    print(f"Site generated in: {output_dir.absolute()}")
    print("Next steps:")
    print("1. Verify the generated files")
    print("2. Commit the docs/ folder to your GitHub repository")
    print("3. Enable GitHub Pages (Settings → Pages → Source: /docs folder)")

if __name__ == '__main__':
    generate_site()