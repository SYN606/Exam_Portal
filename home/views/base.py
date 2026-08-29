from django.shortcuts import render
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"


class ContactView(TemplateView):
    template_name = "contact.html"


class FAQView(TemplateView):
    template_name = "faq.html"


def custom_404_view(request, exception=None):
    return render(request, "404.html", status=404)