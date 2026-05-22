#!/usr/bin/env python3
"""
Process Lattes JSON files into standardized faculty data.
Expects files in data/json/ directory.
Outputs unified JSON to data/processed/faculty_data.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def extract_name_from_lattes(nome_completo: str) -> str:
    """Extract clean name from Lattes format."""
    # Lattes sometimes has names in format "SOBRENOME, Nome"
    if ',' in nome_completo:
        parts = nome_completo.split(',', 1)
        if len(parts) == 2:
            sobrenome = parts[0].strip()
            nome = parts[1].strip()
            # If nome seems to be first name(s) and sobrenome is last name
            if len(nome.split()) <= 3 and len(sobrenome.split()) <= 3:
                return f"{nome} {sobrenome}"
    return nome_completo

def process_lattes_json(filepath: str) -> Dict[str, Any]:
    """Process a single Lattes JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    info = data.get('informacoes_pessoais', {})
    
    # Extract basic info
    faculty = {
        'id': info.get('id_lattes', ''),
        'name': extract_name_from_lattes(info.get('nome_completo', '')),
        'name_citations': info.get('nome_citacoes', ''),
        'sex': info.get('sexo', ''),
        'professional_address': info.get('endereco_profissional', ''),
        'last_update': info.get('atualizacao_cv', ''),
        'lattes_url': info.get('url', ''),
        'summary': info.get('texto_resumo', ''),
        'education': [],
        'professional_experience': [],
        'research_projects': [],
        'extension_projects': [],
        'development_projects': [],
        'areas_of_expertise': [],
        'languages': [],
        'awards_titles': [],
        'research_lines': [],
        'publications': {
            'journal_articles': [],
            'books': [],
            'book_chapters': [],
            'conference_works': [],
            'expanded_abstracts': [],
            'conference_abstracts': [],
            'accepted_articles': [],
            'work_presentations': [],
            'newspaper_articles': [],
            'other_productions': []
        },
        'technical_production': [],
        'patents': [],
        'artistic_production': [],
        'supervision': {
            'completed': [],
            'ongoing': []
        },
        'events': [],
        'committees': [],
        'statistics': {}
    }
    
    # Process education
    for edu in data.get('formacao_academica', []):
        faculty['education'].append({
            'type': clean_text(edu.get('tipo', '')),
            'institution': clean_text(edu.get('nome_instituicao', '')),
            'start_year': clean_text(edu.get('ano_inicio', '')),
            'end_year': clean_text(edu.get('ano_conclusao', '')),
            'description': clean_text(edu.get('descricao', ''))
        })
    
    # Process professional experience
    for exp in data.get('atuacao_profissional', []):
        faculty['professional_experience'].append({
            'type': clean_text(exp.get('tipo', '')),
            'institution': clean_text(exp.get('nome_instituicao', '')),
            'start_year': clean_text(exp.get('ano_inicio', '')),
            'end_year': clean_text(exp.get('ano_conclusao', '')),
            'description': clean_text(exp.get('descricao', ''))
        })
    
    # Process research projects
    for proj in data.get('projetos_pesquisa', []):
        faculty['research_projects'].append({
            'name': clean_text(proj.get('nome_projeto', '')),
            'description': clean_text(proj.get('descricao', '')),
            'start_year': clean_text(proj.get('ano_inicio', '')),
            'end_year': clean_text(proj.get('ano_conclusao', '')),
            'sponsor': clean_text(proj.get('fonte_fomento', '')),
            'role': clean_text(proj.get('natureza', '')),
            'status': clean_text(proj.get('situacao', ''))
        })
    
    # Process extension projects
    for proj in data.get('projetos_extensao', []):
        faculty['extension_projects'].append({
            'name': clean_text(proj.get('nome_projeto', '')),
            'description': clean_text(proj.get('descricao', '')),
            'start_year': clean_text(proj.get('ano_inicio', '')),
            'end_year': clean_text(proj.get('ano_conclusao', '')),
            'sponsor': clean_text(proj.get('fonte_fomento', '')),
            'role': clean_text(proj.get('natureza', '')),
            'status': clean_text(proj.get('situacao', ''))
        })
    
    # Process development projects
    for proj in data.get('projetos_desenvolvimento', []):
        faculty['development_projects'].append({
            'name': clean_text(proj.get('nome_projeto', '')),
            'description': clean_text(proj.get('descricao', '')),
            'start_year': clean_text(proj.get('ano_inicio', '')),
            'end_year': clean_text(proj.get('ano_conclusao', '')),
            'sponsor': clean_text(proj.get('fonte_fomento', '')),
            'role': clean_text(proj.get('natureza', '')),
            'status': clean_text(proj.get('situacao', ''))
        })
    
    # Process areas of expertise
    for area in data.get('areas_de_atuacao', []):
        faculty['areas_of_expertise'].append({
            'area': clean_text(area.get('nome_area', '')),
            'level': clean_text(area.get('nivel', ''))
        })
    
    # Process languages
    for lang in data.get('idiomas', []):
        faculty['languages'].append({
            'language': clean_text(lang.get('idioma', '')),
            'proficiency': clean_text(lang.get('proficiencia_completa', ''))
        })
    
    # Process awards and titles
    for award in data.get('premios_titulos', []):
        faculty['awards_titles'].append({
            'name': clean_text(award.get('nome_premio_titulo', '')),
            'year': clean_text(award.get('ano', '')),
            'description': clean_text(award.get('descricao', ''))
        })
    
    # Process research lines
    for line in data.get('linhas_de_pesquisa', []):
        faculty['research_lines'].append(clean_text(line.get('linha_pesquisa', '')))
    
    # Process publications - journal articles
    for article in data.get('producao_bibliografica', {}).get('artigos_periodicos', []):
        faculty['publications']['journal_articles'].append({
            'title': clean_text(article.get('titulo', '')),
            'year': clean_text(article.get('ano', '')),
            'authors': clean_text(article.get('autores', '')),
            'journal': clean_text(article.get('revista', '')),
            'volume': clean_text(article.get('volume', '')),
            'number': clean_text(article.get('numero', '')),
            'pages': clean_text(article.get('paginas', '')),
            'issn': clean_text(article.get('issn', '')),
            'doi': clean_text(article.get('doi', '')),
            'qualis': clean_text(article.get('qualis', '')),
            'language': clean_text(article.get('idioma', ''))
        })
    
    # Process publications - books
    for book in data.get('producao_bibliografica', {}).get('livros_publicados', []):
        faculty['publications']['books'].append({
            'title': clean_text(book.get('titulo', '')),
            'year': clean_text(book.get('ano', '')),
            'authors': clean_text(book.get('autores', '')),
            'publisher': clean_text(book.get('editora', '')),
            'place': clean_text(book.get('local_publicacao', '')),
            'isbn': clean_text(book.get('isbn', '')),
            'language': clean_text(book.get('idioma', '')),
            'edition': clean_text(book.get('edicao', ''))
        })
    
    # Process publications - book chapters
    for chapter in data.get('producao_bibliografica', {}).get('capitulos_livros', []):
        faculty['publications']['book_chapters'].append({
            'title': clean_text(chapter.get('titulo', '')),
            'year': clean_text(chapter.get('ano', '')),
            'authors': clean_text(chapter.get('autores', '')),
            'book_title': clean_text(chapter.get('titulo_livro', '')),
            'book_authors': clean_text(chapter.get('autores_livro', '')),
            'publisher': clean_text(chapter.get('editora', '')),
            'place': clean_text(chapter.get('local_publicacao', '')),
            'isbn': clean_text(chapter.get('isbn', '')),
            'pages': clean_text(chapter.get('paginas', '')),
            'language': clean_text(chapter.get('idioma', ''))
        })
    
    # Process supervision - completed orientacoes
    for orient in data.get('orientacoes', {}).get('orientacoes_concluidas', []):
        faculty['supervision']['completed'].append({
            'type': clean_text(orient.get('tipo_orientacao', '')),
            'title': clean_text(orient.get('titulo', '')),
            'student': clean_text(orient.get('nome_aluno', '')),
            'year': clean_text(orient.get('ano_conclusao', '')),
            'institution': clean_text(orient.get('nome_instituicao', '')),
            'level': clean_text(orient.get('nivel', ''))
        })
    
    # Process supervision - ongoing orientacoes
    for orient in data.get('orientacoes', {}).get('orientacoes_em_andamento', []):
        faculty['supervision']['ongoing'].append({
            'type': clean_text(orient.get('tipo_orientacao', '')),
            'title': clean_text(orient.get('titulo', '')),
            'student': clean_text(orient.get('nome_aluno', '')),
            'start_year': clean_text(orient.get('ano_inicio', '')),
            'institution': clean_text(orient.get('nome_instituicao', '')),
            'level': clean_text(orient.get('nivel', ''))
        })
    
    # Process statistics
    stats = data.get('estatisticas', {})
    faculty['statistics'] = {
        'total_publications': stats.get('total_producoes', 0),
        'journal_articles': stats.get('artigos_periodicos', 0),
        'books': stats.get('livros_publicados', 0),
        'book_chapters': stats.get('capitulos_livros', 0),
        'completed_supervisions': stats.get('orientacoes_concluidas_mestrado', 0) + 
                               stats.get('orientacoes_concluidas_doutorado', 0) +
                               stats.get('orientacoes_concluidas_graduacao', 0),
        'ongoing_supervisions': stats.get('orientacoes_em_andamento_mestrado', 0) +
                               stats.get('orientacoes_em_andamento_doutorado', 0) +
                               stats.get('orientacoes_em_andamento_graduacao', 0)
    }
    
    return faculty

def process_all_faculty(input_dir: str = 'data/json') -> List[Dict]:
    """Process all faculty files in input directory."""
    faculty_list = []
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Input directory {input_dir} does not exist")
        return faculty_list
    
    # Process JSON files
    json_files = sorted(input_path.glob('*.json'))
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        try:
            faculty = process_lattes_json(str(json_file))
            if faculty.get('name'):
                faculty_list.append(faculty)
                print(f"✓ Processed: {faculty['name']} ({faculty['id']})")
            else:
                print(f"✗ Skipped {json_file.name}: No name found")
        except Exception as e:
            print(f"✗ Error processing {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    return faculty_list

def main():
    """Main processing function."""
    print("=" * 50)
    print("Processing Lattes data for PPGCS Faculty")
    print("=" * 50)
    
    faculty_data = process_all_faculty()
    
    # Save processed data
    output_path = Path('data/processed/faculty_data.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(faculty_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 50)
    print(f"Processed {len(faculty_data)} faculty members")
    print(f"Data saved to: {output_path}")
    print("=" * 50)
    
    # Show summary statistics
    if faculty_data:
        total_pubs = sum(f.get('statistics', {}).get('total_publications', 0) for f in faculty_data)
        total_superv = sum(f.get('statistics', {}).get('completed_supervisions', 0) for f in faculty_data)
        print(f"Total publications across faculty: {total_pubs}")
        print(f"Total completed supervisions: {total_superv}")

if __name__ == '__main__':
    main()