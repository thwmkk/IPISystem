import secrets
import string

from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Department, UserRole, Employee,
    VerificationRequest,
    ScientificWork, OrganizationalWork, TechnicalWork,
    KPIGroup, KPIWeight, KPIResult,
    Task,
)
from .ipi_calculator import calculate_ipi, recalculate_all
from .rule_engine import apply_rules, assign_weights, assign_weights_all
from .serializers import (
    DepartmentSerializer, UserRoleSerializer,
    EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateSerializer,
    VerificationRequestSerializer,
    ScientificWorkSerializer,
    OrganizationalWorkSerializer,
    TechnicalWorkSerializer,
    KPIGroupSerializer, KPIWeightSerializer, KPIResultSerializer,
    TaskSerializer,
    LoginSerializer,
)


# ============================================================
#  Permissions
# ============================================================

class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'employee'):
            return False
        return request.user.employee.role.role_name in ('руководитель', 'администратор')


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'employee'):
            return False
        return request.user.employee.role.role_name == 'администратор'


# ============================================================
#  Auth
# ============================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'detail': 'Неверный email или пароль'}, status=status.HTTP_401_UNAUTHORIZED)

    employee = getattr(user, 'employee', None)
    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'employee_id': employee.id if employee else None,
            'full_name': employee.full_name if employee else user.username,
            'role': employee.role.role_name if employee else None,
        }
    })


@api_view(['GET'])
def me_view(request):
    user = request.user
    employee = getattr(user, 'employee', None)
    return Response({
        'id': user.id,
        'email': user.email,
        'employee_id': employee.id if employee else None,
        'full_name': employee.full_name if employee else user.username,
        'role': employee.role.role_name if employee else None,
        'position': employee.position if employee else None,
        'department': employee.department.department_short_name if employee else None,
    })


# ============================================================
#  Справочники
# ============================================================

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer


# ============================================================
#  Сотрудники
# ============================================================

def _generate_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department', 'role').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        if self.action in ('retrieve', 'update', 'partial_update'):
            return EmployeeDetailSerializer
        return EmployeeListSerializer

    def perform_create(self, serializer):
        employee = serializer.save()
        password = _generate_password()
        user = User.objects.create_user(
            username=employee.email,
            email=employee.email,
            password=password,
        )
        employee.user = user
        employee.save(update_fields=['user'])
        # TODO: send email with credentials (employee.email, password)
        self._generated_password = password

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        data['generated_password'] = self._generated_password
        return Response(data, status=status.HTTP_201_CREATED)


# ============================================================
#  Верификация
# ============================================================

class VerificationRequestViewSet(viewsets.ModelViewSet):
    queryset = VerificationRequest.objects.select_related('requester', 'evaluator').all()
    serializer_class = VerificationRequestSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        vr = self.get_object()
        vr.status = 'approved'
        vr.evaluator = request.user.employee
        vr.save()
        for work in vr.scientific_works.all():
            work.verified = True
            work.save(update_fields=['verified'])
        for work in vr.organizational_works.all():
            work.verified = True
            work.save(update_fields=['verified'])
        for work in vr.technical_works.all():
            work.verified = True
            work.save(update_fields=['verified'])
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        vr = self.get_object()
        vr.status = 'rejected'
        vr.evaluator = request.user.employee
        vr.comment = request.data.get('comment', '')
        vr.save()
        return Response({'status': 'rejected'})


# ============================================================
#  Научные работы
# ============================================================

class ScientificWorkViewSet(viewsets.ModelViewSet):
    queryset = ScientificWork.objects.select_related(
        'employee', 'verification_request',
        'publication__article', 'publication__monograph',
        'dissertation', 'project_participation', 'software',
    ).all()
    serializer_class = ScientificWorkSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.role.role_name == 'сотрудник':
            qs = qs.filter(employee=user.employee)
        return qs


# ============================================================
#  Организационные работы
# ============================================================

class OrganizationalWorkViewSet(viewsets.ModelViewSet):
    queryset = OrganizationalWork.objects.select_related('employee', 'verification_request').all()
    serializer_class = OrganizationalWorkSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.role.role_name == 'сотрудник':
            qs = qs.filter(employee=user.employee)
        return qs


# ============================================================
#  Технические работы
# ============================================================

class TechnicalWorkViewSet(viewsets.ModelViewSet):
    queryset = TechnicalWork.objects.select_related('employee', 'verification_request').all()
    serializer_class = TechnicalWorkSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.role.role_name == 'сотрудник':
            qs = qs.filter(employee=user.employee)
        return qs


# ============================================================
#  KPI
# ============================================================

class KPIGroupViewSet(viewsets.ModelViewSet):
    queryset = KPIGroup.objects.all()
    serializer_class = KPIGroupSerializer


class KPIWeightViewSet(viewsets.ModelViewSet):
    queryset = KPIWeight.objects.select_related('kpi_group').all()
    serializer_class = KPIWeightSerializer


class KPIResultViewSet(viewsets.ModelViewSet):
    queryset = KPIResult.objects.select_related('employee').all()
    serializer_class = KPIResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.role.role_name == 'сотрудник':
            qs = qs.filter(employee=user.employee)
        return qs


# ============================================================
#  Задачи
# ============================================================

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('assigned_to', 'created_by', 'kpi_group').all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'employee') and user.employee.role.role_name == 'сотрудник':
            qs = qs.filter(assigned_to=user.employee) | qs.filter(assigned_to__isnull=True)
        return qs

    @action(detail=True, methods=['post'])
    def take(self, request, pk=None):
        task = self.get_object()
        if task.assigned_to is not None:
            return Response({'detail': 'Задача уже назначена'}, status=status.HTTP_400_BAD_REQUEST)
        task.assigned_to = request.user.employee
        task.status = 'assigned'
        task.save()
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        task = self.get_object()
        task.status = 'in_progress'
        task.save()
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = 'completed'
        task.save()
        return Response(TaskSerializer(task).data)


# ============================================================
#  IPI расчёт
# ============================================================

@api_view(['POST'])
def calculate_ipi_view(request):
    """Рассчитать IPI для сотрудника. Body: {employee_id, year, quarter}"""
    employee_id = request.data.get('employee_id')
    year = request.data.get('year')
    quarter = request.data.get('quarter')

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'detail': 'Сотрудник не найден'}, status=404)

    result = calculate_ipi(employee, int(year), int(quarter))
    return Response(KPIResultSerializer(result).data)


@api_view(['POST'])
def recalculate_all_view(request):
    """Пересчитать IPI для всех сотрудников. Body: {year?, quarter?}"""
    year = request.data.get('year')
    quarter = request.data.get('quarter')
    results = recalculate_all(
        year=int(year) if year else None,
        quarter=int(quarter) if quarter else None,
    )
    return Response(KPIResultSerializer(results, many=True).data)


# ============================================================
#  Rule Engine
# ============================================================

@api_view(['GET'])
def preview_weights_view(request, employee_id):
    """Предпросмотр: какие веса будут назначены сотруднику."""
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'detail': 'Сотрудник не найден'}, status=404)

    result = apply_rules(employee)
    return Response(result)


@api_view(['POST'])
def assign_weights_view(request, employee_id):
    """Применить правила и сохранить веса для сотрудника."""
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'detail': 'Сотрудник не найден'}, status=404)

    weights = assign_weights(employee)
    return Response(KPIWeightSerializer(weights, many=True).data)


@api_view(['POST'])
def assign_weights_all_view(request):
    """Применить правила и назначить веса всем сотрудникам."""
    results = assign_weights_all()
    return Response(results)
