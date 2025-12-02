#!/usr/bin/env python3
"""
Générateur de blog statique pour CyberInsight
Lit tous les articles markdown du dossier _articles/ et génère le site dans _site/
"""

import os
import re
import markdown
from pathlib import Path
from datetime import datetime

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

def load_article(filepath):
    """Charge un article markdown et extrait les métadonnées"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, markdown_content = parse_frontmatter(content)
    
    # Extraire le titre du markdown si pas dans frontmatter
    if 'title' not in frontmatter:
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        if title_match:
            frontmatter['title'] = title_match.group(1)
    
    # Générer un slug depuis le nom de fichier
    slug = filepath.stem
    
    # Convertir le markdown en HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'fenced_code', 'tables', 'toc'])
    html_content = md.convert(markdown_content)
    
    # Extraire un excerpt des premiers 150 caractères
    plain_text = re.sub('<[^<]+?>', '', html_content)
    excerpt = plain_text[:200].strip() + '...' if len(plain_text) > 200 else plain_text
    
    return {
        'title': frontmatter.get('title', 'Sans titre'),
        'slug': slug,
        'category': frontmatter.get('category', 'Général'),
        'date': frontmatter.get('date', datetime.now().strftime('%Y-%m-%d')),
        'author': frontmatter.get('author', 'CyberInsight'),
        'excerpt': frontmatter.get('excerpt', excerpt),
        'content': html_content,
        'filepath': filepath
    }

def format_date(date_str):
    """Formate une date en français"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        months = {
            1: 'Jan', 2: 'Fév', 3: 'Mars', 4: 'Avr', 5: 'Mai', 6: 'Juin',
            7: 'Juil', 8: 'Août', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'
        }
        return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"
    except:
        return date_str

def generate_article_page(article):
    """Génère une page HTML pour un article"""
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - CyberInsight</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css">
    <style>
        :root {{
            --color-bg: #0a0e17;
            --color-surface: #151922;
            --color-surface-elevated: #1e232e;
            --color-primary: #00f5a0;
            --color-secondary: #00d9ff;
            --color-accent: #ff006e;
            --color-text: #e8ecf3;
            --color-text-muted: #8b92a8;
            --color-border: #2a3142;
            --font-display: 'JetBrains Mono', monospace;
            --font-body: 'Poppins', sans-serif;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: var(--font-body);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.8;
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
        }}

        .container {{
            max-width: 900px;
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
            background: rgba(10, 14, 23, 0.9);
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

        .back-link {{
            color: var(--color-text-muted);
            text-decoration: none;
            font-size: 0.95rem;
            transition: color 0.3s ease;
        }}

        .back-link:hover {{ color: var(--color-primary); }}

        article {{ padding: 4rem 0; }}

        .article-header {{ margin-bottom: 3rem; }}

        .article-meta {{
            display: flex;
            gap: 1rem;
            align-items: center;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            color: var(--color-text-muted);
            font-family: var(--font-display);
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

        .article-title {{
            font-size: 2.8rem;
            line-height: 1.2;
            margin-bottom: 1rem;
            font-weight: 700;
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

        footer {{
            border-top: 1px solid var(--color-border);
            padding: 2rem 0;
            margin-top: 4rem;
            text-align: center;
            color: var(--color-text-muted);
        }}

        @media (max-width: 768px) {{
            .article-title {{ font-size: 2rem; }}
            .article-content {{ font-size: 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <a href="../index.html" class="logo">CyberInsight</a>
                <a href="../index.html" class="back-link">← Retour</a>
            </div>
        </div>
    </header>

    <main>
        <div class="container">
            <article>
                <div class="article-header">
                    <div class="article-meta">
                        <span class="category-badge">{article['category']}</span>
                        <span>{format_date(article['date'])}</span>
                        <span>•</span>
                        <span>{article['author']}</span>
                    </div>
                    <h1 class="article-title">{article['title']}</h1>
                </div>
                
                <div class="article-content">
                    {article['content']}
                </div>
            </article>
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 CyberInsight. Tous droits réservés.</p>
        </div>
    </footer>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
</body>
</html>'''
    
    return html

def generate_index_page(articles):
    """Génère la page d'accueil"""
    
    # Trier par date (plus récent en premier)
    articles_sorted = sorted(articles, key=lambda x: x['date'], reverse=True)
    
    # Article en vedette (le plus récent)
    featured = articles_sorted[0] if articles_sorted else None
    
    # Générer les cartes d'articles
    articles_html = ''
    for article in articles_sorted:
        articles_html += f'''
        <article class="article-card">
            <div class="article-meta">
                <span class="article-category">{article['category']}</span>
                <span>•</span>
                <span>{format_date(article['date'])}</span>
            </div>
            <h3>{article['title']}</h3>
            <p class="article-excerpt">{article['excerpt']}</p>
            <a href="articles/{article['slug']}.html" class="read-more">Lire plus</a>
        </article>
        '''
    
    featured_html = ''
    if featured:
        featured_html = f'''
        <div class="featured-article">
            <span class="featured-label">⭐ Article en vedette</span>
            <h2>{featured['title']}</h2>
            <p>{featured['excerpt']}</p>
            <a href="articles/{featured['slug']}.html" class="read-more">Lire l'article complet</a>
        </div>
        '''
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberInsight - Blog de Cybersécurité</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --color-bg: #0a0e17;
            --color-surface: #151922;
            --color-surface-elevated: #1e232e;
            --color-primary: #00f5a0;
            --color-secondary: #00d9ff;
            --color-accent: #ff006e;
            --color-text: #e8ecf3;
            --color-text-muted: #8b92a8;
            --color-border: #2a3142;
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
            background: rgba(10, 14, 23, 0.8);
            animation: slideDown 0.6s ease-out;
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
        }}

        .article-category {{
            color: var(--color-primary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
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
            margin-bottom: 1.5rem;
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
            nav {{ gap: 1.5rem; }}
            .articles-grid {{ grid-template-columns: 1fr; }}
            .featured-article {{ padding: 2rem; }}
            .featured-article h2 {{ font-size: 1.8rem; }}
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
                </nav>
            </div>
        </div>
    </header>

    <main>
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

        <section class="articles-section">
            <div class="container">
                {featured_html}

                <h2 class="section-title" id="articles">Articles récents</h2>
                
                <div class="articles-grid">
                    {articles_html}
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 CyberInsight. Tous droits réservés.</p>
        </div>
    </footer>
</body>
</html>'''
    
    return html

def main():
    """Fonction principale"""
    print("🚀 Génération du blog CyberInsight...")
    
    # Créer les dossiers de sortie
    OUTPUT_DIR.mkdir(exist_ok=True)
    ARTICLES_OUTPUT.mkdir(exist_ok=True)
    
    # Charger tous les articles
    articles = []
    if ARTICLES_DIR.exists():
        for filepath in ARTICLES_DIR.glob("*.md"):
            if not filepath.name.startswith('_'):  # Ignorer les fichiers commençant par _
                print(f"  📄 Traitement de {filepath.name}...")
                article = load_article(filepath)
                articles.append(article)
                
                # Générer la page de l'article
                article_html = generate_article_page(article)
                output_path = ARTICLES_OUTPUT / f"{article['slug']}.html"
                output_path.write_text(article_html, encoding='utf-8')
    
    print(f"  ✅ {len(articles)} article(s) traité(s)")
    
    # Générer la page d'accueil
    print("  🏠 Génération de la page d'accueil...")
    index_html = generate_index_page(articles)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding='utf-8')
    
    print("✨ Blog généré avec succès dans le dossier _site/")

if __name__ == "__main__":
    main()
