from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializer import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime
# Create your views here.

#register
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Tạo UserProfile tự động khi đăng ký
        UserProfile.objects.create(user_id=user)
        return Response(
            {
                'message': 'registered successfully!',
                'user_id': user.id,
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###login
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login successful!",
        "user_id": user.id,
        "username": user.username,
        "role": "admin" if user.is_staff else "user",
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }, status=status.HTTP_200_OK)


#USER PROFILE VIEWS 
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    try:
        profile = UserProfile.objects.get(user_id=request.user)
    except UserProfile.DoesNotExist:
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#TASK STATUS ICON VIEWS 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_status_icons(request):    
    if request.method == 'GET':
        icons = TaskStatusIcon.objects.filter(user_id=request.user)
        serializer = TaskStatusIconSerializer(icons, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        request.data['user_id'] = request.user.id
        serializer = TaskStatusIconSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_status_icon_detail(request, icon_id):
    try:
        icon = TaskStatusIcon.objects.get(id=icon_id, user_id=request.user)
    except TaskStatusIcon.DoesNotExist:
        return Response({"detail": "Icon not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskStatusIconSerializer(icon)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = TaskStatusIconSerializer(icon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        icon.delete()
        return Response({"message": "Icon deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#  DAILY TASK LIST VIEWS 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def daily_task_lists(request):    
    if request.method == 'GET':
        date_str = request.query_params.get('date')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                daily_list = DailyTaskList.objects.filter(user_id=request.user, date=date)
            except ValueError:
                return Response({"detail": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            daily_list = DailyTaskList.objects.filter(user_id=request.user).order_by('-date')
        
        serializer = DailyTaskListSerializer(daily_list, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        date_str = request.data.get('date')
        if not date_str:
            date = timezone.now().date()
        else:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"detail": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra đã tạo danh sách cho ngày này chưa
        existing = DailyTaskList.objects.filter(user_id=request.user, date=date)
        if existing.exists():
            return Response(
                {"detail": f"Daily task list already exists for {date}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        daily_list = DailyTaskList.objects.create(user_id=request.user, date=date)
        serializer = DailyTaskListSerializer(daily_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def daily_task_list_detail(request, list_id):
    try:
        daily_list = DailyTaskList.objects.get(id=list_id, user_id=request.user)
    except DailyTaskList.DoesNotExist:
        return Response({"detail": "Daily task list not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DailyTaskListSerializer(daily_list)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = DailyTaskListSerializer(daily_list, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        daily_list.delete()
        return Response({"message": "Daily task list deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#  TASK VIEWS 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tasks(request):    
    if request.method == 'GET':
        list_id = request.query_params.get('list_id')
        status_filter = request.query_params.get('status')
        
        tasks_query = Task.objects.filter(user_id=request.user)
        
        if list_id:
            tasks_query = tasks_query.filter(list_id=list_id)
        if status_filter:
            tasks_query = tasks_query.filter(status_icon_id=status_filter)
        
        serializer = TaskSerializer(tasks_query.order_by('-created_at'), many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        request.data['user_id'] = request.user.id
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user_id=request.user)
    except Task.DoesNotExist:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_task_completion(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user_id=request.user)
    except Task.DoesNotExist:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    task.is_completed = not task.is_completed
    task.save()
    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  STATISTICS VIEWS 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_statistics(request):
    user_tasks = Task.objects.filter(user_id=request.user)
    
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(is_completed=True).count()
    pending_tasks = user_tasks.filter(is_completed=False).count()
    
    return Response({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": f"{(completed_tasks / total_tasks * 100):.2f}%" if total_tasks > 0 else "0%"
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_calendar_statistics(request):
    """
    API thống kê công việc theo tháng cho trang lịch
    Query params: year (2025), month (1-12)
    Response: Danh sách ngày trong tháng với số task, completed, pending
    """
    from calendar import monthrange
    
    year = request.query_params.get('year')
    month = request.query_params.get('month')
    
    if not year or not month:
        now = timezone.now()
        year = now.year
        month = now.month
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        return Response({"detail": "Invalid year or month"}, status=status.HTTP_400_BAD_REQUEST)
    
    if month < 1 or month > 12:
        return Response({"detail": "Month must be between 1 and 12"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Lấy số ngày trong tháng
    _, days_in_month = monthrange(year, month)
    
    calendar_data = []
    
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day).date()
        
        # Lấy daily task list của ngày này
        daily_list = DailyTaskList.objects.filter(user_id=request.user, date=date).first()
        
        if daily_list:
            tasks = Task.objects.filter(list_id=daily_list)
            total = tasks.count()
            completed = tasks.filter(is_completed=True).count()
            pending = tasks.filter(is_completed=False).count()
        else:
            total = 0
            completed = 0
            pending = 0
        
        calendar_data.append({
            "date": date.isoformat(),
            "day": day,
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": f"{(completed / total * 100):.0f}%" if total > 0 else "0%",
            "has_tasks": total > 0
        })
    
    return Response({
        "year": year,
        "month": month,
        "calendar": calendar_data
    })