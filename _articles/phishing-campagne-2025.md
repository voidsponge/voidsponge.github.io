---
title: "Analyse d'une campagne de phishing sophistiquée en 2025"
date: 2025-11-30
category: Phishing
author: CyberInsight Team
excerpt: "Découverte et analyse d'une nouvelle campagne de phishing ciblant les entreprises françaises avec des techniques d'ingénierie sociale avancées."
---

# Analyse d'une campagne de phishing sophistiquée en 2025

## Introduction

Au cours des dernières semaines, nous avons identifié une campagne de phishing particulièrement sophistiquée ciblant spécifiquement les entreprises françaises du secteur technologique. Cette campagne se distingue par l'utilisation de techniques d'ingénierie sociale avancées et d'infrastructures cloud compromises.

## Vecteur d'attaque initial

L'attaque débute par un email parfaitement rédigé en français, se faisant passer pour une notification de la plateforme Microsoft Teams. Les éléments qui rendent cette campagne particulièrement dangereuse :

- **Usurpation d'identité crédible** : Les emails proviennent de domaines légitimes compromis
- **Timing parfait** : Les messages arrivent pendant les heures de travail
- **Contenu personnalisé** : Utilisation d'informations OSINT sur les cibles

## Analyse technique

### Infrastructure utilisée

```
Domaine compromis: sharepoint-notifications[.]fr
IP C2: 185.xxx.xxx.xxx (Hébergement en Allemagne)
Framework: Evilginx2 modifié
```

### Chaîne d'infection

1. **Email de phishing** → Lien vers une page de phishing
2. **Page clone Microsoft** → Capture des identifiants + token MFA
3. **Redirection** → Site légitime Microsoft (pour éviter les soupçons)
4. **Accès au compte** → Exfiltration de données sensibles

## Indicateurs de compromission (IoC)

| Type | Valeur |
|------|--------|
| Domaine | sharepoint-notifications[.]fr |
| Hash MD5 | a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 |
| User-Agent | Mozilla/5.0 (compatible; PhishBot/2.0) |

## Recommandations

### Pour les utilisateurs

- ✅ Vérifiez toujours l'URL avant de saisir vos identifiants
- ✅ Activez l'authentification multi-facteurs (MFA) basée sur application
- ✅ Méfiez-vous des demandes urgentes

### Pour les équipes sécurité

```bash
# Bloquer le domaine avec iptables
iptables -A OUTPUT -d sharepoint-notifications.fr -j DROP

# Scanner votre infrastructure
grep "sharepoint-notifications.fr" /var/log/nginx/access.log
```

## Timeline de l'attaque

| Date | Événement |
|------|-----------|
| 15 Nov | Première détection de la campagne |
| 20 Nov | Identification de 50+ victimes |
| 25 Nov | Takedown du domaine principal |
| 28 Nov | Apparition de nouveaux domaines |

## Conclusion

Cette campagne illustre l'évolution constante des techniques de phishing. Les attaquants investissent désormais dans des infrastructures sophistiquées et utilisent l'OSINT pour personnaliser leurs attaques. La vigilance et la formation restent les meilleures défenses.

---

## Ressources complémentaires

- [CERT-FR - Alertes de sécurité](https://www.cert.ssi.gouv.fr/)
- [ANSSI - Guide phishing](https://www.ssi.gouv.fr/)
- [Evilginx2 Repository](https://github.com/kgretzky/evilginx2)

**Tags:** #phishing #security #entreprise #microsoft #mfa
