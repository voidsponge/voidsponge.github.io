# 🔐 CyberInsight - Blog de Cybersécurité

Un blog statique moderne et élégant sur la cybersécurité, généré automatiquement avec GitHub Pages.

## ✨ Fonctionnalités

- 🎨 Design moderne avec esthétique "cyber" (thème sombre, néons)
- 📝 Articles en Markdown avec coloration syntaxique
- 🚀 Génération automatique via GitHub Actions
- 📱 Responsive design
- ⚡ Performance optimale (site statique)
- 🔄 Mise à jour automatique à chaque commit

## 🚀 Installation rapide

### 1. Créer votre repository GitHub

```bash
# Créez un nouveau repository nommé : votre-nom.github.io
# Exemple : johnsmith.github.io
```

### 2. Cloner ce template

```bash
git clone https://github.com/VOTRE-NOM/votre-nom.github.io.git
cd votre-nom.github.io
```

### 3. Activer GitHub Pages

1. Allez dans **Settings** > **Pages**
2. Source : **GitHub Actions**
3. Sauvegardez

### 4. Pousser votre premier commit

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

✅ Votre blog sera accessible à : `https://votre-nom.github.io`

## 📝 Ajouter un nouvel article

### Méthode 1 : Via l'interface GitHub (plus simple)

1. Allez dans le dossier `_articles/` sur GitHub
2. Cliquez sur **Add file** > **Create new file**
3. Nommez votre fichier : `mon-article.md`
4. Copiez-collez le template ci-dessous
5. Commit → Le blog se régénère automatiquement ! 🎉

### Méthode 2 : En local

```bash
# Créer un nouvel article
cd _articles/
cp _template.md mon-nouvel-article.md

# Éditer l'article
nano mon-nouvel-article.md

# Commit et push
git add _articles/mon-nouvel-article.md
git commit -m "Ajout: Mon nouvel article"
git push origin main
```

## 📄 Template d'article

Créez un fichier `.md` dans `_articles/` avec ce format :

```markdown
---
title: "Titre de votre article"
date: 2025-12-02
category: Web Security
author: Votre Nom
excerpt: "Un résumé court qui apparaîtra sur la page d'accueil"
---

# Titre de votre article

## Introduction

Votre contenu ici...

### Code

\`\`\`python
def exploit():
    print("Hello World")
\`\`\`

### Commandes shell

\`\`\`bash
nmap -sV target.com
\`\`\`

## Tableaux

| Colonne 1 | Colonne 2 |
|-----------|-----------|
| Donnée 1  | Donnée 2  |

## Conclusion

Votre conclusion...

**Tags:** #pentest #web #security
```

## 🎨 Catégories disponibles

- `Web Security`
- `Malware`
- `Network`
- `CTF Writeup`
- `OSINT`
- `IoT`
- `Phishing`
- `Pentest`
- `Red Team`
- `Blue Team`

## 📁 Structure du projet

```
votre-repo/
├── .github/
│   └── workflows/
│       └── build.yml          # Workflow GitHub Actions
├── _articles/                  # 📝 VOS ARTICLES ICI
│   ├── _template.md           # Template pour nouveaux articles
│   ├── article-1.md
│   └── article-2.md
├── _site/                      # Généré automatiquement (ne pas modifier)
│   ├── index.html
│   └── articles/
├── generate.py                 # Script de génération
└── README.md
```

## 🛠️ Comment ça marche ?

1. Vous ajoutez/modifiez un article `.md` dans `_articles/`
2. Vous faites un `git push`
3. GitHub Actions détecte le changement
4. Le script `generate.py` :
   - Lit tous les articles markdown
   - Convertit en HTML
   - Génère les pages avec le design
5. Le site est publié sur GitHub Pages

## 🎯 Workflow

```
Écrire article     Push Git      GitHub Actions    Site publié
    .md         →     🚀      →      ⚙️         →      🌐
   (_articles/)                   (generate.py)    (username.github.io)
```

## 🔧 Personnalisation

### Changer le titre du blog

Éditez `generate.py` ligne ~600 :

```python
<div class="logo">VotreNom</div>  # Changez "CyberInsight"
```

### Changer les couleurs

Éditez les variables CSS dans `generate.py` :

```css
:root {
    --color-primary: #00f5a0;    /* Vert néon */
    --color-secondary: #00d9ff;  /* Cyan */
    --color-accent: #ff006e;     /* Rose */
}
```

### Ajouter un lien GitHub dans le header

Éditez `generate.py` ligne ~650 :

```html
<a href="https://github.com/VOTRE-USERNAME/VOTRE-REPO" target="_blank">GitHub</a>
```

## 📊 Statistiques

Le blog génère automatiquement :
- ⭐ Un article "en vedette" (le plus récent)
- 📅 Tri chronologique des articles
- 🏷️ Badges de catégories
- 🔗 Navigation automatique

## 🐛 Dépannage

### Le site ne se met pas à jour ?

1. Vérifiez que GitHub Actions est activé (Settings > Actions > Allow all actions)
2. Vérifiez les logs dans l'onglet **Actions**
3. Assurez-vous que le workflow a les permissions (Settings > Actions > General > Workflow permissions > Read and write)

### Les articles n'apparaissent pas ?

1. Vérifiez que le fichier est bien dans `_articles/`
2. Vérifiez que le fichier se termine par `.md`
3. Vérifiez que le frontmatter (les `---`) est correct
4. Les fichiers commençant par `_` sont ignorés (comme `_template.md`)

### Erreur "markdown module not found" ?

C'est normal, GitHub Actions l'installe automatiquement. Si vous testez en local :

```bash
pip install markdown
python generate.py
```

## 📚 Ressources

- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🤝 Contribution

Pour améliorer ce template :

1. Fork le repo
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements
4. Push et créez une Pull Request

## 📝 License

MIT License - Utilisez librement pour vos projets !

## 💡 Idées d'articles

- Write-ups de CTF
- Analyses de malware
- Tutoriels de pentest
- Découvertes de CVE
- Guides d'outils
- Configurations sécurisées
- Retours d'expérience Bug Bounty

---

**Créé avec ❤️ pour la communauté cybersécurité**

🔗 [Voir un exemple](https://votre-nom.github.io)
