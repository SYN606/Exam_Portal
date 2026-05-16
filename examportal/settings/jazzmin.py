JAZZMIN_SETTINGS = {

    # Branding
    "site_title":
    "Exam Portal Admin",
    "site_header":
    "Exam Management System",
    "site_brand":
    "Exam Portal",
    "welcome_sign":
    "Manage exams, students, and results",
    "copyright":
    "Exam Portal",

    # Sidebar
    "show_sidebar":
    True,
    "navigation_expanded":
    True,

    # App & Model Order
    "order_with_respect_to": [
        "exams",
    ],

    # Icons
    "icons": {
        "exams.Exam": "fas fa-file-alt",
        "exams.Subject": "fas fa-book",
        "exams.Question": "fas fa-question-circle",
        "students.Student": "fas fa-user-graduate",
        "teachers.Teacher": "fas fa-chalkboard-teacher",
        "results.Result": "fas fa-chart-line",
        "results.Attendance": "fas fa-calendar-check",
        "auth.User": "fas fa-user-shield",
        "auth.Group": "fas fa-users-cog",
    },

    # Top Menu
    "topmenu_links": [
        {
            "name": "Dashboard",
            "url": "/admin",
            "new_window": False,
        },
        {
            "name": "View Website",
            "url": "/",
            "new_window": True,
        },
    ],

    # UI Cleanup
    "hide_apps": [],
    "hide_models": [],

    # Customization
    "show_ui_builder":
    False,
    "changeform_format":
    "horizontal_tabs",
    "related_modal_active":
    True,
}

JAZZMIN_UI_TWEAKS = {

    # Theme
    "theme": "cyborg",
    "dark_mode_theme": "cyborg",

    # Navbar
    "navbar": "navbar-dark navbar-primary",

    # Sidebar
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,

    # Brand
    "brand_colour": "navbar-primary",

    # Accent
    "accent": "accent-primary",

    # Buttons
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },

    # Misc
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
}
