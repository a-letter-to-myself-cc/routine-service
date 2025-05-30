from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView



app_name = 'routines'

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", TemplateView.as_view(template_name="commons/index.html"), name="home"),
    path("routine/", include("routine.urls")),  
    path("api/routines/", include("routine.urls")),
]