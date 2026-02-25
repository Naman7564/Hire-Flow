# 🚀 HireFlow — HR Hiring Platform

A modern, full-stack HR Hiring Web Application built with Django, MySQL, and a stunning dark-theme UI. Containerized with Docker for easy deployment.

![HireFlow Dashboard](https://img.shields.io/badge/HireFlow-Hiring_Platform-6366f1?style=for-the-badge)

## ✨ Features

### Authentication
- User registration with role selection (HR/Candidate)
- Secure login/logout with Django auth
- Password change functionality
- Role-based access control

### HR Panel (Admin Dashboard)
- 📊 Analytics dashboard with pipeline charts
- ➕ Create, edit, delete job postings
- 👥 View all candidates per job
- 🔍 Filter candidates by skills, experience, status
- 📋 Update application status (Applied → Hired/Rejected)
- 📄 View candidate profiles and resumes

### Candidate Panel
- 🎯 Browse available jobs with search & filters
- 📝 Apply to jobs with cover letter and resume
- 📊 Track application status
- ✏️ Edit profile, skills, and upload resume
- 🏠 Dashboard with profile completion checklist

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 4.2 (Python) |
| Database | MySQL 8.0 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Web Server | Gunicorn + Nginx |
| Containers | Docker & Docker Compose |

## 📁 Project Structure

```
HR hiring/
├── hr_hiring/          # Django project settings
├── accounts/           # User auth, profiles
├── jobs/               # Job postings CRUD
├── applications/       # Job applications
├── dashboard/          # Dashboard views
├── templates/          # HTML templates
│   ├── accounts/       # Login, register, profile
│   ├── dashboard/      # HR & Candidate dashboards
│   ├── jobs/           # Job listing, detail, form
│   └── applications/   # Apply, status, tracking
├── static/             # CSS & JavaScript
├── nginx/              # Nginx configuration
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone and navigate to the project
cd "HR hiring"

# Start all services
docker-compose up --build

# Access the application
# → http://localhost
```

### Default Admin Account
- **Username:** admin
- **Password:** admin123
- **Role:** HR/Admin

## 🎨 UI Theme
- Premium dark theme with glassmorphism effects
- Gradient accent colors (Indigo/Purple)
- Responsive design (mobile + desktop)
- Canvas-based analytics charts
- Smooth micro-animations
- Font: Inter (Google Fonts)

## 📝 License
MIT License
