from django.urls import path
from . import views

app_name = 'routines' # 앱 네임스페이스 설정

#api/routines/ 기준으로 상대 경로

urlpatterns = [
    path('', views.save_routine, name='save_routine'), # /api/routines/
    
    # GET 루틴 캘린더 목록
    path('events/', views.get_routine_events, name='get_routine_events'), # /api/routines/events/
    
    path('list/', views.list_routines, name='list_routine'),
    
    # DELETE 루틴 삭제
    path('delete/<int:pk>/', views.delete_routine, name='delete_routine'), # /api/routines/delete/3/
    
    # 테스트용 루틴 조회
    path('today/', views.test_routines_for_scheduler), # /api/routines/today/
]
