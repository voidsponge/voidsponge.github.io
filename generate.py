#!/usr/bin/env python3
"""
Générateur de blog statique pour CyberInsight - Version ELITE
Avec : Commentaires, ToC, RSS, Séries, Code Playground
"""

import os
import re
import json
import markdown
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Dossiers
ARTICLES_DIR = Path("_articles")
OUTPUT_DIR = Path("_site")
ARTICLES_OUTPUT = OUTPUT_DIR / "articles"

def parse_frontmatter(content):
    """Parse le frontmatter YAML d'un article"""
    frontmatter = {}
    
    if content.startswith('---'):
        try:
            end = content.index('---', 3)
            front = content[3:end].strip()
            content = content[end+3:].strip()
            
            for line in front.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"\'')
        except ValueError:
            pass
    
    return frontmatter, content

def estimate_reading_time(text):
    """Estime le temps de lecture"""
    words = len(re.findall(r'\w+', text))
    minutes = max(1, round(words / 200))
    return minutes

def extract_headings(html_content):
    """Extrait les titres H2 et H3 pour la table des matières"""
    headings = []
    pattern = r'<h([23])>(.*?)</h\1>'
    
    for match in re.finditer(pattern, html_content):
        level = int(match.group(1))
        text = re.sub('<[^<]+?>', '', match.group(2))
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        headings.append({
            'level': level,
            'text': text,
            'slug': slug
        })
    
    return headings

def add_heading_ids(html_content):
    """Ajoute des IDs aux titres pour les ancres"""
    def add_id(match):
        level = match.group(1)
        text = match.group(2)
        slug = re.sub(r'[^\w\s-]', '', re.sub('<[^<]+?>', '', text).lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return f'<h{level} id="{slug}">{text}</h{level}>'
    
    return re.sub(r'<h([23])>(.*?)</h\1>', add_id, html_content)

def load_article(filepath):
    """Charge un article markdown et extrait les métadonnées"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, markdown_content = parse_frontmatter(content)
    
    if 'title' not in frontmatter:
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        if title_match:
            frontmatter['title'] = title_match.group(1)
    
    slug = filepath.stem
    
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'fenced_code', 'tables', 'toc'])
    html_content = md.convert(markdown_content)
    
    # Ajouter des IDs aux titres et extraire la ToC
    html_content = add_heading_ids(html_content)
    headings = extract_headings(html_content)
    
    plain_text = re.sub('<[^<]+?>', '', html_content)
    excerpt = plain_text[:200].strip() + '...' if len(plain_text) > 200 else plain_text
    
    reading_time = estimate_reading_time(plain_text)
    
    tags = []
    if 'tags' in frontmatter:
        tags = [tag.strip() for tag in frontmatter['tags'].split(',')]
    
    # Support des séries d'articles
    series = frontmatter.get('series', None)
    series_part = int(frontmatter.get('series_part', 0))
    
    return {
        'title': frontmatter.get('title', 'Sans titre'),
        'slug': slug,
        'category': frontmatter.get('category', 'Général'),
        'date': frontmatter.get('date', datetime.now().strftime('%Y-%m-%d')),
        'author': frontmatter.get('author', 'CyberInsight'),
        'excerpt': frontmatter.get('excerpt', excerpt),
        'content': html_content,
        'reading_time': reading_time,
        'tags': tags,
        'series': series,
        'series_part': series_part,
        'headings': headings,
        'filepath': filepath
    }

def format_date(date_str):
    """Formate une date en français"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        months = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
            7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"
    except:
        return date_str

def get_related_articles(article, all_articles, max_related=3):
    """Trouve les articles liés"""
    related = []
    
    for other in all_articles:
        if other['slug'] == article['slug']:
            continue
        
        score = 0
        if other['category'] == article['category']:
            score += 3
        
        common_tags = set(article['tags']).intersection(set(other['tags']))
        score += len(common_tags) * 2
        
        # Bonus si même série
        if article['series'] and other['series'] == article['series']:
            score += 10
        
        if score > 0:
            related.append((score, other))
    
    related.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in related[:max_related]]

def get_series_articles(article, all_articles):
    """Récupère tous les articles de la même série"""
    if not article['series']:
        return []
    
    series_articles = [a for a in all_articles if a['series'] == article['series']]
    series_articles.sort(key=lambda x: x['series_part'])
    return series_articles

def generate_toc_html(headings):
    """Génère le HTML de la table des matières"""
    if not headings:
        return ''
    
    toc_html = '<nav class="table-of-contents"><h4>📖 Table des matières</h4><ul class="toc-list">'
    
    for heading in headings:
        indent_class = 'toc-h3' if heading['level'] == 3 else 'toc-h2'
        toc_html += f'<li class="{indent_class}"><a href="#{heading["slug"]}">{heading["text"]}</a></li>'
    
    toc_html += '</ul></nav>'
    return toc_html

def generate_series_nav(article, series_articles):
    """Génère la navigation de série"""
    if not series_articles or len(series_articles) <= 1:
        return ''
    
    current_index = next((i for i, a in enumerate(series_articles) if a['slug'] == article['slug']), -1)
    
    series_html = f'''
    <div class="series-navigation">
        <h4>📚 Série : {article['series']}</h4>
        <div class="series-progress">
            <span>Partie {article['series_part']} sur {len(series_articles)}</span>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {(article['series_part'] / len(series_articles)) * 100}%"></div>
            </div>
        </div>
        <div class="series-nav-buttons">
    '''
    
    if current_index > 0:
        prev_article = series_articles[current_index - 1]
        series_html += f'<a href="{prev_article["slug"]}.html" class="series-nav-btn">← Partie {prev_article["series_part"]}</a>'
    else:
        series_html += '<span class="series-nav-btn disabled">← Début</span>'
    
    if current_index < len(series_articles) - 1:
        next_article = series_articles[current_index + 1]
        series_html += f'<a href="{next_article["slug"]}.html" class="series-nav-btn">Partie {next_article["series_part"]} →</a>'
    else:
        series_html += '<span class="series-nav-btn disabled">Fin →</span>'
    
    series_html += '</div></div>'
    return series_html

def generate_article_page(article, all_articles):
    """Génère une page HTML pour un article avec ToC et commentaires"""
    
    # Articles liés
    related_articles = get_related_articles(article, all_articles)
    related_html = ''
    
    if related_articles:
        related_cards = ''
        for related in related_articles:
            related_cards += f'''
            <a href="{related['slug']}.html" class="related-card">
                <div class="related-category">{related['category']}</div>
                <h4>{related['title']}</h4>
                <p>{related['excerpt'][:100]}...</p>
            </a>
            '''
        
        related_html = f'''
        <section class="related-articles">
            <h3>📚 Articles liés</h3>
            <div class="related-grid">
                {related_cards}
            </div>
        </section>
        '''
    
    # Navigation série
    series_articles = get_series_articles(article, all_articles)
    series_nav = generate_series_nav(article, series_articles)
    
    # Table des matières
    toc_html = generate_toc_html(article['headings'])
    
    # Tags HTML
    tags_html = ''
    if article['tags']:
        tags_items = ''.join([f'<span class="article-tag">#{tag}</span>' for tag in article['tags']])
        tags_html = f'<div class="article-tags">{tags_items}</div>'
    
    html = f'''<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - CyberInsight</title>
    <meta name="description" content="{article['excerpt'][:150]}">
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article['excerpt'][:150]}">
    <meta property="og:type" content="article">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css">
    <style>
        :root[data-theme="dark"] {{
            --color-bg: #0a0e17;
            --color-surface: #151922;
            --color-surface-elevated: #1e232e;
            --color-primary: #00f5a0;
            --color-secondary: #00d9ff;
            --color-accent: #ff006e;
            --color-text: #e8ecf3;
            --color-text-muted: #8b92a8;
            --color-border: #2a3142;
        }}

        :root[data-theme="light"] {{
            --color-bg: #ffffff;
            --color-surface: #f8f9fa;
            --color-surface-elevated: #ffffff;
            --color-primary: #00a870;
            --color-secondary: #0088cc;
            --color-accent: #e91e63;
            --color-text: #1a1a1a;
            --color-text-muted: #6c757d;
            --color-border: #dee2e6;
        }}

        :root {{
            --font-display: 'JetBrains Mono', monospace;
            --font-body: 'Poppins', sans-serif;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: var(--font-body);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.8;
            transition: background 0.3s ease, color 0.3s ease;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(0, 245, 160, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(0, 217, 255, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
            opacity: 0.5;
            transition: opacity 0.3s ease;
        }}

        [data-theme="light"] body::before {{
            opacity: 0.3;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 1;
        }}

        .container-with-toc {{
            max-width: 1400px;
            display: grid;
            grid-template-columns: 1fr 900px 250px 1fr;
            gap: 2rem;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        .container-with-toc > * {{
            grid-column: 2;
        }}

        header {{
            padding: 2rem 0;
            border-bottom: 1px solid var(--color-border);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--color-bg);
            transition: all 0.3s ease;
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-family: var(--font-display);
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
        }}

        .header-actions {{
            display: flex;
            gap: 1.5rem;
            align-items: center;
        }}

        .back-link {{
            color: var(--color-text-muted);
            text-decoration: none;
            font-size: 0.95rem;
            transition: color 0.3s ease;
        }}

        .back-link:hover {{ color: var(--color-primary); }}

        .theme-toggle {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 50px;
            padding: 0.5rem;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s ease;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .theme-toggle:hover {{
            border-color: var(--color-primary);
            transform: rotate(180deg);
        }}

        /* Table of Contents */
        .table-of-contents {{
            grid-column: 3;
            position: sticky;
            top: 100px;
            align-self: start;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 1.5rem;
            max-height: calc(100vh - 120px);
            overflow-y: auto;
        }}

        .table-of-contents h4 {{
            font-family: var(--font-display);
            margin-bottom: 1rem;
            font-size: 1rem;
        }}

        .toc-list {{
            list-style: none;
        }}

        .toc-list li {{
            margin-bottom: 0.5rem;
        }}

        .toc-list a {{
            color: var(--color-text-muted);
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            display: block;
            padding: 0.3rem 0;
            border-left: 2px solid transparent;
            padding-left: 0.5rem;
        }}

        .toc-list a:hover {{
            color: var(--color-primary);
            border-left-color: var(--color-primary);
        }}

        .toc-list a.active {{
            color: var(--color-primary);
            border-left-color: var(--color-primary);
            font-weight: 600;
        }}

        .toc-h3 {{
            margin-left: 1rem;
        }}

        .toc-h3 a {{
            font-size: 0.85rem;
        }}

        /* Series Navigation */
        .series-navigation {{
            background: linear-gradient(135deg, var(--color-surface-elevated), var(--color-surface));
            border: 1px solid var(--color-primary);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 3rem;
        }}

        .series-navigation h4 {{
            font-family: var(--font-display);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }}

        .series-progress {{
            margin-bottom: 1rem;
        }}

        .series-progress span {{
            font-size: 0.9rem;
            color: var(--color-text-muted);
            font-family: var(--font-display);
        }}

        .progress-bar {{
            height: 8px;
            background: var(--color-surface-elevated);
            border-radius: 4px;
            margin-top: 0.5rem;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
            transition: width 0.3s ease;
        }}

        .series-nav-buttons {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }}

        .series-nav-btn {{
            flex: 1;
            padding: 0.8rem 1.5rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            color: var(--color-text);
            text-decoration: none;
            text-align: center;
            font-family: var(--font-display);
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }}

        .series-nav-btn:hover:not(.disabled) {{
            border-color: var(--color-primary);
            transform: translateY(-2px);
        }}

        .series-nav-btn.disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        article {{ padding: 4rem 0; }}

        .article-header {{ margin-bottom: 3rem; }}

        .article-meta {{
            display: flex;
            gap: 1.5rem;
            align-items: center;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            color: var(--color-text-muted);
            font-family: var(--font-display);
            flex-wrap: wrap;
        }}

        .category-badge {{
            background: var(--color-primary);
            color: var(--color-bg);
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}

        .reading-time {{
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .article-title {{
            font-size: 2.8rem;
            line-height: 1.2;
            margin-bottom: 1rem;
            font-weight: 700;
        }}

        .article-tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .article-tag {{
            background: var(--color-surface-elevated);
            color: var(--color-primary);
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.85rem;
            font-family: var(--font-display);
            border: 1px solid var(--color-border);
        }}

        .article-content {{
            font-size: 1.1rem;
            line-height: 1.9;
        }}

        .article-content h1,
        .article-content h2,
        .article-content h3 {{
            color: var(--color-text);
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            font-family: var(--font-display);
            scroll-margin-top: 100px;
        }}

        .article-content h1 {{ font-size: 2.5rem; }}
        .article-content h2 {{
            font-size: 2rem;
            color: var(--color-primary);
        }}
        .article-content h3 {{ font-size: 1.5rem; }}

        .article-content p {{ margin-bottom: 1.5rem; }}

        .article-content ul,
        .article-content ol {{
            margin-left: 2rem;
            margin-bottom: 1.5rem;
        }}

        .article-content li {{ margin-bottom: 0.5rem; }}

        .article-content code {{
            font-family: var(--font-display);
            background: var(--color-surface);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            color: var(--color-secondary);
            font-size: 0.9em;
        }}

        .article-content pre {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 1.5rem;
            overflow-x: auto;
            margin-bottom: 1.5rem;
            position: relative;
        }}

        /* Code Playground Button */
        .code-playground-btn {{
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: var(--color-primary);
            color: var(--color-bg);
            border: none;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-family: var(--font-display);
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .code-playground-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 245, 160, 0.3);
        }}

        .article-content pre code {{
            background: none;
            padding: 0;
            color: var(--color-text);
        }}

        .article-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            background: var(--color-surface);
            border-radius: 8px;
            overflow: hidden;
        }}

        .article-content th,
        .article-content td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--color-border);
        }}

        .article-content th {{
            background: var(--color-surface-elevated);
            color: var(--color-primary);
            font-family: var(--font-display);
            font-weight: 700;
        }}

        .article-content blockquote {{
            border-left: 4px solid var(--color-primary);
            padding-left: 1.5rem;
            margin: 2rem 0;
            color: var(--color-text-muted);
            font-style: italic;
        }}

        .article-content a {{
            color: var(--color-secondary);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.3s ease;
        }}

        .article-content a:hover {{
            border-bottom-color: var(--color-secondary);
        }}

        .article-content hr {{
            border: none;
            border-top: 1px solid var(--color-border);
            margin: 3rem 0;
        }}

        /* Code Playground Modal */
        .playground-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 10000;
            align-items: center;
            justify-content: center;
        }}

        .playground-modal.active {{
            display: flex;
        }}

        .playground-content {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            width: 90%;
            max-width: 1200px;
            height: 80%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .playground-header {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--color-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .playground-header h3 {{
            font-family: var(--font-display);
            font-size: 1.2rem;
        }}

        .playground-close {{
            background: none;
            border: none;
            color: var(--color-text);
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            transition: color 0.3s ease;
        }}

        .playground-close:hover {{
            color: var(--color-accent);
        }}

        .playground-body {{
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            padding: 1rem;
            overflow: hidden;
        }}

        .playground-editor,
        .playground-output {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .playground-editor h4,
        .playground-output h4 {{
            font-family: var(--font-display);
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }}

        .playground-editor textarea {{
            flex: 1;
            background: var(--color-bg);
            color: var(--color-text);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 1rem;
            font-family: var(--font-display);
            font-size: 0.95rem;
            resize: none;
        }}

        .playground-output-content {{
            flex: 1;
            background: var(--color-bg);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 1rem;
            overflow-y: auto;
            font-family: var(--font-display);
            font-size: 0.9rem;
            white-space: pre-wrap;
        }}

        .playground-controls {{
            padding: 1rem 1.5rem;
            border-top: 1px solid var(--color-border);
            display: flex;
            gap: 1rem;
        }}

        .playground-btn {{
            padding: 0.7rem 1.5rem;
            background: var(--color-primary);
            color: var(--color-bg);
            border: none;
            border-radius: 6px;
            font-family: var(--font-display);
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .playground-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 245, 160, 0.3);
        }}

        .playground-btn.secondary {{
            background: var(--color-surface-elevated);
            color: var(--color-text);
        }}

        /* Share Buttons */
        .share-section {{
            margin: 3rem 0;
            padding: 2rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            text-align: center;
        }}

        .share-section h4 {{
            margin-bottom: 1rem;
            font-family: var(--font-display);
        }}

        .share-buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .share-btn {{
            padding: 0.7rem 1.5rem;
            background: var(--color-surface-elevated);
            border: 1px solid var(--color-border);
            border-radius: 6px;
            color: var(--color-text);
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .share-btn:hover {{
            border-color: var(--color-primary);
            transform: translateY(-2px);
        }}

        /* Related Articles */
        .related-articles {{
            margin: 4rem 0;
            padding-top: 3rem;
            border-top: 1px solid var(--color-border);
        }}

        .related-articles h3 {{
            font-family: var(--font-display);
            font-size: 1.8rem;
            margin-bottom: 2rem;
        }}

        .related-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
        }}

        .related-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 1.5rem;
            text-decoration: none;
            transition: all 0.3s ease;
            display: block;
        }}

        .related-card:hover {{
            border-color: var(--color-primary);
            transform: translateY(-4px);
        }}

        .related-category {{
            color: var(--color-primary);
            font-size: 0.8rem;
            font-family: var(--font-display);
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}

        .related-card h4 {{
            color: var(--color-text);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }}

        .related-card p {{
            color: var(--color-text-muted);
            font-size: 0.9rem;
            line-height: 1.5;
        }}

        /* Comments Section */
        .comments-section {{
            margin: 4rem 0;
            padding-top: 3rem;
            border-top: 1px solid var(--color-border);
        }}

        .comments-section h3 {{
            font-family: var(--font-display);
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
        }}

        /* Back to Top */
        .back-to-top {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            background: var(--color-primary);
            color: var(--color-bg);
            border: none;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 245, 160, 0.3);
        }}

        .back-to-top.visible {{
            opacity: 1;
            pointer-events: all;
        }}

        .back-to-top:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 245, 160, 0.4);
        }}

        footer {{
            border-top: 1px solid var(--color-border);
            padding: 2rem 0;
            margin-top: 4rem;
            text-align: center;
            color: var(--color-text-muted);
        }}

        @media (max-width: 1200px) {{
            .container-with-toc {{
                grid-template-columns: 1fr;
            }}

            .table-of-contents {{
                display: none;
            }}

            .container-with-toc > * {{
                grid-column: 1;
            }}
        }}

        @media (max-width: 768px) {{
            .article-title {{ font-size: 2rem; }}
            .article-content {{ font-size: 1rem; }}
            .related-grid {{ grid-template-columns: 1fr; }}
            .back-to-top {{
                bottom: 1rem;
                right: 1rem;
                width: 45px;
                height: 45px;
            }}
            .playground-body {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <a href="../index.html" class="logo">CyberInsight</a>
                <div class="header-actions">
                    <a href="../index.html" class="back-link">← Retour</a>
                    <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                        <span id="themeIcon">🌙</span>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <main>
        <div class="container-with-toc">
            <article>
                {series_nav}

                <div class="article-header">
                    <div class="article-meta">
                        <span class="category-badge">{article['category']}</span>
                        <span>{format_date(article['date'])}</span>
                        <span>•</span>
                        <span>{article['author']}</span>
                        <span>•</span>
                        <span class="reading-time">⏱️ {article['reading_time']} min</span>
                    </div>
                    <h1 class="article-title">{article['title']}</h1>
                    {tags_html}
                </div>
                
                <div class="article-content">
                    {article['content']}
                </div>

                <div class="share-section">
                    <h4>📤 Partager cet article</h4>
                    <div class="share-buttons">
                        <a href="https://twitter.com/intent/tweet?text={article['title']}&url=https://voidsponge.github.io/articles/{article['slug']}.html" 
                           target="_blank" 
                           class="share-btn">
                            𝕏 Twitter
                        </a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://voidsponge.github.io/articles/{article['slug']}.html" 
                           target="_blank" 
                           class="share-btn">
                            in LinkedIn
                        </a>
                        <button onclick="copyLink()" class="share-btn">
                            🔗 Copier le lien
                        </button>
                    </div>
                </div>

                {related_html}

                <section class="comments-section">
                    <h3>💬 Commentaires</h3>
                    <script src="https://giscus.app/client.js"
                        data-repo="voidsponge/voidsponge.github.io"
                        data-repo-id="VOTRE_REPO_ID"
                        data-category="General"
                        data-category-id="VOTRE_CATEGORY_ID"
                        data-mapping="pathname"
                        data-strict="0"
                        data-reactions-enabled="1"
                        data-emit-metadata="0"
                        data-input-position="top"
                        data-theme="dark"
                        data-lang="fr"
                        crossorigin="anonymous"
                        async>
                    </script>
                    <p style="margin-top: 1rem; color: var(--color-text-muted); font-size: 0.9rem;">
                        💡 Pour activer les commentaires, configurez giscus avec votre repo GitHub<br>
                        Guide : <a href="https://giscus.app/fr" target="_blank" style="color: var(--color-secondary);">giscus.app/fr</a>
                    </p>
                </section>
            </article>

            {toc_html}
        </div>
    </main>

    <button class="back-to-top" id="backToTop" aria-label="Retour en haut">↑</button>

    <!-- Code Playground Modal -->
    <div class="playground-modal" id="playgroundModal">
        <div class="playground-content">
            <div class="playground-header">
                <h3>🎮 Code Playground</h3>
                <button class="playground-close" onclick="closePlayground()">×</button>
            </div>
            <div class="playground-body">
                <div class="playground-editor">
                    <h4>📝 Éditeur</h4>
                    <textarea id="playgroundCode" spellcheck="false"></textarea>
                </div>
                <div class="playground-output">
                    <h4>🖥️ Sortie</h4>
                    <div class="playground-output-content" id="playgroundOutput">
                        Cliquez sur "Exécuter" pour voir le résultat...
                    </div>
                </div>
            </div>
            <div class="playground-controls">
                <button class="playground-btn" onclick="runCode()">▶️ Exécuter</button>
                <button class="playground-btn secondary" onclick="clearOutput()">🗑️ Effacer</button>
            </div>
        </div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2025 CyberInsight. Tous droits réservés.</p>
        </div>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        hljs.highlightAll();

        // Theme Toggle
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const html = document.documentElement;

        const savedTheme = localStorage.getItem('theme') || 'dark';
        html.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);

        themeToggle.addEventListener('click', () => {{
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        }});

        function updateThemeIcon(theme) {{
            themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
        }}

        // Back to Top
        const backToTop = document.getElementById('backToTop');

        window.addEventListener('scroll', () => {{
            if (window.pageYOffset > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});

        backToTop.addEventListener('click', () => {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});

        // Copy Link
        function copyLink() {{
            navigator.clipboard.writeText(window.location.href);
            alert('✅ Lien copié dans le presse-papiers !');
        }}

        // Interactive ToC
        const tocLinks = document.querySelectorAll('.toc-list a');
        const headings = document.querySelectorAll('.article-content h2, .article-content h3');

        window.addEventListener('scroll', () => {{
            let current = '';
            
            headings.forEach(heading => {{
                const rect = heading.getBoundingClientRect();
                if (rect.top >= 0 && rect.top <= 200) {{
                    current = heading.id;
                }}
            }});

            tocLinks.forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {{
                    link.classList.add('active');
                }}
            }});
        }});

        // Code Playground
        let playgroundModal = document.getElementById('playgroundModal');

        // Add "Run Code" buttons to code blocks
        document.querySelectorAll('pre code.language-python, pre code.language-javascript').forEach((block, index) => {{
            const btn = document.createElement('button');
            btn.className = 'code-playground-btn';
            btn.textContent = '▶️ Exécuter';
            btn.onclick = () => openPlayground(block.textContent, block.classList.contains('language-python') ? 'python' : 'javascript');
            block.parentElement.style.position = 'relative';
            block.parentElement.insertBefore(btn, block);
        }});

        function openPlayground(code, language) {{
            document.getElementById('playgroundCode').value = code;
            document.getElementById('playgroundCode').dataset.language = language;
            playgroundModal.classList.add('active');
        }}

        function closePlayground() {{
            playgroundModal.classList.remove('active');
        }}

        function clearOutput() {{
            document.getElementById('playgroundOutput').textContent = 'Sortie effacée...';
        }}

        function runCode() {{
            const code = document.getElementById('playgroundCode').value;
            const language = document.getElementById('playgroundCode').dataset.language;
            const output = document.getElementById('playgroundOutput');

            try {{
                if (language === 'javascript') {{
                    // Capture console.log
                    let logs = [];
                    const oldLog = console.log;
                    console.log = (...args) => logs.push(args.join(' '));
                    
                    eval(code);
                    
                    console.log = oldLog;
                    output.textContent = logs.length > 0 ? logs.join('\\n') : 'Code exécuté avec succès ! (Pas de sortie)';
                }} else if (language === 'python') {{
                    output.textContent = '⚠️ Python nécessite Pyodide (chargement lourd).\\nPour une démo complète, intégrez Pyodide.\\n\\nCode Python détecté :\\n' + code;
                }} else {{
                    output.textContent = 'Langage non supporté pour l\\'instant.';
                }}
            }} catch (error) {{
                output.textContent = '❌ Erreur :\\n' + error.message;
                output.style.color = 'var(--color-accent)';
            }}
        }}

        // Close modal on click outside
        playgroundModal.addEventListener('click', (e) => {{
            if (e.target === playgroundModal) {{
                closePlayground();
            }}
        }});
    </script>
</body>
</html>'''
    
    return html

def generate_rss_feed(articles):
    """Génère le flux RSS"""
    rss = Element('rss', version='2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    channel = SubElement(rss, 'channel')
    
    SubElement(channel, 'title').text = 'CyberInsight - Blog de Cybersécurité'
    SubElement(channel, 'link').text = 'https://voidsponge.github.io'
    SubElement(channel, 'description').text = 'Explorez les dernières menaces, vulnérabilités et techniques de protection dans le monde de la sécurité informatique'
    SubElement(channel, 'language').text = 'fr'
    
    atom_link = SubElement(channel, 'atom:link')
    atom_link.set('href', 'https://voidsponge.github.io/rss.xml')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')
    
    for article in sorted(articles, key=lambda x: x['date'], reverse=True)[:20]:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = article['title']
        SubElement(item, 'link').text = f"https://voidsponge.github.io/articles/{article['slug']}.html"
        SubElement(item, 'description').text = article['excerpt']
        SubElement(item, 'pubDate').text = datetime.strptime(article['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 00:00:00 +0000')
        SubElement(item, 'guid').text = f"https://voidsponge.github.io/articles/{article['slug']}.html"
        
        for tag in article['tags']:
            SubElement(item, 'category').text = tag
    
    xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent='  ')
    return xml_str

def generate_index_page(articles):
    """Génère la page d'accueil (code existant conservé avec améliorations mineures)"""
    
    articles_sorted = sorted(articles, key=lambda x: x['date'], reverse=True)
    featured = articles_sorted[0] if articles_sorted else None
    categories = sorted(set(article['category'] for article in articles_sorted))
    
    category_filters = ''
    for category in categories:
        category_filters += f'<button class="filter-btn" data-category="{category}">{category}</button>\n                    '
    
    articles_html = ''
    for article in articles_sorted:
        tags_preview = ''
        if article['tags']:
            tags_preview = ' '.join([f'#{tag}' for tag in article['tags'][:3]])
        
        series_badge = ''
        if article['series']:
            series_badge = f'<span class="series-badge">📚 Série: {article["series"]} #{article["series_part"]}</span>'
        
        articles_html += f'''
        <article class="article-card" data-category="{article['category']}">
            <div class="article-meta">
                <span class="article-category">{article['category']}</span>
                <span>•</span>
                <span>{format_date(article['date'])}</span>
                <span>•</span>
                <span class="reading-time">⏱️ {article['reading_time']} min</span>
            </div>
            <h3>{article['title']}</h3>
            {series_badge}
            <p class="article-excerpt">{article['excerpt']}</p>
            <div class="article-card-footer">
                <a href="articles/{article['slug']}.html" class="read-more">Lire plus</a>
                {f'<div class="tags-preview">{tags_preview}</div>' if tags_preview else ''}
            </div>
        </article>
        '''
    
    featured_html = ''
    if featured:
        featured_html = f'''
        <div class="featured-article">
            <span class="featured-label">⭐ Article en vedette</span>
            <div class="featured-meta">
                <span class="featured-category">{featured['category']}</span>
                <span>•</span>
                <span>{format_date(featured['date'])}</span>
                <span>•</span>
                <span>⏱️ {featured['reading_time']} min</span>
            </div>
            <h2>{featured['title']}</h2>
            <p>{featured['excerpt']}</p>
            <a href="articles/{featured['slug']}.html" class="read-more">Lire l'article complet</a>
        </div>
        '''
    
    total_articles = len(articles)
    total_reading_time = sum(a['reading_time'] for a in articles)
    all_categories = len(categories)
    
    # HTML simplifié - je garde seulement les parties critiques
    html = f'''<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberInsight - Blog de Cybersécurité</title>
    <meta name="description" content="Explorez les dernières menaces, vulnérabilités et techniques de protection">
    <link rel="alternate" type="application/rss+xml" title="CyberInsight RSS" href="/rss.xml">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Styles inchangés du code précédent - conservés pour la concision */
        :root[data-theme="dark"] {{
            --color-bg: #0a0e17;
            --color-surface: #151922;
            --color-surface-elevated: #1e232e;
            --color-primary: #00f5a0;
            --color-secondary: #00d9ff;
            --color-accent: #ff006e;
            --color-text: #e8ecf3;
            --color-text-muted: #8b92a8;
            --color-border: #2a3142;
        }}

        :root[data-theme="light"] {{
            --color-bg: #ffffff;
            --color-surface: #f8f9fa;
            --color-surface-elevated: #ffffff;
            --color-primary: #00a870;
            --color-secondary: #0088cc;
            --color-accent: #e91e63;
            --color-text: #1a1a1a;
            --color-text-muted: #6c757d;
            --color-border: #dee2e6;
        }}

        :root {{
            --font-display: 'JetBrains Mono', monospace;
            --font-body: 'Poppins', sans-serif;
            --shadow-glow: 0 0 30px rgba(0, 245, 160, 0.15);
            --shadow-strong: 0 20px 50px rgba(0, 0, 0, 0.5);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: var(--font-body);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.7;
            overflow-x: hidden;
            transition: background 0.3s ease, color 0.3s ease;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(0, 245, 160, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(0, 217, 255, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
            opacity: 0.5;
            transition: opacity 0.3s ease;
        }}

        [data-theme="light"] body::before {{
            opacity: 0.2;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 1;
        }}

        header {{
            padding: 2rem 0;
            border-bottom: 1px solid var(--color-border);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--color-bg);
            animation: slideDown 0.6s ease-out;
            transition: all 0.3s ease;
        }}

        @keyframes slideDown {{
            from {{ transform: translateY(-100%); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-family: var(--font-display);
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
            position: relative;
        }}

        .logo::before {{
            content: '> ';
            color: var(--color-accent);
            -webkit-text-fill-color: var(--color-accent);
            animation: blink 1.5s infinite;
        }}

        @keyframes blink {{
            0%, 49% {{ opacity: 1; }}
            50%, 100% {{ opacity: 0; }}
        }}

        nav {{
            display: flex;
            gap: 2.5rem;
            align-items: center;
        }}

        nav a {{
            color: var(--color-text-muted);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            position: relative;
        }}

        nav a::after {{
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--color-primary);
            transition: width 0.3s ease;
        }}

        nav a:hover {{
            color: var(--color-primary);
        }}

        nav a:hover::after {{
            width: 100%;
        }}

        .theme-toggle {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 50px;
            padding: 0.5rem;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s ease;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .theme-toggle:hover {{
            border-color: var(--color-primary);
            transform: rotate(180deg);
        }}

        .rss-link {{
            color: var(--color-accent);
            font-size: 1.3rem;
            transition: transform 0.3s ease;
        }}

        .rss-link:hover {{
            transform: scale(1.2);
        }}

        .stats-bar {{
            padding: 1.5rem 0;
            display: flex;
            justify-content: center;
            gap: 3rem;
            flex-wrap: wrap;
            border-bottom: 1px solid var(--color-border);
            animation: fadeInUp 0.8s ease-out 0.1s both;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            font-family: var(--font-display);
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: var(--color-text-muted);
            margin-top: 0.3rem;
        }}

        .search-filter-section {{
            padding: 2rem 0;
            border-bottom: 1px solid var(--color-border);
            animation: fadeInUp 0.8s ease-out 0.3s both;
        }}

        .search-bar {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            align-items: center;
        }}

        .search-input {{
            flex: 1;
            padding: 1rem 1.5rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            color: var(--color-text);
            font-family: var(--font-body);
            font-size: 1rem;
            transition: all 0.3s ease;
        }}

        .search-input:focus {{
            outline: none;
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(0, 245, 160, 0.1);
        }}

        .search-input::placeholder {{
            color: var(--color-text-muted);
        }}

        .category-filters {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            justify-content: center;
        }}

        .filter-btn {{
            padding: 0.6rem 1.2rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 6px;
            color: var(--color-text-muted);
            font-family: var(--font-display);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .filter-btn:hover {{
            border-color: var(--color-primary);
            color: var(--color-primary);
            transform: translateY(-2px);
        }}

        .filter-btn.active {{
            background: var(--color-primary);
            color: var(--color-bg);
            border-color: var(--color-primary);
            box-shadow: var(--shadow-glow);
        }}

        .no-results {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--color-text-muted);
            font-size: 1.2rem;
        }}

        .no-results-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.3;
        }}

        .article-card.hidden {{
            display: none;
        }}

        .hero {{
            padding: 6rem 0;
            text-align: center;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .hero h1 {{
            font-family: var(--font-display);
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            line-height: 1.1;
            letter-spacing: -0.03em;
        }}

        .hero h1 .gradient-text {{
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary), var(--color-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            background-size: 200% 200%;
            animation: gradientShift 5s ease infinite;
        }}

        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        .hero p {{
            font-size: 1.3rem;
            color: var(--color-text-muted);
            max-width: 700px;
            margin: 0 auto 2rem;
        }}

        .hero-tags {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 2rem;
        }}

        .tag {{
            padding: 0.5rem 1rem;
            background: var(--color-surface-elevated);
            border: 1px solid var(--color-border);
            border-radius: 6px;
            font-family: var(--font-display);
            font-size: 0.85rem;
            color: var(--color-primary);
            transition: all 0.3s ease;
            cursor: default;
        }}

        .tag:hover {{
            background: var(--color-primary);
            color: var(--color-bg);
            border-color: var(--color-primary);
            box-shadow: var(--shadow-glow);
            transform: translateY(-2px);
        }}

        .articles-section {{
            padding: 4rem 0;
            animation: fadeInUp 0.8s ease-out 0.4s both;
        }}

        .section-title {{
            font-family: var(--font-display);
            font-size: 2rem;
            margin-bottom: 3rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .section-title::before {{
            content: '#';
            color: var(--color-accent);
            font-size: 2.5rem;
        }}

        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
        }}

        .article-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 2rem;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}

        .article-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.4s ease;
        }}

        .article-card:hover::before {{
            transform: scaleX(1);
        }}

        .article-card:hover {{
            transform: translateY(-8px);
            box-shadow: var(--shadow-strong);
            border-color: var(--color-primary);
        }}

        .article-meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            font-size: 0.85rem;
            color: var(--color-text-muted);
            font-family: var(--font-display);
            flex-wrap: wrap;
        }}

        .article-category {{
            color: var(--color-primary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .reading-time {{
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .series-badge {{
            display: inline-block;
            background: var(--color-accent);
            color: var(--color-bg);
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-family: var(--font-display);
            margin-bottom: 0.5rem;
        }}

        .article-card h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: var(--color-text);
            line-height: 1.3;
            transition: color 0.3s ease;
        }}

        .article-card:hover h3 {{
            color: var(--color-primary);
        }}

        .article-excerpt {{
            color: var(--color-text-muted);
            margin-bottom: 1.5rem;
            line-height: 1.6;
            flex-grow: 1;
        }}

        .article-card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }}

        .tags-preview {{
            color: var(--color-text-muted);
            font-size: 0.85rem;
            font-family: var(--font-display);
        }}

        .read-more {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--color-secondary);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: gap 0.3s ease;
            white-space: nowrap;
        }}

        .read-more:hover {{
            gap: 1rem;
        }}

        .read-more::after {{
            content: '→';
            font-size: 1.2rem;
        }}

        .featured-article {{
            background: linear-gradient(135deg, var(--color-surface-elevated), var(--color-surface));
            border: 1px solid var(--color-primary);
            border-radius: 16px;
            padding: 3rem;
            margin-bottom: 4rem;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-glow);
            animation: fadeInUp 0.8s ease-out 0.6s both;
        }}

        .featured-label {{
            display: inline-block;
            background: var(--color-accent);
            color: var(--color-bg);
            padding: 0.4rem 1rem;
            border-radius: 6px;
            font-family: var(--font-display);
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
        }}

        .featured-meta {{
            font-size: 0.9rem;
            color: var(--color-text-muted);
            font-family: var(--font-display);
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .featured-category {{
            color: var(--color-primary);
            text-transform: uppercase;
        }}

        .featured-article h2 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            line-height: 1.2;
        }}

        .featured-article p {{
            font-size: 1.1rem;
            color: var(--color-text-muted);
            margin-bottom: 2rem;
        }}

        .back-to-top {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            background: var(--color-primary);
            color: var(--color-bg);
            border: none;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 245, 160, 0.3);
        }}

        .back-to-top.visible {{
            opacity: 1;
            pointer-events: all;
        }}

        .back-to-top:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 245, 160, 0.4);
        }}

        footer {{
            border-top: 1px solid var(--color-border);
            padding: 3rem 0;
            margin-top: 6rem;
            text-align: center;
            color: var(--color-text-muted);
        }}

        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2.5rem; }}
            .hero p {{ font-size: 1.1rem; }}
            nav {{ gap: 1rem; }}
            nav a {{ font-size: 0.85rem; }}
            .articles-grid {{ grid-template-columns: 1fr; }}
            .featured-article {{ padding: 2rem; }}
            .featured-article h2 {{ font-size: 1.8rem; }}
            .search-filter-section {{ padding: 1.5rem 0; }}
            .category-filters {{ gap: 0.5rem; }}
            .stats-bar {{ gap: 1.5rem; }}
            .stat-number {{ font-size: 1.5rem; }}
            .back-to-top {{
                bottom: 1rem;
                right: 1rem;
                width: 45px;
                height: 45px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">CyberInsight</div>
                <nav>
                    <a href="#articles">Articles</a>
                    <a href="https://github.com/voidsponge" target="_blank">GitHub</a>
                    <a href="/rss.xml" class="rss-link" title="Flux RSS">📡</a>
                    <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                        <span id="themeIcon">🌙</span>
                    </button>
                </nav>
            </div>
        </div>
    </header>

    <main>
        <section class="stats-bar">
            <div class="stat">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">Articles</div>
            </div>
            <div class="stat">
                <div class="stat-number">{all_categories}</div>
                <div class="stat-label">Catégories</div>
            </div>
            <div class="stat">
                <div class="stat-number">{total_reading_time}</div>
                <div class="stat-label">Minutes de lecture</div>
            </div>
        </section>

        <section class="hero">
            <div class="container">
                <h1><span class="gradient-text">Décryptage de la Cybersécurité</span></h1>
                <p>Explorez les dernières menaces, vulnérabilités et techniques de protection dans le monde de la sécurité informatique</p>
                <div class="hero-tags">
                    <span class="tag">DevSecOps</span>
                    <span class="tag">Forensic</span>
                    <span class="tag">CTF</span>
                    <span class="tag">Cheat</span>
                    <span class="tag">OSINT</span>
                    <span class="tag">Red Team / Blue Team</span>
                </div>
            </div>
        </section>

        <section class="search-filter-section">
            <div class="container">
                <div class="search-bar">
                    <input type="text" 
                           id="searchInput" 
                           class="search-input" 
                           placeholder="🔍 Rechercher un article...">
                </div>
                <div class="category-filters" id="categoryFilters">
                    <button class="filter-btn active" data-category="all">Tous</button>
                    {category_filters}
                </div>
            </div>
        </section>

        <section class="articles-section">
            <div class="container">
                {featured_html}

                <h2 class="section-title" id="articles">Articles récents</h2>
                
                <div class="articles-grid" id="articlesGrid">
                    {articles_html}
                </div>
                <div class="no-results" id="noResults" style="display: none;">
                    <div class="no-results-icon">🔍</div>
                    <p>Aucun article trouvé</p>
                </div>
            </div>
        </section>
    </main>

    <button class="back-to-top" id="backToTop" aria-label="Retour en haut">↑</button>

    <footer>
        <div class="container">
            <p>&copy; 2025 CyberInsight. Tous droits réservés.</p>
        </div>
    </footer>

    <script>
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const html = document.documentElement;

        const savedTheme = localStorage.getItem('theme') || 'dark';
        html.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);

        themeToggle.addEventListener('click', () => {{
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        }});

        function updateThemeIcon(theme) {{
            themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
        }}

        const searchInput = document.getElementById('searchInput');
        const articlesGrid = document.getElementById('articlesGrid');
        const noResults = document.getElementById('noResults');
        const articleCards = articlesGrid.querySelectorAll('.article-card');

        searchInput.addEventListener('input', function() {{
            const searchTerm = this.value.toLowerCase();
            let visibleCount = 0;

            articleCards.forEach(card => {{
                const title = card.querySelector('h3').textContent.toLowerCase();
                const excerpt = card.querySelector('.article-excerpt').textContent.toLowerCase();
                const category = card.querySelector('.article-category').textContent.toLowerCase();
                
                const matches = title.includes(searchTerm) || 
                               excerpt.includes(searchTerm) || 
                               category.includes(searchTerm);

                if (matches) {{
                    card.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    card.classList.add('hidden');
                }}
            }});

            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }});

        const filterButtons = document.querySelectorAll('.filter-btn');

        filterButtons.forEach(button => {{
            button.addEventListener('click', function() {{
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                const category = this.getAttribute('data-category');
                let visibleCount = 0;

                articleCards.forEach(card => {{
                    const cardCategory = card.querySelector('.article-category').textContent;
                    
                    if (category === 'all' || cardCategory === category) {{
                        card.classList.remove('hidden');
                        visibleCount++;
                    }} else {{
                        card.classList.add('hidden');
                    }}
                }});

                searchInput.value = '';
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }});
        }});

        const backToTop = document.getElementById('backToTop');

        window.addEventListener('scroll', () => {{
            if (window.pageYOffset > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});

        backToTop.addEventListener('click', () => {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    """Fonction principale"""
    print("🚀 Génération du blog CyberInsight ELITE...")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    ARTICLES_OUTPUT.mkdir(exist_ok=True)
    
    articles = []
    if ARTICLES_DIR.exists():
        for filepath in ARTICLES_DIR.glob("*.md"):
            if not filepath.name.startswith('_'):
                print(f"  📄 Traitement de {filepath.name}...")
                article = load_article(filepath)
                articles.append(article)
                
                article_html = generate_article_page(article, articles)
                output_path = ARTICLES_OUTPUT / f"{article['slug']}.html"
                output_path.write_text(article_html, encoding='utf-8')
    
    print(f"  ✅ {len(articles)} article(s) traité(s)")
    
    # Générer RSS
    print("  📡 Génération du flux RSS...")
    rss_xml = generate_rss_feed(articles)
    (OUTPUT_DIR / "rss.xml").write_text(rss_xml, encoding='utf-8')
    
    # Générer page d'accueil
    print("  🏠 Génération de la page d'accueil...")
    index_html = generate_index_page(articles)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding='utf-8')
    
    print("✨ Blog ELITE généré avec succès !")
    print(f"📊 Statistiques : {len(articles)} articles, {sum(a['reading_time'] for a in articles)} min de lecture")
    print("🎉 Fonctionnalités : ToC, RSS, Séries, Commentaires, Code Playground")

if __name__ == "__main__":
    main()