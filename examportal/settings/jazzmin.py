JAZZMIN_SETTINGS = {
    # Branding
    "site_title":
    "Exam Portal Admin",
    "site_header":
    "Exam Management System",
    "site_brand":
    "Exam Portal",
    "welcome_sign":
    "Welcome to Exam Portal Management",
    "copyright":
    "Exam Portal",

    # Search & User Menu
    "search_model": ["exam.Exam", "auth.User"],
    "user_avatar":
    None,

    # Sidebar
    "show_sidebar":
    True,
    "navigation_expanded":
    True,
    "hide_apps": [],
    "hide_models": [],

    # App & Model Ordering
    "order_with_respect_to": [
        "exam",
        "home",
        "auth",
    ],

    # FontAwesome Icons (Updated for exact app names: 'exam', 'home', 'auth')
    "icons": {
        # Exam App Models
        "exam.Exam": "fas fa-file-alt",
        "exam.Question": "fas fa-question-circle",
        "exam.Option": "fas fa-list-ul",
        "exam.Participant": "fas fa-user-graduate",
        "exam.ParticipantAnswer": "fas fa-tasks",

        # Core Auth & Django Models
        "auth.User": "fas fa-user-shield",
        "auth.Group": "fas fa-users-cog",
    },

    # Top Navigation Bar Links
    "topmenu_links": [
        {
            "name": "Dashboard",
            "url": "admin:index",
            "permissions": ["auth.view_user"],
        },
        {
            "name": "View Site",
            "url": "home:homepage",
            "new_window": True,
        },
    ],

    # UI Behaviors
    "show_ui_builder":
    False,
    "changeform_format":
    "horizontal_tabs",
    "related_modal_active":
    True,
    "use_google_fonts_roboo":
    True,
}

JAZZMIN_UI_TWEAKS = {
    # Light Theme Selection
    "theme": "flatly",
    "dark_mode_theme": None,

    # Navbar Styling (Clean White Header)
    "navbar": "navbar-white navbar-light border-bottom",

    # Sidebar Styling (Light Slate Sidebar with Indigo Selection)
    "sidebar": "sidebar-light-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,

    # Brand Logo Area
    "brand_colour": "navbar-indigo",

    # UI Accent Colors
    "accent": "accent-indigo",

    # Button Design
    "button_classes": {
        "primary": "btn-indigo text-white",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },

    # Typography Tweaks
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
}
