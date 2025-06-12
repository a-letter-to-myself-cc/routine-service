from django.urls import path
from . import views

app_name = 'routines' # 앱 네임스페이스 설정

# urlpatterns = [
#     path('', views.save_routine, name='routine_home'),     
#     path('api/routines/', views.save_routine, name='save_routine'),  # POST 루틴 저장
#     path('api/routines/events/', views.get_routine_events, name='get_routine_events'),  # GET 루틴 목록
#     path('routine/delete/<int:pk>/', views.delete_routine, name='delete_routine'), # DELETE 루틴 삭제
#     #path("api/routines/today/", views.get_today_routines, name="get_today_routines"),
#     #path("api/routines/today/", views.test_routines_for_scheduler), #테스트용!!!!
#     path('today/', views.test_routines_for_scheduler), # 테스트용 루틴 조회
# ]

#api/routines/ 기준으로 상대 경로

urlpatterns = [
    path('', views.save_routine, name='save_routine'), # /api/routines/
    
    # GET 루틴 목록
    path('events/', views.get_routine_events, name='get_routine_events'), # /api/routines/events/
    
    # DELETE 루틴 삭제
    path('delete/<int:pk>/', views.delete_routine, name='delete_routine'), # /api/routines/delete/3/
    
    # 테스트용 루틴 조회
    path('today/', views.test_routines_for_scheduler), # /api/routines/today/
]
