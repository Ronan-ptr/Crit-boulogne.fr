# 🎯 Crit Agency — Web Platform & HR Dashboard

A digital platform for **Crit Event Agency**, featuring a public-facing website and a secure analytical dashboard for managing event staff data.

---

## 📌 Objective

Provide Crit Agency with a simple and effective tool to:
- Showcase the agency through a public website
- Analyze event staff data via a private dashboard

---

## 🏗️ Project Architecture

```
crit-agency/
│
├── .gitignore                  # Files excluded from Git
├── README.md                   # Project documentation
├── docker-compose.yml          # Container orchestration (coming soon)
│
├── data/                       # Where you should put the data and ressources
│
├── website/                    # Public website (HTML/CSS)
│   ├── index.html              # Agency homepage
│   ├── style.css               # Stylesheet
│   └── assets/                 # Images, icons, fonts
│
└── dashboard/                  # Analytical application (Python/Streamlit)
    ├── Dockerfile              # Dashboard Docker image
    ├── requirements.txt        # Python dependencies
    ├── app.py                  # Main Streamlit application
    └── data/                   # Event CSV files (ignored by Git)
        └── .gitkeep
```
## 🌐 Website — `website/`

Public-facing showcase website for Crit Agency.

**Planned Pages:**
- `index.html` — Homepage introducing the agency
- Popup window with application information
- Availability form (coming soon)
- Login page redirecting to the dashboard

---

## 📊 Dashboard — `dashboard/`

Private analytical application, accessible only to authorized users.

**Planned Features:**
- Secure authentication (username/password)
- CSV file import and analysis
- Event staff data visualization
- Statistics on hours worked, role distribution, and availability

**Tech Stack:**
- Python 3.11
- Streamlit
- Pandas
- Plotly

---

## 🐳 Run the Project with Docker

> Prerequisites: Docker installed on your machine

```bash
# Construire et démarrer les conteneurs
docker compose up --build
```

| Service | local URL |
|---|---|
| Site web | http://localhost:80 |
| Dashboard | http://localhost:8501 |

---

## 🚀 Roadmap

- [x] Initialize repository and structure architecture
- [x] Develop HTML/CSS showcase website
- [ ] Develop Streamlit application
- [ ] Implement authentication
- [ ] Connect website to dashboard
- [ ] Full containerization with Docker Compose
- [ ] Production deployment
---

## 🗓️ Milestones

| Deliverable | Target Date |
|---|---|
| Dashboard | End of April |
| Complete interactive web page | Early May |
| Functional website | End of May |

---

*Project developed by Ronan Potier*
