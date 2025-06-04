from django.apps import AppConfig


class RoutineServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    #name = 'routine-service.routine' -> 모놀리식
    name = 'routine'
    
