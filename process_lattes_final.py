#!/usr/bin/env python3
"""
Process Lattes JSON files into standardized faculty data.
Expects files in data/json/ directory.
Outputs unified JSON to data/processed/faculty_data.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Union
import re

def safe_string(value: Any) -> str:
    """Safely convert any value to a clean string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        # If it's a list of strings, join them
        if all(isinstance(item, str) for item in value):
            return clean_text(" ".join(value))
        # If it's a list of dicts, try to extract meaningful text
        elif all(isinstance(item, dict) for item in value):
            # For now, return empty string or first item's description if it's a dict with desc
            # This is a fallback - we'll handle specific cases in the processing
            return ""
        else:
            # Mixed or other types - convert each to string and join
            return clean_text(" ".join(str(item) for item in value))
    # For dict, int, float, etc.
    return clean_text(str(value))

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def extract_name_from_lattes(nome_completo: str) -> str:
    """Extract clean name from Lattes format."""
    if not nome_completo:
        return ""
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
        'id': safe_string(info.get('id_lattes', '')),
        'name': extract_name_from_lattes(safe_string(info.get('nome_completo', ''))),
        'name_citations': safe_string(info.get('nome_citacoes', '')),
        'sex': safe_string(info.get('sexo', '')),
        'professional_address': safe_string(info.get('endereco_profissional', '')),
        'last_update': safe_string(info.get('atualizacao_cv', '')),
        'lattes_url': safe_string(info.get('url', '')),
        'summary': safe_string(info.get('texto_resumo', '')),
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
        if isinstance(edu, dict):
            faculty['education'].append({
                'type': safe_string(edu.get('tipo', '')),
                'institution': safe_string(edu.get('nome_instituicao', '')),
                'start_year': safe_string(edu.get('ano_inicio', '')),
                'end_year': safe_string(edu.get('ano_conclusao', '')),
                'description': safe_string(edu.get('descricao', ''))
            })
    
    # Process professional experience
    for exp in data.get('atuacao_profissional', []):
        if isinstance(exp, dict):
            faculty['professional_experience'].append({
                'type': safe_string(exp.get('tipo', '')),
                'institution': safe_string(exp.get('nome_instituicao', '')),
                'start_year': safe_string(exp.get('ano_inicio', '')),
                'end_year': safe_string(exp.get('ano_conclusao', '')),
                'description': safe_string(exp.get('descricao', ''))
            })
    
    # Process research projects
    for proj in data.get('projetos_pesquisa', []):
        if isinstance(proj, dict):
            # Handle descricao which might be a list
            descricao = proj.get('descricao', '')
            if isinstance(descricao, list):
                descricao = " ".join(descricao) if descricao else ""
            
            # Handle integrantes which might be a list of dicts
            integrantes = proj.get('integrantes', [])
            integrantes_processed = []
            if isinstance(integrantes, list):
                for integ in integrantes:
                    if isinstance(integ, dict):
                        nome = safe_string(integ.get('nome', ''))
                        papel = safe_string(integ.get('papel', ''))
                        if nome or papel:
                            integrantes_processed.append({
                                'name': nome,
                                'role': papel
                            })
            
            faculty['research_projects'].append({
                'name': safe_string(proj.get('nome', '')),
                'description': safe_string(descricao),
                'start_year': safe_string(proj.get('ano_inicio', '')),
                'end_year': safe_string(proj.get('ano_conclusao', '')),
                'type': safe_string(proj.get('tipo', '')),
                'integrantes': integrantes_processed
            })
    
    # Process extension projects
    for proj in data.get('projetos_extensao', []):
        if isinstance(proj, dict):
            # Handle descricao which might be a list
            descricao = proj.get('descricao', '')
            if isinstance(descricao, list):
                descricao = " ".join(descricao) if descricao else ""
            
            # Handle integrantes
            integrantes = proj.get('integrantes', [])
            integrantes_processed = []
            if isinstance(integrantes, list):
                for integ in integrantes:
                    if isinstance(integ, dict):
                        nome = safe_string(integ.get('nome', ''))
                        papel = safe_string(integ.get('papel', ''))
                        if nome or papel:
                            integrantes_processed.append({
                                'name': nome,
                                'role': papel
                            })
            
            faculty['extension_projects'].append({
                'name': safe_string(proj.get('nome', '')),
                'description': safe_string(descricao),
                'start_year': safe_string(proj.get('ano_inicio', '')),
                'end_year': safe_string(proj.get('ano_conclusao', '')),
                'type': safe_string(proj.get('tipo', '')),
                'integrantes': integrantes_processed
            })
    
    # Process development projects
    for proj in data.get('projetos_desenvolvimento', []):
        if isinstance(proj, dict):
            faculty['development_projects'].append({
                'name': safe_string(proj.get('nome', '')),
                'description': safe_string(proj.get('descricao', '')),
                'start_year': safe_string(proj.get('ano_inicio', '')),
                'end_year': safe_string(proj.get('ano_conclusao', '')),
                'type': safe_string(proj.get('tipo', ''))
            })
    
    # Process areas of expertise
    for area in data.get('areas_de_atuacao', []):
        if isinstance(area, dict):
            faculty['areas_of_expertise'].append({
                'area': safe_string(area.get('area', '')) or safe_string(area.get('nome_area', '')),
                'level': safe_string(area.get('nivel', '')),
                'grande_area': safe_string(area.get('grande_area', '')),
                'subarea': safe_string(area.get('subarea', '')),
                'especialidade': safe_string(area.get('especialidade', '')),
                'descricao_completa': safe_string(area.get('descricao_completa', ''))
            })
    
    # Process languages
    for lang in data.get('idiomas', []):
        if isinstance(lang, dict):
            faculty['languages'].append({
                'language': safe_string(lang.get('nome', '')) or safe_string(lang.get('idioma', '')),
                'compreende': safe_string(lang.get('compreende', '')),
                'fala': safe_string(lang.get('fala', '')),
                'le': safe_string(lang.get('le', '')),
                'escreve': safe_string(lang.get('escreve', '')),
                'proficiencia_completa': safe_string(lang.get('proficiencia_completa', ''))
            })
    
    # Process awards and titles
    for award in data.get('premios_titulos', []):
        if isinstance(award, dict):
            faculty['awards_titles'].append({
                'name': safe_string(award.get('nome_premio_titulo', '')),
                'year': safe_string(award.get('ano', '')),
                'description': safe_string(award.get('descricao', ''))
            })
    
    # Process research lines
    for line in data.get('linhas_de_pesquisa', []):
        if isinstance(line, dict):
            faculty['research_lines'].append(safe_string(line.get('linha_pesquisa', '')))
        elif isinstance(line, str):
            faculty['research_lines'].append(safe_string(line))
    
    # Process publications - journal articles
    for article in data.get('producao_bibliografica', {}).get('artigos_periodicos', []):
        if isinstance(article, dict):
            faculty['publications']['journal_articles'].append({
                'title': safe_string(article.get('titulo', '')),
                'year': safe_string(article.get('ano', '')),
                'authors': safe_string(article.get('autores', '')),
                'journal': safe_string(article.get('revista', '')),
                'volume': safe_string(article.get('volume', '')),
                'number': safe_string(article.get('numero', '')),
                'pages': safe_string(article.get('paginas', '')),
                'issn': safe_string(article.get('issn', '')),
                'doi': safe_string(article.get('doi', '')),
                'qualis': safe_string(article.get('qualis', '')),
                'language': safe_string(article.get('idioma', ''))
            })
    
    # Process publications - books
    for book in data.get('producao_bibliografica', {}).get('livros_publicados', []):
        if isinstance(book, dict):
            faculty['publications']['books'].append({
                'title': safe_string(book.get('titulo', '')),
                'year': safe_string(book.get('ano', '')),
                'authors': safe_string(book.get('autores', '')),
                'publisher': safe_string(book.get('editora', '')),
                'place': safe_string(book.get('local_publicacao', '')),
                'isbn': safe_string(book.get('isbn', '')),
                'language': safe_string(book.get('idioma', '')),
                'edition': safe_string(book.get('edicao', ''))
            })
    
    # Process publications - book chapters
    for chapter in data.get('producao_bibliografica', {}).get('capitulos_livros', []):
        if isinstance(chapter, dict):
            faculty['publications']['book_chapters'].append({
                'title': safe_string(chapter.get('titulo', '')),
                'year': safe_string(chapter.get('ano', '')),
                'authors': safe_string(chapter.get('autores', '')),
                'book_title': safe_string(chapter.get('titulo_livro', '')),
                'book_authors': safe_string(chapter.get('autores_livro', '')),
                'publisher': safe_string(chapter.get('editora', '')),
                'place': safe_string(chapter.get('local_publicacao', '')),
                'isbn': safe_string(chapter.get('isbn', '')),
                'pages': safe_string(chapter.get('paginas', '')),
                'language': safe_string(chapter.get('idioma', ''))
            })
    
    # Process supervision - completed orientacoes
    for orient in data.get('orientacoes', {}).get('orientacoes_concluidas', []):
        if isinstance(orient, dict):
            faculty['supervision']['completed'].append({
                'type': safe_string(orient.get('tipo_orientacao', '')),
                'title': safe_string(orient.get('titulo', '')),
                'student': safe_string(orient.get('nome_aluno', '')),
                'year': safe_string(orient.get('ano_conclusao', '')),
                'institution': safe_string(orient.get('nome_instituicao', '')),
                'level': safe_string(orient.get('nivel', ''))
            })
    
    # Process supervision - ongoing orientacoes
    for orient in data.get('orientacoes', {}).get('orientacoes_em_andamento', []):
        if isinstance(orient, dict):
            faculty['supervision']['ongoing'].append({
                'type': safe_string(orient.get('tipo_orientacao', '')),
                'title': safe_string(orient.get('titulo', '')),
                'student': safe_string(orient.get('nome_aluno', '')),
                'start_year': safe_string(orient.get('ano_inicio', '')),
                'institution': safe_string(orient.get('nome_instituicao', '')),
                'level': safe_string(orient.get('nivel', ''))
            })
    
    # Process statistics - map from estatisticas
    stats = data.get('estatisticas', {})
    faculty['statistics'] = {
        'total_publications': stats.get('total_producoes', 
                                   stats.get('total_artigos_periodicos', 0) + 
                                   stats.get('total_livros', 0) + 
                                   stats.get('total_capitulos', 0) + 
                                   stats.get('total_trabalhos_congressos', 0)),
        'journal_articles': stats.get('total_artigos_periodicos', 0),
        'books': stats.get('total_livros', 0),
        'book_chapters': stats.get('total_capitulos', 0),
        'conference_works': stats.get('total_trabalhos_congressos', 0),
        'completed_supervisions': stats.get('total_orientacoes_concluidas', 0),
        'ongoing_supervisions': stats.get('total_orientacoes_andamento', 0)
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
        total_journal = sum(f.get('statistics', {}).get('journal_articles', 0) for f in faculty_data)
        total_books = sum(f.get('statistics', {}).get('books', 0) for f in faculty_data)
        total_chapters = sum(f.get('statistics', {}).get('book_chapters', 0) for f in faculty_data)
        total_superv_completed = sum(f.get('statistics', {}).get('completed_supervisions', 0) for f in faculty_data)
        total_superv_ongoing = sum(f.get('statistics', {}).get('ongoing_supervisions', 0) for f in faculty_data)
        print(f"Total publications across faculty: {total_pubs}")
        print(f"  - Journal articles: {total_journal}")
        print(f"  - Books: {total_books}")
        print(f"  - Book chapters: {total_chapters}")
        print(f"Total completed supervisions: {total_superv_completed}")
        print(f"Total ongoing supervisions: {total_superv_ongoing}")

if __name__ == '__main__':
    main()