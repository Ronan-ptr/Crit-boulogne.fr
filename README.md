# 🎯 Crit Agency — Plateforme Web & Dashboard RH

Plateforme numérique de l'agence événementielle **Crit**, composée d'un site vitrine et d'un dashboard analytique sécurisé dédié à la gestion du personnel événementiel.

---

## 📌 Objectif

Fournir à l'agence Crit un outil simple et efficace permettant de :
- Présenter l'agence via un site web public
- Analyser les données du personnel ayant travaillé lors des événements via un dashboard privé

---

## 🏗️ Architecture du projet

```
crit-agency/
│
├── .gitignore                  # Fichiers exclus de Git
├── README.md                   # Documentation du projet
├── docker-compose.yml          # Orchestration des conteneurs (à venir)
│
├── website/                    # Site web public (HTML/CSS)
│   ├── index.html              # Page d'accueil de l'agence
│   ├── style.css               # Feuille de styles
│   └── assets/                 # Images, icônes, polices
│
└── dashboard/                  # Application analytique (Python/Streamlit)
    ├── Dockerfile              # Image Docker du dashboard
    ├── requirements.txt        # Dépendances Python
    ├── app.py                  # Application Streamlit principale
    └── data/                   # Fichiers CSV des événements (ignorés par Git)
        └── .gitkeep
```

---

## 🌐 Site Web — `website/`

Site vitrine public de l'agence Crit, accessible à tous.

**Pages prévues :**
- `index.html` — Page d'accueil présentant l'agence
- Fenêtre popup avec les informations pour postuler
- Formulaire de disponibilités (à venir)
- Page de connexion redirigeant vers le dashboard

---

## 📊 Dashboard — `dashboard/`

Application analytique privée, accessible uniquement aux utilisateurs autorisés.

**Fonctionnalités prévues :**
- Authentification sécurisée par identifiant / mot de passe
- Import et analyse de fichiers CSV
- Visualisation des données du personnel par événement
- Statistiques sur les heures travaillées, la répartition des postes, la disponibilité

**Stack technique :**
- Python 3.11
- Streamlit
- Pandas
- Plotly

---

## 🐳 Lancer le projet avec Docker

> Prérequis : Docker installé sur la machine

```bash
# Construire et démarrer les conteneurs
docker compose up --build
```

| Service | URL locale |
|---|---|
| Site web | http://localhost:80 |
| Dashboard | http://localhost:8501 |

---

## 🚀 Roadmap

- [x] Initialisation de la repo et structuration de l'architecture
- [x] Développement du site vitrine HTML/CSS
- [ ] Développement de l'application Streamlit
- [ ] Mise en place de l'authentification
- [ ] Connexion site web → dashboard
- [ ] Conteneurisation complète avec Docker Compose
- [ ] Déploiement en production

---

## 🗓️ Échéances

| Livrable | Date cible |
|---|---|
| Dashboard | Fin Avril 2026 |
| Site web fonctionnel | Début Mai |
| Page web interactive complète | Fin Avril |

---

*Projet développé par Ronan Potier*
