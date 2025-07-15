# 🏋️ Gym Management System (Django)

A complete web-based Gym Management System built with Django, HTML, CSS, and JavaScript. This system supports multiple user roles with separate dashboards and a mock payment system.

---

## 🚀 Features

### 🔐 Authentication
- Role-based login system (Admin, Trainer, Member)
- Registration & secure login/logout

### 👑 Admin Dashboard
- View/add/delete users (trainers/members)
- Assign trainers to members
- Generate mock reports

### 🏋️ Trainer Dashboard
- View assigned members
- Upload workout and diet plans
- Track member progress

### 💪 Member Dashboard
- View trainer, workout plan, and diet chart
- Submit feedback
- Track personal progress
- Mock payment interface

### 💳 Payment (Mock)
- View pricing plans (monthly, quarterly, yearly)
- Simulate successful payment (UI only, no real transaction)

---

## ⚙️ Tech Stack

- **Backend:** Django 4.x (Python 3.x)
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite3
- **Templates:** Django Template Language (DTL)
- **Styling:** Basic CSS (Bootstrap optional)

---

## 📁 Project Structure

gym_management/
├── users/ # Custom user logic (login, register)
├── dashboard/ # Role-based dashboards
├── templates/ # HTML templates
├── static/ # CSS, JS files
├── gym_management/ # Main Django settings and URLs
├── db.sqlite3 # Database


## 🛠️ Setup Instructions

1. **Clone the repo or copy files:**

```bash
git clone <your_repo_url>
cd gym_management

2. **Create a virtual environment (optional but recommended):**

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\\Scripts\\activate    # Windows

3. Install dependencies:

pip install django

4. Run migrations:

python manage.py makemigrations
python manage.py migrate

5.Create superuser:

python manage.py createsuperuser

6.Start the server:

python manage.py runserver

7.Visit:

http://127.0.0.1:8000/

🧪 Test Users (Example)
Username	Password	Role
admin1	admin123	Admin
trainer1	train123	Trainer
member1	mem123	Member

📌 Notes
No real payment integration — mock only

Uses Django’s built-in auth system extended with role support

Easy to extend: Add attendance, reports, analytics

📄 License
MIT — free to use and modify.
---

