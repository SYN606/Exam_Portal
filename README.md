# 📝 Django Exam Portal

A web-based online examination system built using Django. This platform allows participants to take exams with automatic answer saving, resuming capability, timer enforcement, and basic cheating prevention.

## 📌 Features

- 🔐 Participant login using name and mobile number
- 🎯 Multiple exams with visibility toggle
- 🔄 Resume exam after refresh/server restart
- ✅ Auto-save answers after every question
- 📊 Real-time score calculation and result display
- ⏱ Exam-wide timer + per-question lock timer
- 🚫 Tab switch detection (auto-submit after 3 warnings)
- 🔐 No right-click, copy-paste, or Tab switching allowed during exam

## 🛠 Tech Stack

- **Backend**: Django 5.x
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default, easy to replace with PostgreSQL/MySQL)

## 📂 Project Structure

examportal/
├── exam/
│ ├── migrations/
│ ├── static/
│ ├── templates/
│ │ └── exam/
│ │ ├── home.html
│ │ ├── participant_form.html
│ │ └── exam_page.html
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── forms.py
│ ├── models.py
│ ├── tests.py
│ ├── urls.py
│ └── views.py
├── examportal/
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── db.sqlite3
└── manage.py
## 🛠️ Setup Instructions


## 📋 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/exam-portal.git
cd exam-portal```


### 2. Create a Virtual Environment (if You want)
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt



### 3. Install Dependencies


pip install django


### 4. Apply Migrations


python manage.py makemigrations
python manage.py migrate


### 5. Run the Development Server


python manage.py runserver


Then open your browser and go to:

```
http://127.0.0.1:8000/
```

## 🔑 Admin Access

To access the Django admin panel:


python manage.py createsuperuser


Then visit:

```
http://127.0.0.1:8000/admin/
```

## 📌 Technologies Used

- Python 3
- Django 5.2
- SQLite3 (default database)
- HTML5 / CSS3 (templates)


## 💡 Models 

Exam: Title, description, duration, visibility.

Question: Belongs to an Exam. Has 4 options + correct answer.

Participant: Linked to an Exam with name, mobile number, and score.

ParticipantAnswer: Stores per-question answer and allows resume support.

👨‍💻 Author
Developed by [Aditya Pathak].
Email: skilldotpy@gmail.com
GitHub: https://github.com/sde-666
