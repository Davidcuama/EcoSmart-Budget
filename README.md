# EcoSmart - Personal Budget Manager

EcoSmart is a web application built with Django that helps users manage their personal finances by recording income and expenses, setting category budgets, viewing transaction history, and analyzing key financial statistics.

---

## Requirements

| ID | Requirement | Sprint | Status | Responsible |
|----|-------------|--------|--------|-------------|
| FR1 | Register new users securely | Sprint 1 | Done | David Cuadros |
| FR2 | Authenticate registered users | Sprint 1 | Done | David Cuadros |
| FR3 | Record income entries with amount and date | Sprint 1 | Done | Miguel Mercado |
| FR4 | Record expense entries with category and amount | Sprint 1 | Done | Miguel Mercado |
| FR5 | Create monthly budgets per category | Sprint 1 | Done | Victor Infante |
| FR6 | Retrieve and display transaction history | Sprint 2 | Done | Victor Infante |
| FR7 | Generate basic income/expense charts | Sprint 1 | Done | David Cuadros |
| FR8 | Manage custom expense categories | Sprint 1 | Done | Miguel Mercado |
| FR9 | Validate all financial inputs | Sprint 1 | Done | Team |
| FR10 | Calculate remaining budget in real time | Sprint 1 | Done | Victor Infante |
| FR11 | Display financial dashboard | Sprint 2 | In Progress | David Cuadros |
| FR15 | Define savings goals | Sprint 2 | In Progress | Miguel Mercado |
| FR16 | Track savings goal progress | Sprint 2 | In Progress | Miguel Mercado |
| FR18 | Filter transactions by date/category/amount | Sprint 2 | Done | David Cuadros |
| FR20 | Calculate key financial statistics | Sprint 2 | Done | Miguel Mercado |

---

## Tech Stack

- Python 3.11
- Django 5.2
- SQLite
- Bootstrap 5.3
- Chart.js

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/Davidcuama/EcoSmart-Budget.git
cd EcoSmart-Budget/EcoSmart

# 2. Install dependencies
pip install django

# 3. Apply migrations
python manage.py migrate

# 4. Run the development server
python manage.py runserver
```

Open in browser: http://127.0.0.1:8000/

---

## Project Structure

```
EcoSmart/
├── EcoSmart/          # Project configuration (settings, urls)
├── budget/            # Main app
│   ├── models.py      # Models: Ingreso, Gasto, Presupuesto, Categoria
│   ├── views.py       # View logic for each feature
│   └── urls.py        # App URL routes
└── templates/
    └── budget/        # HTML templates for each view
```

---

## Available Routes

| Route | Description |
|-------|-------------|
| `/` | Home dashboard with financial summary |
| `/ingreso/` | Record and list income entries |
| `/gasto/` | Record and list expense entries |
| `/presupuesto/` | Create budgets per category |
| `/presupuesto/restante/` | View remaining budget for the current month |
| `/historial/` | Unified transaction history with filters |
| `/estadisticas/` | Key financial statistics and charts |
| `/categorias/` | Manage expense categories |
