#!/usr/bin/env python3
"""
Générateur de blog CyberInsight - Style MODERNE CYBERSEC
Design élégant avec Matrix subtile en background
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
    """Génère la page HTML d'un article"""
    related_articles = get_related_articles(article, all_articles)
    
    related_html = ""
    for related in related_articles:
        related_html += f"""
        <article class="related-card">
            <h4><a href="/articles/{related['slug']}.html">{related['title']}</a></h4>
            <div class="related-meta">
                <span class="category-badge">{related['category']}</span>
                <span>⏱ {related['reading_time']} min</span>
            </div>
        </article>
        """
    
    tags_html = ""
    for tag in article['tags']:
        tags_html += f'<span class="tag">#{tag}</span>'
    
    html = """<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CyberInsight</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root[data-theme="dark"] {{
            --bg-primary: #0a0e1a;
            --bg-secondary: #131824;
            --bg-tertiary: #1a1f2e;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent: #06d6a0;
            --accent-dark: #048a6b;
            --border: #1e293b;
            --shadow: rgba(0, 0, 0, 0.3);
        }}

        :root[data-theme="light"] {{
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --accent: #06d6a0;
            --accent-dark: #048a6b;
            --border: #e2e8f0;
            --shadow: rgba(0, 0, 0, 0.1);
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.7;
            overflow-x: hidden;
            transition: background 0.3s ease, color 0.3s ease;
        }}

        /* MATRIX BACKGROUND SUBTIL */
        #matrix-canvas {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.03;
            pointer-events: none;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            position: relative;
            z-index: 1;
        }}

        /* HEADER */
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 2rem 0 3rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 3rem;
        }}

        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .logo::before {{
            content: '▸';
            color: var(--accent);
            font-size: 1.8rem;
        }}

        nav {{
            display: flex;
            gap: 2rem;
            align-items: center;
        }}

        nav a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }}

        nav a:hover {{
            color: var(--accent);
        }}

        .theme-toggle {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.3s;
        }}

        .theme-toggle:hover {{
            border-color: var(--accent);
            transform: rotate(180deg);
        }}

        /* ARTICLE HEADER */
        .article-header {{
            margin-bottom: 3rem;
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--text-primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .article-meta {{
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 1rem;
        }}

        .category-badge {{
            background: var(--accent);
            color: var(--bg-primary);
            padding: 0.4rem 0.9rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
        }}

        .tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .tag {{
            color: var(--accent);
            background: var(--bg-secondary);
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            border: 1px solid var(--border);
        }}

        /* CONTENT */
        .article-content {{
            margin: 3rem 0;
            font-size: 1.05rem;
        }}

        .article-content h2 {{
            font-size: 2rem;
            margin: 3rem 0 1.5rem 0;
            color: var(--text-primary);
            font-weight: 700;
        }}

        .article-content h3 {{
            font-size: 1.5rem;
            margin: 2rem 0 1rem 0;
            color: var(--text-primary);
            font-weight: 600;
        }}

        .article-content p {{
            margin: 1.5rem 0;
            color: var(--text-secondary);
        }}

        .article-content code {{
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg-secondary);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9em;
            color: var(--accent);
            border: 1px solid var(--border);
        }}

        .article-content pre {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            overflow-x: auto;
            margin: 2rem 0;
        }}

        .article-content pre code {{
            background: none;
            border: none;
            padding: 0;
            color: var(--text-primary);
        }}

        .article-content ul, .article-content ol {{
            margin: 1.5rem 0;
            padding-left: 2rem;
            color: var(--text-secondary);
        }}

        .article-content li {{
            margin: 0.5rem 0;
        }}

        .article-content a {{
            color: var(--accent);
            text-decoration: none;
            border-bottom: 1px solid var(--accent);
        }}

        .article-content a:hover {{
            color: var(--accent-dark);
            border-bottom-color: var(--accent-dark);
        }}

        .article-content blockquote {{
            border-left: 3px solid var(--accent);
            padding-left: 1.5rem;
            margin: 2rem 0;
            color: var(--text-muted);
            font-style: italic;
        }}

        /* RELATED ARTICLES */
        .related-section {{
            margin-top: 4rem;
            padding-top: 3rem;
            border-top: 1px solid var(--border);
        }}

        .related-section h3 {{
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }}

        .related-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s;
        }}

        .related-card:hover {{
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px var(--shadow);
        }}

        .related-card h4 {{
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }}

        .related-card h4 a {{
            color: var(--text-primary);
            text-decoration: none;
        }}

        .related-card h4 a:hover {{
            color: var(--accent);
        }}

        .related-meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }}

        /* BACK BUTTON */
        .back-btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 3rem;
            padding: 0.8rem 1.5rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
        }}

        .back-btn:hover {{
            border-color: var(--accent);
            background: var(--bg-tertiary);
        }}

        footer {{
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        /* RESPONSIVE */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            h1 {{
                font-size: 2rem;
            }}

            header {{
                flex-direction: column;
                gap: 1rem;
                align-items: flex-start;
            }}

            nav {{
                width: 100%;
                justify-content: space-between;
            }}
        }}

        /* SCROLLBAR */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--accent);
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-dark);
        }}
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>

    <div class="container">
        <header>
            <a href="/" class="logo">CyberInsight</a>
            <nav>
                <a href="/">Articles</a>
                <a href="https://github.com/voidsponge" target="_blank">GitHub</a>
                <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                    <span id="themeIcon">🌙</span>
                </button>
            </nav>
        </header>

        <main>
            <div class="article-header">
                <h1>{title}</h1>
                <div class="article-meta">
                    <span class="category-badge">{category}</span>
                    <span>📅 {date}</span>
                    <span>⏱ {reading_time} min de lecture</span>
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
            <p>&copy; 2025 CyberInsight - Blog de cybersécurité</p>
        </footer>
    </div>

    <script>
        // MATRIX BACKGROUND SUBTIL
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const characters = '01';
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = [];

        for (let i = 0; i < columns; i++) {{
            drops[i] = Math.random() * canvas.height / fontSize;
        }}

        function drawMatrix() {{
            ctx.fillStyle = 'rgba(10, 14, 26, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#06d6a0';
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

        setInterval(drawMatrix, 50);

        window.addEventListener('resize', () => {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }});

        // THEME TOGGLE
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const html = document.documentElement;

        const savedTheme = localStorage.getItem('theme') || 'dark';
        html.setAttribute('data-theme', savedTheme);
        themeIcon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';

        themeToggle.addEventListener('click', () => {{
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeIcon.textContent = newTheme === 'dark' ? '🌙' : '☀️';
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
        related_section=f'<div class="related-section"><h3>Articles liés</h3>{related_html}</div>' if related_html else ''
    )
    
    return html

def generate_index_page(articles):
    """Génère la page d'accueil moderne"""
    total_articles = len(articles)
    all_categories = sorted(set(a['category'] for a in articles))
    total_reading_time = sum(a['reading_time'] for a in articles)
    
    # Featured article (premier)
    featured = articles[0] if articles else None
    featured_html = ""
    if featured:
        featured_tags = " ".join([f'<span class="tag">#{tag}</span>' for tag in featured['tags'][:3]])
        featured_html = f"""
        <div class="featured-article">
            <span class="featured-badge">⭐ À la une</span>
            <h2><a href="/articles/{featured['slug']}.html">{featured['title']}</a></h2>
            <p>{featured['excerpt']}</p>
            <div class="featured-meta">
                <span class="category-badge">{featured['category']}</span>
                <span>📅 {featured['date']}</span>
                <span>⏱ {featured['reading_time']} min</span>
            </div>
            <div class="tags">{featured_tags}</div>
        </div>
        """
    
    # Articles grid
    articles_html = ""
    for article in articles[1:]:  # Skip featured
        tags_html = " ".join([f'<span class="tag">#{tag}</span>' for tag in article['tags'][:3]])
        
        articles_html += f"""
        <article class="article-card">
            <div class="card-header">
                <span class="category-badge">{article['category']}</span>
                <span class="date">{article['date']}</span>
            </div>
            <h3><a href="/articles/{article['slug']}.html">{article['title']}</a></h3>
            <p class="excerpt">{article['excerpt']}</p>
            <div class="card-footer">
                <div class="tags">{tags_html}</div>
                <span class="reading-time">⏱ {article['reading_time']} min</span>
            </div>
        </article>
        """
    
    # Category filters
    category_filters = '<button class="filter-btn active" data-category="all">Tous</button>'
    for cat in all_categories:
        category_filters += f'<button class="filter-btn" data-category="{cat}">{cat}</button>'
    
    html_template = """<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberInsight - Blog de Cybersécurité</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root[data-theme="dark"] {{
            --bg-primary: #0a0e1a;
            --bg-secondary: #131824;
            --bg-tertiary: #1a1f2e;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent: #06d6a0;
            --accent-dark: #048a6b;
            --border: #1e293b;
            --shadow: rgba(0, 0, 0, 0.3);
        }}

        :root[data-theme="light"] {{
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --accent: #06d6a0;
            --accent-dark: #048a6b;
            --border: #e2e8f0;
            --shadow: rgba(0, 0, 0, 0.1);
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
            transition: background 0.3s ease, color 0.3s ease;
        }}

        /* MATRIX BACKGROUND SUBTIL */
        #matrix-canvas {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.03;
            pointer-events: none;
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
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 2rem 0;
            margin-bottom: 3rem;
        }}

        .logo {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .logo::before {{
            content: '▸';
            color: var(--accent);
            font-size: 2.5rem;
        }}

        nav {{
            display: flex;
            gap: 2rem;
            align-items: center;
        }}

        nav a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }}

        nav a:hover {{
            color: var(--accent);
        }}

        .theme-toggle {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s;
        }}

        .theme-toggle:hover {{
            border-color: var(--accent);
            transform: rotate(180deg);
        }}

        /* HERO */
        .hero {{
            text-align: center;
            padding: 4rem 0;
            margin-bottom: 3rem;
        }}

        .hero h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--text-primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero p {{
            font-size: 1.3rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
        }}

        /* STATS */
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            margin-bottom: 4rem;
        }}

        .stat-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s;
        }}

        .stat-card:hover {{
            border-color: var(--accent);
            transform: translateY(-5px);
            box-shadow: 0 8px 20px var(--shadow);
        }}

        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent);
            display: block;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 0.5rem;
        }}

        /* FEATURED ARTICLE */
        .featured-article {{
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 3rem;
            margin-bottom: 4rem;
            position: relative;
            overflow: hidden;
        }}

        .featured-article::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent), var(--accent-dark));
        }}

        .featured-badge {{
            background: var(--accent);
            color: var(--bg-primary);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            display: inline-block;
            margin-bottom: 1.5rem;
        }}

        .featured-article h2 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}

        .featured-article h2 a {{
            color: var(--text-primary);
            text-decoration: none;
        }}

        .featured-article h2 a:hover {{
            color: var(--accent);
        }}

        .featured-article p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            line-height: 1.7;
        }}

        .featured-meta {{
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }}

        /* FILTERS */
        .filters {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 3rem;
        }}

        .filter-btn {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 0.7rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            transition: all 0.3s;
        }}

        .filter-btn:hover {{
            border-color: var(--accent);
            color: var(--accent);
        }}

        .filter-btn.active {{
            background: var(--accent);
            color: var(--bg-primary);
            border-color: var(--accent);
        }}

        /* SEARCH */
        .search-box {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto 3rem auto;
            padding: 1rem 1.5rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            transition: all 0.3s;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(6, 214, 160, 0.1);
        }}

        .search-box::placeholder {{
            color: var(--text-muted);
        }}

        /* ARTICLES GRID */
        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 4rem;
        }}

        .article-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2rem;
            transition: all 0.3s;
        }}

        .article-card:hover {{
            border-color: var(--accent);
            transform: translateY(-5px);
            box-shadow: 0 8px 20px var(--shadow);
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

        .category-badge {{
            background: var(--accent);
            color: var(--bg-primary);
            padding: 0.4rem 0.9rem;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
        }}

        .date {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .article-card h3 {{
            font-size: 1.4rem;
            margin: 1rem 0;
            line-height: 1.3;
        }}

        .article-card h3 a {{
            color: var(--text-primary);
            text-decoration: none;
        }}

        .article-card h3 a:hover {{
            color: var(--accent);
        }}

        .excerpt {{
            color: var(--text-secondary);
            margin: 1rem 0;
            line-height: 1.6;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}

        .tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .tag {{
            color: var(--accent);
            background: var(--bg-tertiary);
            padding: 0.3rem 0.7rem;
            border-radius: 6px;
            font-size: 0.8rem;
            border: 1px solid var(--border);
        }}

        .reading-time {{
            color: var(--text-muted);
            font-size: 0.9rem;
            white-space: nowrap;
        }}

        /* NO RESULTS */
        .no-results {{
            text-align: center;
            padding: 4rem;
            color: var(--text-muted);
            display: none;
        }}

        footer {{
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
        }}

        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}

        /* RESPONSIVE */
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2.5rem;
            }}

            .stats {{
                grid-template-columns: 1fr;
            }}

            .articles-grid {{
                grid-template-columns: 1fr;
            }}

            header {{
                flex-direction: column;
                gap: 1.5rem;
                align-items: flex-start;
            }}

            nav {{
                width: 100%;
                justify-content: space-between;
            }}

            .featured-article {{
                padding: 2rem;
            }}

            .featured-article h2 {{
                font-size: 1.8rem;
            }}
        }}

        /* SCROLLBAR */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--accent);
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-dark);
        }}
    </style>
</head>
<body>
    <canvas id="matrix-canvas"></canvas>

    <div class="container">
        <header>
            <a href="/" class="logo">CyberInsight</a>
            <nav>
                <a href="#articles">Articles</a>
                <a href="https://github.com/voidsponge" target="_blank">GitHub</a>
                <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                    <span id="themeIcon">🌙</span>
                </button>
            </nav>
        </header>

        <section class="hero">
            <h1>CyberInsight</h1>
            <p>Explorez le monde de la cybersécurité : Pentest, CTF, OSINT et plus encore</p>
        </section>

        <div class="stats">
            <div class="stat-card">
                <span class="stat-value">{total_articles}</span>
                <span class="stat-label">Articles</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{total_categories}</span>
                <span class="stat-label">Catégories</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{total_reading_time}</span>
                <span class="stat-label">Minutes de lecture</span>
            </div>
        </div>

        {featured_html}

        <input type="text" id="searchInput" class="search-box" placeholder="🔍 Rechercher un article...">

        <div class="filters" id="filters">
            {category_filters}
        </div>

        <div class="articles-grid" id="articlesGrid">
            {articles_html}
        </div>

        <div class="no-results" id="noResults">
            <p>Aucun article trouvé</p>
        </div>

        <footer>
            <p>&copy; 2025 CyberInsight - <a href="https://github.com/voidsponge" target="_blank">GitHub</a></p>
        </footer>
    </div>

    <script>
        // MATRIX BACKGROUND SUBTIL (juste des 0 et 1)
        const canvas = document.getElementById('matrix-canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const characters = '01';
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = [];

        for (let i = 0; i < columns; i++) {{
            drops[i] = Math.random() * canvas.height / fontSize;
        }}

        function drawMatrix() {{
            ctx.fillStyle = 'rgba(10, 14, 26, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#06d6a0';
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

        setInterval(drawMatrix, 50);

        window.addEventListener('resize', () => {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }});

        // THEME TOGGLE
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const html = document.documentElement;

        const savedTheme = localStorage.getItem('theme') || 'dark';
        html.setAttribute('data-theme', savedTheme);
        themeIcon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';

        themeToggle.addEventListener('click', () => {{
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeIcon.textContent = newTheme === 'dark' ? '🌙' : '☀️';
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
                const title = card.querySelector('h3').textContent.toLowerCase();
                const excerpt = card.querySelector('.excerpt').textContent.toLowerCase();
                const category = card.querySelector('.category-badge').textContent.toLowerCase();
                
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
                    const cardCategory = card.querySelector('.category-badge').textContent;
                    
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
</html>"""
    
    html = html_template.format(
        total_articles=total_articles,
        total_categories=len(all_categories),
        total_reading_time=total_reading_time,
        featured_html=featured_html,
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
    print("🚀 Génération du blog CyberInsight MODERNE...")
    
    # Créer dossiers
    OUTPUT_DIR.mkdir(exist_ok=True)
    ARTICLES_OUTPUT.mkdir(exist_ok=True)
    
    # Charger articles
    articles = []
    for filepath in sorted(ARTICLES_DIR.glob("*.md")):
        if filepath.name == '_template.md':
            continue
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
    
    print("✨ Blog MODERNE généré avec succès !")
    print(f"🎨 Style: Clean & Élégant + Matrix subtile")
    print(f"📊 {len(articles)} articles")

if __name__ == "__main__":
    main()