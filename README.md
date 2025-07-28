# 📝 Exam Portal

**Exam Portal** is a Django-based web application that allows users to take exams online. Admins can create exams, add questions, and manage participant data. Participants can register, take exams, and receive automatic results.

## 🚀 Features

- 👨‍🏫 Admin interface to manage exams, questions, and participants
- ✅ Exam visibility toggle (show/hide exams)
- 🧑 Participant registration form before each exam
- 🧠 Exam questions rendered dynamically
- 🧮 Auto-grading with detailed result feedback
- 🕒 Timer-ready structure (easy to add countdown)
- 📊 Clean database models using Django ORM

## 📦 Project Structure

```
examportal/
├── exam/               # Main app for exams
│   ├── models.py       # Exam, Question, Participant models
│   ├── views.py        # Core views (home, start_exam, submit_exam)
│   ├── admin.py        # Admin panel customization
│   ├── urls.py         # App routing
│   └── templates/      # HTML templates (home, exam page, etc.)
├── examportal/
│   ├── settings.py     # Project settings
│   └── urls.py         # Main URL routing
├── db.sqlite3          # SQLite database
└── manage.py           # Django project manager
```

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd examportal
```

### 2. Create a Virtual Environment (Optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/Mac
```

### 3. Install Dependencies

```bash
pip install django
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

Then open your browser and go to:

```
http://127.0.0.1:8000/
```

## 🔑 Admin Access

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

Then visit:

```
http://127.0.0.1:8000/admin/
```

## 📌 Technologies Used

- Python 3
- Django 5.2
- SQLite3 (default database)
- HTML5 / CSS3 (templates)

## 💡 Future Enhancements

- Countdown timer for exams
- Result download in PDF format
- REST API for mobile/web clients
- OTP or email login for participants

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to improve.
.
----Aditya pathak 
