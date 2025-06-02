from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import LetterRoutine, SpecialDateRoutine
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, localtime
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .service import verify_access_token
from django.contrib.auth import get_user_model #  Django에서 현재 사용하는 사용자 모델을 가져옴


#@login_required(login_url='login')

WEEKDAYS = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}


def get_user_from_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise Exception("Authorization header missing")
    token = auth_header.split("Bearer ")[1]
    user_id = verify_access_token(token)
    User = get_user_model()
    return User.objects.get(id=user_id)




@csrf_exempt
@api_view(['POST'])
def save_routine(request):
    
    try:
        request.user = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)
    
    data = request.data
    routine = None
    special_routine = None

    if "title" in data:
        title = data.get("title") or "기본 루틴 제목"
        routine_type = data.get("routine_type")
        day_of_week = data.get("day_of_week") if routine_type == "weekly" else None
        day_of_month = data.get("day_of_month") if routine_type == "monthly" else None
        time = data.get("routine_time")

        routine = LetterRoutine.objects.create(
            user=request.user,
            title=title,
            routine_type=routine_type,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            time=time
        )

    elif "name" in data:
        name = data.get("name")
        date = data.get("date")

        special_routine = SpecialDateRoutine.objects.create(
            user=request.user,
            name=name,
            date=date
        )
    
    # lists = {
    #     "days": days,
    #     "routines": routines,
    #     "specialDays": specialDays,
    #     "routine_id": routine.id if routine else None,
    #     "special_routine_id": special_routine.id if special_routine else None
    # }

    #return render(request, "routines/routine.html", lists)

    return JsonResponse({
        "routine_id": routine.id if routine else None,
        "special_routine_id": special_routine.id if special_routine else None
    })


#@login_required
@api_view(['GET'])
def get_routine_events(request):
    
    try:
        request.user = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)

    
    # User = get_user_model()
    
    # #임시 유저 할당!!
    # request.user = User.objects.first()
    

    user = request.user
    routines = LetterRoutine.objects.filter(user=user)
    special_dates = SpecialDateRoutine.objects.filter(user=user)

    
    today = datetime.today().date()
    events = []

    for routine in routines:
        if routine.routine_type == "weekly":
            weekday = routine.day_of_week
            if weekday:
                weekday_num = WEEKDAYS[weekday]
                next_date = today + timedelta(days=(weekday_num - today.weekday() + 7) % 7)
                for i in range(52):
                    events.append({
                        "id": routine.id,
                        "title": routine.title,
                        "start": (next_date + timedelta(weeks=i)).strftime("%Y-%m-%d"),
                        "allDay": True
                    })
        elif routine.routine_type == "monthly":
            for month in range(1, 13):
                try:
                    events.append({
                        "id": routine.id,
                        "title": routine.title,
                        "start": f"2025-{month:02d}-{routine.day_of_month:02d}",
                        "allDay": True
                    })
                except:
                    continue

    for special in special_dates:
        events.append({
            "title": f"🎉 {special.name}",
            "start": special.date.strftime("%Y-%m-%d"),
            "allDay": True,
            "color": "#3399ff"
        })

    return JsonResponse(events, safe=False)



@api_view(['DELETE'])
def delete_routine(request, pk):
    
    try:
        request.user = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)

    
    try:
        routine = get_object_or_404(LetterRoutine, pk=pk, user=request.user)
        routine.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@api_view(['GET'])
def get_today_routines(request):
    
    try:
        request.user = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)
    
    
    now_dt = localtime(now()).replace(second=0, microsecond=0)
    today = now_dt.strftime("%A")
    current_day = now_dt.day
    window_start = (now_dt - timedelta(minutes=1)).time()
    window_end = (now_dt + timedelta(minutes=1)).time()
    
    
    # User = get_user_model()
    
    # user = User.objects.first()  # 임시 사용자

    routines = LetterRoutine.objects.filter(user=user, time__range=(window_start, window_end))
    result = []

    for r in routines:
        if r.routine_type == 'weekly' and r.day_of_week == today:
            result.append({
                "user_email": r.user.email,
                "username": r.user.username,
                "time": str(r.time)
            })
        elif r.routine_type == 'monthly' and r.day_of_month == current_day:
            result.append({
                "user_email": r.user.email,
                "username": r.user.username,
                "time": str(r.time)
            })

    return JsonResponse(result, safe=False)

@csrf_exempt
@api_view(['GET'])
def test_routines_for_scheduler(request):
    routines = LetterRoutine.objects.all()[:3]  # 일부만 테스트용으로
    result = []

    for r in routines:
        result.append({
            "email": "dummy@example.com",   # 실제 email 없어도 됨
            "username": "TestUser",
            "time": str(r.time),
        })

    return JsonResponse(result, safe=False)