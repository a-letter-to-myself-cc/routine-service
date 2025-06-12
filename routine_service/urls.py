from django.contrib import admin
from django.urls import path, include # URL 라우팅을 위한 함수
from django.views.generic import TemplateView
from routine.views import health_check # 헬스체크용 뷰 함수 import

urlpatterns = [
     # Django 기본 관리자 페이지 경로 (/admin/)
    path('admin/', admin.site.urls),
    
    # 루트 경로('/') 요청 시 commons/index.html 템플릿 렌더링
    path("", TemplateView.as_view(template_name="commons/index.html"), name="home"),
    
    # 실제 요청 경로: /api/routines/{save,events,delete,today}
    path("api/routines/", include("routine.urls")), 
    
    # /health/ 경로 요청 시 health_check 뷰 호출
    path("health/", health_check),
]