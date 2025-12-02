#!/usr/bin/env python3
"""
Générateur de blog CyberInsight - Style MATRIX HACKER
"""

import os
import re
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
    """Parse le frontmatter YAML"""
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

def load_article(filepath):
    """Charge et parse un article"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, markdown_content = parse_frontmatter(content)
    html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'codehilite'])
    
    slug = filepath.stem
    
    article = {
        'slug': slug,
        'title': frontmatter.get('title', 'Sans titre'),
        'date': frontmatter.get('date', '2025-01-01'),
        'category': frontmatter.get('category', 'General'),
        'tags': [t.strip() for t in frontmatter.get('tags', '').split(',') if t.strip()],
        'excerpt': frontmatter.get('excerpt', ''),
        'content': html_content,
        'reading_time': estimate_reading_time(markdown_content),
        'series': frontmatter.get('series', ''),
        'series_part': int(frontmatter.get('series_part', 0)) if frontmatter.get('series_part') else 0
    }
    
    return article

def get_related_articles(article, all_articles, limit=3):
    """Trouve les articles liés"""
    scored_articles = []
    
    for other in all_articles:
        if other['slug'] == article['slug']:
            continue
        
        score = 0
        if other['category'] == article['category']:
            score += 3
        
        common_tags = set(article['tags']) & set(other['tags'])
        score += len(common_tags) * 2
        
        if article.get('series') and other.get('series') == article['series']:
            score += 10
        
        if score > 0:
            scored_articles.append((score, other))
    
    scored_articles.sort(reverse=True, key=lambda x: x[0])
    return [a[1] for a in scored_articles[:limit]]

def generate_article_page(article, all_articles):
    """Génère la page HTML d'un article avec style MATRIX"""
    related_articles = get_related_articles(article, all_articles)
    
    related_html = ""
    for related in related_articles:
        related_html += f"""
        <article class="related-card">
            <span class="terminal-prompt">></span>
            <h4><a href="/articles/{related['slug']}.html">{related['title']}</a></h4>
            <div class="related-meta">
                <span class="category-tag">{related['category']}</span>
                <span>⏱ {related['reading_time']} min</span>
            </div>
        </article>
        """
    
    tags_html = ""
    for tag in article['tags']:
        tags_html += f'<span class="tag">#{tag}</span>'
    
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CyberInsight</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Courier New', monospace;
            background: #000000;
            color: #00ff00;
            line-height: 1.8;
            overflow-x: hidden;
        }}

        /* MATRIX RAIN BACKGROUND */
        #matrix-canvas {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.15;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            position: relative;
            z-index: 1;
        }}

        /* HEADER */
        header {{
            border-bottom: 2px solid #00ff00;
            padding: 1rem 0 2rem 0;
            margin-bottom: 3rem;
            text-shadow: 0 0 10px #00ff00;
        }}

        .logo {{
            font-size: 2rem;
            color: #00ff00;
            text-decoration: none;
            font-weight: bold;
            text-shadow: 0 0 20px #00ff00;
            animation: flicker 3s infinite alternate;
        }}

        @keyframes flicker {{
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{
                text-shadow: 0 0 20px #00ff00, 0 0 40px #00ff00;
            }}
            20%, 24%, 55% {{
                text-shadow: none;
            }}
        }}

        nav {{
            margin-top: 1rem;
        }}

        nav a {{
            color: #00ff00;
            text-decoration: none;
            margin-right: 2rem;
            transition: all 0.3s;
        }}

        nav a:hover {{
            text-shadow: 0 0 10px #00ff00;
            color: #00ff88;
        }}

        /* ARTICLE */
        .article-header {{
            margin-bottom: 3rem;
            border: 1px solid #00ff00;
            padding: 2rem;
            background: rgba(0, 255, 0, 0.03);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.1);
        }}

        h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #00ff00;
            text-shadow: 0 0 15px #00ff00;
        }}

        .article-meta {{
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
            color: #00aa00;
            font-size: 0.9rem;
        }}

        .category-tag {{
            background: #00ff00;
            color: #000;
            padding: 0.3rem 0.8rem;
            border-radius: 3px;
            font-weight: bold;
        }}

        .tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .tag {{
            color: #00aa00;
            border: 1px solid #00aa00;
            padding: 0.2rem 0.6rem;
            border-radius: 3px;
            font-size: 0.85rem;
        }}

        /* CONTENT */
        .article-content {{
            border-left: 2px solid #00ff00;
            padding-left: 2rem;
            margin: 3rem 0;
        }}

        .article-content h2 {{
            color: #00ff00;
            margin: 2rem 0 1rem 0;
            font-size: 1.8rem;
            text-shadow: 0 0 10px #00ff00;
        }}

        .article-content h3 {{
            color: #00cc00;
            margin: 1.5rem 0 1rem 0;
            font-size: 1.4rem;
        }}

        .article-content p {{
            margin: 1rem 0;
            color: #00dd00;
            line-height: 1.8;
        }}

        .article-content code {{
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid #00aa00;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            color: #00ff00;
        }}

        .article-content pre {{
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            padding: 1rem;
            overflow-x: auto;
            margin: 1.5rem 0;
            box-shadow: inset 0 0 20px rgba(0, 255, 0, 0.1);
        }}

        .article-content pre code {{
            background: none;
            border: none;
            padding: 0;
        }}

        .article-content ul, .article-content ol {{
            margin: 1rem 0 1rem 2rem;
            color: #00dd00;
        }}

        .article-content li {{
            margin: 0.5rem 0;
        }}

        .article-content a {{
            color: #00ff88;
            text-decoration: none;
            border-bottom: 1px dashed #00ff88;
        }}

        .article-content a:hover {{
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
        }}

        /* RELATED ARTICLES */
        .related-section {{
            margin-top: 4rem;
            padding: 2rem;
            border: 1px solid #00ff00;
            background: rgba(0, 255, 0, 0.02);
        }}

        .related-section h3 {{
            color: #00ff00;
            margin-bottom: 1.5rem;
            text-shadow: 0 0 10px #00ff00;
        }}

        .related-card {{
            padding: 1rem;
            border-left: 2px solid #00aa00;
            margin-bottom: 1rem;
            background: rgba(0, 255, 0, 0.02);
            transition: all 0.3s;
        }}

        .related-card:hover {{
            border-left-color: #00ff00;
            background: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
        }}

        .terminal-prompt {{
            color: #00ff00;
            margin-right: 0.5rem;
            font-weight: bold;
        }}

        .related-card h4 {{
            color: #00dd00;
            margin-bottom: 0.5rem;
        }}

        .related-card h4 a {{
            color: #00dd00;
            text-decoration: none;
        }}

        .related-card h4 a:hover {{
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }}

        .related-meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.85rem;
            color: #00aa00;
            margin-top: 0.5rem;
        }}

        /* BACK BUTTON */
        .back-btn {{
            display: inline-block;
            margin-top: 3rem;
            padding: 0.8rem 1.5rem;
            border: 2px solid #00ff00;
            color: #00ff00;
            text-decoration: none;
            transition: all 0.3s;
            background: rgba(0, 0, 0, 0.5);
        }}

        .back-btn:hover {{
            background: #00ff00;
            color: #000;
            box-shadow: 0 0 20px #00ff00;
        }}

        footer {{
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 2px solid #00ff00;
            text-align: center;
            color: #00aa00;
        }}

        /* SCROLLBAR */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: #000;
        }}

        ::-webkit-scrollbar-thumb {{
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #00ff88;
        }}
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>

    <div class="container">
        <header>
            <a href="/" class="logo">CyberInsight</a>
            <nav>
                <a href="/">← Accueil</a>
                <a href="https://github.com/voidsponge" target="_blank">GitHub</a>
            </nav>
        </header>

        <main>
            <div class="article-header">
                <h1>{title}</h1>
                <div class="article-meta">
                    <span class="category-tag">{category}</span>
                    <span>📅 {date}</span>
                    <span>⏱ {reading_time} min</span>
                </div>
                <div class="tags">
                    {tags_html}
                </div>
            </div>

            <article class="article-content">
                {content}
            </article>

            {related_section}

            <a href="/" class="back-btn">← Retour aux articles</a>
        </main>

        <footer>
            <p>&copy; 2025 CyberInsight - Hack The Planet</p>
        </footer>
    </div>

    <script>
        // MATRIX RAIN EFFECT
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const characters = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const fontSize = 16;
        const columns = canvas.width / fontSize;
        const drops = [];

        for (let i = 0; i < columns; i++) {{
            drops[i] = Math.random() * canvas.height / fontSize;
        }}

        function drawMatrix() {{
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#00ff00';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {{
                const text = characters[Math.floor(Math.random() * characters.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);

                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                    drops[i] = 0;
                }}

                drops[i]++;
            }}
        }}

        setInterval(drawMatrix, 33);

        window.addEventListener('resize', () => {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }});
    </script>
</body>
</html>""".format(
        title=article['title'],
        category=article['category'],
        date=article['date'],
        reading_time=article['reading_time'],
        tags_html=tags_html,
        content=article['content'],
        related_section=f'<div class="related-section"><h3>> Articles liés</h3>{related_html}</div>' if related_html else ''
    )
    
    return html

def generate_index_page(articles):
    """Génère la page d'accueil avec style MATRIX"""
    total_articles = len(articles)
    all_categories = sorted(set(a['category'] for a in articles))
    total_reading_time = sum(a['reading_time'] for a in articles)
    
    articles_html = ""
    for article in articles:
        tags_html = " ".join([f'<span class="tag">#{tag}</span>' for tag in article['tags'][:3]])
        
        articles_html += f"""
        <article class="article-card">
            <div class="card-header">
                <span class="terminal-prompt">root@cyberinsight:~#</span>
                <span class="category-tag">{article['category']}</span>
            </div>
            <h2><a href="/articles/{article['slug']}.html">{article['title']}</a></h2>
            <p class="excerpt">{article['excerpt']}</p>
            <div class="card-meta">
                <span>📅 {article['date']}</span>
                <span>⏱ {article['reading_time']} min</span>
            </div>
            <div class="tags">{tags_html}</div>
        </article>
        """
    
    category_filters = '<button class="filter-btn active" data-category="all">[ ALL ]</button>'
    for cat in all_categories:
        category_filters += f'<button class="filter-btn" data-category="{cat}">[ {cat.upper()} ]</button>'
    
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberInsight - Hacking The Matrix</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Courier New', monospace;
            background: #000000;
            color: #00ff00;
            overflow-x: hidden;
        }}

        /* MATRIX RAIN BACKGROUND */
        #matrix-canvas {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.15;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            position: relative;
            z-index: 1;
        }}

        /* HEADER */
        header {{
            border-bottom: 2px solid #00ff00;
            padding: 2rem 0;
            text-align: center;
            margin-bottom: 3rem;
        }}

        .logo {{
            font-size: 3rem;
            color: #00ff00;
            font-weight: bold;
            text-shadow: 0 0 30px #00ff00, 0 0 60px #00ff00;
            animation: flicker 3s infinite alternate;
            display: block;
            margin-bottom: 1rem;
        }}

        @keyframes flicker {{
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{
                text-shadow: 0 0 30px #00ff00, 0 0 60px #00ff00;
                opacity: 1;
            }}
            20%, 24%, 55% {{
                text-shadow: 0 0 10px #00ff00;
                opacity: 0.8;
            }}
        }}

        .tagline {{
            color: #00aa00;
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }}

        .ascii-art {{
            color: #00ff00;
            font-size: 0.7rem;
            margin: 1rem 0;
            white-space: pre;
            line-height: 1;
        }}

        /* STATS */
        .stats {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            padding: 2rem 0;
            border-bottom: 1px solid #00aa00;
            margin-bottom: 3rem;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 2rem;
            color: #00ff00;
            text-shadow: 0 0 20px #00ff00;
            display: block;
        }}

        .stat-label {{
            color: #00aa00;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}

        /* FILTERS */
        .filters {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 2rem;
            justify-content: center;
        }}

        .filter-btn {{
            background: transparent;
            border: 1px solid #00aa00;
            color: #00aa00;
            padding: 0.5rem 1rem;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
        }}

        .filter-btn:hover {{
            border-color: #00ff00;
            color: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }}

        .filter-btn.active {{
            background: #00ff00;
            color: #000;
            border-color: #00ff00;
            box-shadow: 0 0 20px #00ff00;
        }}

        /* SEARCH */
        .search-box {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto 3rem auto;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #00ff00;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 1rem;
            text-align: center;
        }}

        .search-box:focus {{
            outline: none;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }}

        .search-box::placeholder {{
            color: #00aa00;
        }}

        /* ARTICLES GRID */
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }}

        .article-card {{
            border: 1px solid #00aa00;
            padding: 1.5rem;
            background: rgba(0, 255, 0, 0.02);
            transition: all 0.3s;
        }}

        .article-card:hover {{
            border-color: #00ff00;
            background: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 25px rgba(0, 255, 0, 0.3);
            transform: translateY(-5px);
        }}

        .article-card.hidden {{
            display: none;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}

        .terminal-prompt {{
            color: #00ff00;
            font-weight: bold;
        }}

        .category-tag {{
            background: #00ff00;
            color: #000;
            padding: 0.3rem 0.8rem;
            font-weight: bold;
            font-size: 0.85rem;
        }}

        .article-card h2 {{
            margin: 1rem 0;
            font-size: 1.4rem;
        }}

        .article-card h2 a {{
            color: #00ff00;
            text-decoration: none;
            text-shadow: 0 0 10px #00ff00;
        }}

        .article-card h2 a:hover {{
            color: #00ff88;
            text-shadow: 0 0 20px #00ff88;
        }}

        .excerpt {{
            color: #00cc00;
            margin: 1rem 0;
            line-height: 1.6;
        }}

        .card-meta {{
            display: flex;
            gap: 1.5rem;
            color: #00aa00;
            font-size: 0.9rem;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #00aa00;
        }}

        .tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.5rem;
        }}

        .tag {{
            color: #00aa00;
            border: 1px solid #00aa00;
            padding: 0.2rem 0.5rem;
            font-size: 0.75rem;
        }}

        /* NO RESULTS */
        .no-results {{
            text-align: center;
            padding: 4rem;
            color: #00aa00;
            display: none;
        }}

        /* FOOTER */
        footer {{
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 2px solid #00ff00;
            text-align: center;
            color: #00aa00;
        }}

        footer a {{
            color: #00ff00;
            text-decoration: none;
        }}

        footer a:hover {{
            text-shadow: 0 0 10px #00ff00;
        }}

        /* SCROLLBAR */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: #000;
        }}

        ::-webkit-scrollbar-thumb {{
            background: #00ff00;
            box-shadow: 0 0 10px #00ff00;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #00ff88;
        }}

        @media (max-width: 768px) {{
            .logo {{
                font-size: 2rem;
            }}

            .stats {{
                flex-direction: column;
                gap: 1rem;
            }}

            .articles-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>

    <div class="container">
        <header>
            <div class="ascii-art">
   ____      __               ____           _       __    __ 
  / ___\\_  _/ /  ___  ___    /  _/___  ___ (_)___ _/ /  _/ /_
 / /__/ / / / _ \\/ -_)/ __/   _/ // _ \\(_-</ // _ `/ _ \\/ __/
 \\___/\\_\\_,_/_.__/\\__//_/    /___//_//_/___/_/ \\_, /_//_/\\__/ 
                                              /___/            
            </div>
            <h1 class="logo">CyberInsight</h1>
            <p class="tagline">> Hack The Planet | Pentest | CTF | OSINT</p>
        </header>

        <div class="stats">
            <div class="stat">
                <span class="stat-value">{total_articles}</span>
                <span class="stat-label">ARTICLES</span>
            </div>
            <div class="stat">
                <span class="stat-value">{total_categories}</span>
                <span class="stat-label">CATEGORIES</span>
            </div>
            <div class="stat">
                <span class="stat-value">{total_reading_time}</span>
                <span class="stat-label">MIN READ</span>
            </div>
        </div>

        <input type="text" id="searchInput" class="search-box" placeholder="> root@search:~# _">

        <div class="filters">
            {category_filters}
        </div>

        <div class="articles-grid" id="articlesGrid">
            {articles_html}
        </div>

        <div class="no-results" id="noResults">
            <p>> ERROR: No articles found</p>
            <p>> Try different search terms</p>
        </div>

        <footer>
            <p>&copy; 2025 CyberInsight - <a href="https://github.com/voidsponge" target="_blank">GitHub</a></p>
            <p style="margin-top: 0.5rem; font-size: 0.85rem;">> "In the matrix, there is no spoon"</p>
        </footer>
    </div>

    <script>
        // MATRIX RAIN EFFECT
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const characters = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const fontSize = 16;
        const columns = canvas.width / fontSize;
        const drops = [];

        for (let i = 0; i < columns; i++) {{
            drops[i] = Math.random() * canvas.height / fontSize;
        }}

        function drawMatrix() {{
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#00ff00';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {{
                const text = characters[Math.floor(Math.random() * characters.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);

                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                    drops[i] = 0;
                }}

                drops[i]++;
            }}
        }}

        setInterval(drawMatrix, 33);

        window.addEventListener('resize', () => {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }});

        // SEARCH & FILTERS
        const searchInput = document.getElementById('searchInput');
        const articlesGrid = document.getElementById('articlesGrid');
        const noResults = document.getElementById('noResults');
        const articleCards = articlesGrid.querySelectorAll('.article-card');

        searchInput.addEventListener('input', function() {{
            const searchTerm = this.value.toLowerCase();
            let visibleCount = 0;

            articleCards.forEach(function(card) {{
                const title = card.querySelector('h2').textContent.toLowerCase();
                const excerpt = card.querySelector('.excerpt').textContent.toLowerCase();
                const category = card.querySelector('.category-tag').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || excerpt.includes(searchTerm) || category.includes(searchTerm)) {{
                    card.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    card.classList.add('hidden');
                }}
            }});

            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }});

        // CATEGORY FILTERS
        const filterButtons = document.querySelectorAll('.filter-btn');
        
        filterButtons.forEach(function(button) {{
            button.addEventListener('click', function() {{
                filterButtons.forEach(function(btn) {{
                    btn.classList.remove('active');
                }});
                this.classList.add('active');

                const category = this.getAttribute('data-category');
                let visibleCount = 0;

                articleCards.forEach(function(card) {{
                    const cardCategory = card.querySelector('.category-tag').textContent;
                    
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
    </script>
</body>
</html>""".format(
        total_articles=total_articles,
        total_categories=len(all_categories),
        total_reading_time=total_reading_time,
        category_filters=category_filters,
        articles_html=articles_html
    )
    
    return html

def generate_rss_feed(articles):
    """Génère le flux RSS"""
    rss = Element('rss', version='2.0')
    channel = SubElement(rss, 'channel')
    
    SubElement(channel, 'title').text = 'CyberInsight'
    SubElement(channel, 'link').text = 'https://voidsponge.github.io'
    SubElement(channel, 'description').text = 'Blog de cybersécurité : Pentest, CTF, OSINT'
    SubElement(channel, 'language').text = 'fr'
    
    for article in articles[:20]:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = article['title']
        SubElement(item, 'link').text = f"https://voidsponge.github.io/articles/{article['slug']}.html"
        SubElement(item, 'description').text = article['excerpt']
        SubElement(item, 'pubDate').text = article['date']
        SubElement(item, 'category').text = article['category']
    
    xml_string = minidom.parseString(tostring(rss)).toprettyxml(indent="  ")
    return xml_string

def main():
    """Fonction principale"""
    print("🚀 Génération du blog CyberInsight MATRIX...")
    
    # Créer dossiers
    OUTPUT_DIR.mkdir(exist_ok=True)
    ARTICLES_OUTPUT.mkdir(exist_ok=True)
    
    # Charger articles
    articles = []
    for filepath in sorted(ARTICLES_DIR.glob("*.md")):
        print(f"  📄 Traitement de {filepath.name}...")
        article = load_article(filepath)
        articles.append(article)
    
    # Trier par date (décroissant)
    articles.sort(key=lambda x: x['date'], reverse=True)
    
    print(f"  ✅ {len(articles)} article(s) traité(s)")
    
    # Générer pages articles
    for article in articles:
        article_html = generate_article_page(article, articles)
        output_path = ARTICLES_OUTPUT / f"{article['slug']}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(article_html)
    
    # Générer RSS
    print("  📡 Génération du flux RSS...")
    rss_content = generate_rss_feed(articles)
    with open(OUTPUT_DIR / "rss.xml", 'w', encoding='utf-8') as f:
        f.write(rss_content)
    
    # Générer page d'accueil
    print("  🏠 Génération de la page d'accueil...")
    index_html = generate_index_page(articles)
    with open(OUTPUT_DIR / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print("✨ Blog MATRIX généré avec succès !")
    print(f"💀 Style: HARDCORE HACKER")
    print(f"📊 {len(articles)} articles | Matrix Rain Background")

if __name__ == "__main__":
    main()