# BaaS Pro Template

A production-ready, automated Backend-as-a-Service (BaaS) template built with FastAPI, designed for professional scalability and rapid delivery.

## 🚀 Project Objective
Build a high-speed, zero-cost (free-tier) backend stack to accelerate project delivery and maintain professional standards.

## 🛠️ Tech Stack
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (High-performance Python)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database:** [Supabase (PostgreSQL)](https://supabase.com/)
- **Security:** Bcrypt (Salting & Hashing) & JOSE (JWT Authentication)
- **Deployment:** Automated via `build_it_all.py`

## ✨ Core Features
- **Automated Scaffolding:** Single-script setup for directory structure and environment.
- **Database Sync:** Automatic table creation in Supabase directly from Python models.
- **Secure Authentication:** 
  - Salted Bcrypt hashing for password security.
  - JWT (JSON Web Tokens) for stateless, secure session management.
- **Professional Architecture:** Clean separation of concerns (Models, Schemas, API, Core).

## 📂 Project Structure
```text
├── app/
│   ├── api/        # API Endpoints (Auth, etc.)
│   ├── core/       # Database config & Security logic
│   ├── models/     # SQLAlchemy Database Models
│   ├── schemas/    # Pydantic Data Validation
│   └── main.py     # Application Entry point
├── build_it_all.py # Automation script
└── requirements.txt
```

## 🚥 Current Status
- **Security Engine:** 100% Verified (Signup, Login, Token Issuance).
- **Cloud Integration:** Fully synced with Supabase cloud.

## 🗺️ Roadmap
- [ ] **Digital Asset Manager:** Projects table for portfolio storage.
- [ ] **Protected Routes:** JWT-based access control for sensitive endpoints.
- [ ] **Client Documentation:** Auto-generated Swagger/Redoc integration.

---
**Developer:** Revanthraghava  
**Date:** April 2026
