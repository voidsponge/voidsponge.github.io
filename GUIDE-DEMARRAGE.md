# 🚀 Guide de Démarrage Rapide

## Étape 1 : Créer le repository GitHub

1. Allez sur https://github.com/new
2. Nommez votre repo : `votre-nom.github.io` (par exemple : `johnsmith.github.io`)
3. Cochez "Public"
4. Ne cochez PAS "Add README"
5. Cliquez sur "Create repository"

## Étape 2 : Uploader les fichiers

### Option A : Via l'interface GitHub (recommandé pour débutants)

1. Sur la page de votre nouveau repo, cliquez sur "uploading an existing file"
2. Glissez-déposez TOUS les fichiers/dossiers que vous avez téléchargés :
   - `.github/` (dossier)
   - `_articles/` (dossier)
   - `generate.py`
   - `README.md`
   - `.gitignore`
3. Écrivez un message de commit : "Initial commit"
4. Cliquez sur "Commit changes"

### Option B : Via Git (si vous connaissez Git)

```bash
cd chemin/vers/les/fichiers
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/VOTRE-NOM/votre-nom.github.io.git
git push -u origin main
```

## Étape 3 : Activer GitHub Pages

1. Allez dans **Settings** (paramètres) de votre repo
2. Dans le menu de gauche, cliquez sur **Pages**
3. Sous "Build and deployment"
4. **Source** : Sélectionnez "GitHub Actions"
5. C'est tout ! Pas besoin de cliquer sur "Save"

## Étape 4 : Activer les permissions

1. Toujours dans **Settings**
2. Dans le menu de gauche, cliquez sur **Actions** > **General**
3. Descendez jusqu'à "Workflow permissions"
4. Sélectionnez "Read and write permissions"
5. Cliquez sur "Save"

## Étape 5 : Vérifier le déploiement

1. Allez dans l'onglet **Actions** de votre repo
2. Vous devriez voir un workflow "Générer le Blog" en cours d'exécution (cercle jaune 🟡)
3. Attendez qu'il devienne vert ✅ (environ 1-2 minutes)
4. Votre site est en ligne ! 🎉

## Étape 6 : Visiter votre blog

Ouvrez votre navigateur et allez à :
```
https://votre-nom.github.io
```

## 📝 Ajouter votre premier article

### Via GitHub (le plus simple)

1. Sur votre repo GitHub, cliquez sur le dossier `_articles/`
2. Cliquez sur "Add file" > "Create new file"
3. Nommez le fichier : `mon-premier-article.md`
4. Copiez-collez ceci :

```markdown
---
title: "Mon premier article de cybersécurité"
date: 2025-12-02
category: Pentest
author: Votre Nom
excerpt: "Ceci est mon premier article sur mon nouveau blog de cybersécurité !"
---

# Mon premier article

## Introduction

Bienvenue sur mon blog de cybersécurité ! Je vais partager ici mes découvertes, write-ups et analyses.

## Pourquoi ce blog ?

- Partager mes connaissances
- Documenter mes apprentissages
- Contribuer à la communauté

## Prochains sujets

Je prévois d'écrire sur :
- Les write-ups de CTF
- L'analyse de malware
- Les techniques de pentest

## Conclusion

À bientôt pour de nouveaux articles !

**Tags:** #cybersecurity #blog #introduction
```

5. Cliquez sur "Commit changes"
6. Attendez 1-2 minutes
7. Rafraîchissez votre site → Votre article est en ligne ! 🎉

## ❓ Problèmes fréquents

### "Le site n'est pas accessible"
- Attendez 2-3 minutes après le premier commit
- Vérifiez que le workflow est vert dans l'onglet Actions
- Assurez-vous que le nom du repo est bien `votre-nom.github.io`

### "Workflow failed"
- Vérifiez les permissions dans Settings > Actions > General
- Assurez-vous que tous les fichiers ont été uploadés

### "Les articles n'apparaissent pas"
- Les fichiers doivent être dans `_articles/`
- Les fichiers doivent se terminer par `.md`
- Le frontmatter (les `---`) doit être correct

## 🎉 Félicitations !

Vous avez maintenant un blog de cybersécurité fonctionnel et automatisé !

Chaque fois que vous ajouterez un article `.md` dans `_articles/` et que vous ferez un commit, votre blog se mettra à jour automatiquement.

## 📚 Prochaines étapes

- Personnalisez le titre dans `generate.py`
- Ajoutez vos propres articles
- Partagez votre blog sur Twitter/LinkedIn
- Rejoignez la communauté cybersec !

**Besoin d'aide ?** Ouvrez une issue sur le repo GitHub !
