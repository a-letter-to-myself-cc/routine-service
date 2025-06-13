from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now, localtime
from django.views.decorators.http import require_GET
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import LetterRoutine, SpecialDateRoutine
from datetime import datetime, timedelta
from .service import verify_access_token  # auth-service에 요청 보내는 함수


# 요일 문자열을 숫자로 매핑
WEEKDAYS = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}


# Authorization 헤더에서 사용자 ID 추출하는 유틸 함수
def get_user_from_token(request):
    #Authorization 헤더에서 직접 토큰 파싱
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Exception("Access token missing in Authorization header")
    token = auth_header.split(" ")[1]

    token = auth_header.split(" ")[1]
    #verify_access_token(token) 호출
    return verify_access_token(token)

# 루틴 등록 API (POST: 루틴 저장)
@api_view(['POST'])
def save_routine(request):

    try:
        user_id = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)
    
    data = request.data
    routine = None
    special_routine = None

    # 일반 루틴 등록 (요일 or 날짜 기반)
    if "title" in data:
        title = data.get("title") or "기본 루틴 제목"
        routine_type = data.get("routine_type")
        day_of_week = data.get("day_of_week") if routine_type == "weekly" else None
        day_of_month = data.get("day_of_month") if routine_type == "monthly" else None
        time = data.get("routine_time")

        routine = LetterRoutine.objects.create(
            user_id=user_id,
            title=title,
            routine_type=routine_type,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            time=time
        )

    # SpecialDay 루틴 등록
    elif "name" in data:
        name = data.get("name")
        date = data.get("date")

        special_routine = SpecialDateRoutine.objects.create(
            user_id=user_id,
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

    # 등록 결과 반환
    return JsonResponse({
        "routine_id": routine.id if routine else None,
        "special_routine_id": special_routine.id if special_routine else None
    })



@api_view(['GET'])
def list_routines(request):
    try:
        user_id = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)

    routines = LetterRoutine.objects.filter(user_id=user_id)
    special_dates = SpecialDateRoutine.objects.filter(user_id=user_id)

    routine_data = []
    for r in routines:
        routine_data.append({
            "id": r.id,
            "title": r.title,
            "routine_type": r.routine_type,
            "day_of_week": r.day_of_week,
            "day_of_month": r.day_of_month,
            "routine_time": str(r.time),
            "type": "routine"
        })

    special_data = []
    for s in special_dates:
        special_data.append({
            "id": s.id,
            "name": s.name,
            "date": s.date.strftime("%Y-%m-%d"),
            "type": "special"
        })

    return Response(routine_data + special_data)




#루틴 목록을 캘린더 이벤트 형식으로 반환
@api_view(['GET'])
def get_routine_events(request):
    
    try:
        user_id = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)

    routines = LetterRoutine.objects.filter(user_id=user_id)
    special_dates = SpecialDateRoutine.objects.filter(user_id=user_id)

    
    today = datetime.today().date()
    events = []

    # 주간 루틴 → 1년치 (52주) 반복 이벤트 생성
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
        # 월간 루틴 → 12개월 반복 이벤트 생성
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
                
    # 특별 날짜 루틴 이벤트 추가
    for special in special_dates:
        events.append({
            "title": f"🎉 {special.name}",
            "start": special.date.strftime("%Y-%m-%d"),
            "allDay": True,
            "color": "#3399ff"
        })

    return JsonResponse(events, safe=False)


# 루틴 삭제 API
@api_view(['DELETE'])
def delete_routine(request, pk):
    
    try:
        user_id = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)

    
    try:
        # 해당 루틴이 사용자의 것인지 확인 후 삭제
        routine = get_object_or_404(LetterRoutine, pk=pk, user_id=user_id)
        routine.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# 현재 시간 기준으로 알림 보낼 루틴 조회 (Celery가 호출)
@api_view(['GET'])
def get_today_routines(request):
    
    try:
        user_id = get_user_from_token(request)
    except Exception as e:
        return Response({"detail": str(e)}, status=401)
    
    
    now_dt = localtime(now()).replace(second=0, microsecond=0) # 현재 시간 (초 단위 제거)
    today = now_dt.strftime("%A") # 예: Monday
    current_day = now_dt.day
    window_start = (now_dt - timedelta(minutes=1)).time() # 알림 오차 허용 범위: -1분
    window_end = (now_dt + timedelta(minutes=1)).time() # +1분
    
    

    # 현재 시간대에 해당하는 루틴 조회
    routines = LetterRoutine.objects.filter(
        user_id=user_id,
        time__range=(window_start, window_end)
    )

    
    result = []

    # 요일 또는 날짜 조건 확인
    for r in routines:
        if r.routine_type == 'weekly' and r.day_of_week == today:
            result.append({
                "user_email": r.user_email,
                "username": r.username,
                "time": str(r.time)
            })
        elif r.routine_type == 'monthly' and r.day_of_month == current_day:
            result.append({
                "user_email": r.user_email,
                "username": r.username,
                "time": str(r.time)
            })

    return JsonResponse(result, safe=False)


# ✅ 테스트용 루틴 데이터 반환 (스케줄러용 목업 응답)
@api_view(['GET'])
def test_routines_for_scheduler(request):
    routines = LetterRoutine.objects.all()[:3]  # 일부만 테스트용으로
    result = []

    for r in routines:
        result.append({
            "email": "dummy@example.com",   # 실제 email 없어도 됨
            "username": "TestUser", # 테스트용 이름
            "time": str(r.time),
        })

    return JsonResponse(result, safe=False)

# 헬스체크용 엔드포인트 
@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"})


