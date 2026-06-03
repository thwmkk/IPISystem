import secrets
import string

from django.contrib.auth.models import User
from django.db import models as db_models
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Department, UserRole, Employee,
    VerificationRequest,
    ScientificWork, OrganizationalWork, TechnicalWork,
    KPIGroup, KPIIndicator, KPIGroupWeight, KPIResult,
    Project, ProjectMember,
    Task, Attachment,
)
from .ipi_calculator import calculate_ipi, recalculate_all, calculate_breakdown
from .serializers import (
    DepartmentSerializer, UserRoleSerializer,
    EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateSerializer,
    VerificationRequestSerializer,
    ScientificWorkSerializer,
    OrganizationalWorkSerializer,
    TechnicalWorkSerializer,
    KPIGroupSerializer, KPIIndicatorSerializer, KPIGroupWeightSerializer, KPIResultSerializer,
    ProjectListSerializer, ProjectDetailSerializer, ProjectMemberSerializer,
    TaskSerializer, AttachmentSerializer,
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

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdmin()]


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdmin()]


# ============================================================
#  Сотрудники
# ============================================================

def _generate_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department', 'role').all()

    def get_permissions(self):
        # Создание / редактирование / удаление сотрудников — только руководитель или админ
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]

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
        employees_to_recalc = set()
        for work in vr.scientific_works.all():
            work.verified = True
            work.save(update_fields=['verified'])
            employees_to_recalc.add(work.employee)
        for work in vr.organizational_works.all():
            work.verified = True
            work.save(update_fields=['verified'])
            employees_to_recalc.add(work.employee)
        for work in vr.technical_works.all():
            work.verified = True
            work.save(update_fields=['verified'])
            employees_to_recalc.add(work.employee)
        from datetime import date
        now = date.today()
        quarter = (now.month - 1) // 3 + 1
        for emp in employees_to_recalc:
            calculate_ipi(emp, now.year, quarter)
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        vr = self.get_object()
        vr.status = 'rejected'
        vr.evaluator = request.user.employee
        vr.comment = request.data.get('comment', '')
        vr.save()
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def update_work(self, request, pk=None):
        """Руководитель редактирует привязанную работу."""
        vr = self.get_object()
        data = request.data
        work = (
            vr.scientific_works.first()
            or vr.organizational_works.first()
            or vr.technical_works.first()
        )
        if not work:
            return Response({'detail': 'Работа не найдена'}, status=404)

        for field in ('title', 'work_type', 'points'):
            if field in data:
                setattr(work, field, data[field])

        if vr.work_type == 'organizational':
            for field in ('event_date', 'participants_count'):
                if field in data:
                    setattr(work, field, data[field])
        elif vr.work_type == 'technical':
            for field in ('work_date', 'registration_number', 'metric', 'base_points'):
                if field in data:
                    setattr(work, field, data[field])

        work.save()

        if vr.work_type == 'scientific':
            pub_data = data.get('publication')
            if pub_data:
                pub = getattr(work, 'publication', None)
                if pub:
                    for f in ('title', 'year', 'pub_type'):
                        if f in pub_data:
                            setattr(pub, f, pub_data[f])
                    pub.save()
                    art_data = pub_data.get('article')
                    if art_data:
                        article = getattr(pub, 'article', None)
                        if article:
                            for f in ('journal', 'doi', 'quartile', 'is_scopus'):
                                if f in art_data:
                                    setattr(article, f, art_data[f])
                            article.save()
                    mono_data = pub_data.get('monograph')
                    if mono_data:
                        mono = getattr(pub, 'monograph', None)
                        if mono:
                            for f in ('publisher', 'isbn', 'pages_count'):
                                if f in mono_data:
                                    setattr(mono, f, mono_data[f])
                            mono.save()
            diss_data = data.get('dissertation')
            if diss_data:
                diss = getattr(work, 'dissertation', None)
                if diss:
                    for f in ('stage', 'defense_date'):
                        if f in diss_data:
                            setattr(diss, f, diss_data[f])
                    diss.save()
            proj_data = data.get('project')
            if proj_data:
                proj = getattr(work, 'project_participation', None)
                if proj:
                    for f in ('role', 'budget', 'start_date', 'end_date'):
                        if f in proj_data:
                            setattr(proj, f, proj_data[f])
                    proj.save()
            soft_data = data.get('software')
            if soft_data:
                soft = getattr(work, 'software', None)
                if soft:
                    for f in ('version', 'is_commercial'):
                        if f in soft_data:
                            setattr(soft, f, soft_data[f])
                    soft.save()

        if work.verified:
            from datetime import date
            now = date.today()
            quarter = (now.month - 1) // 3 + 1
            calculate_ipi(work.employee, now.year, quarter)

        return Response(VerificationRequestSerializer(vr).data)


# ============================================================
#  Научные работы
# ============================================================

def _transfer_task_attachments(task_id, work, fk_field):
    """Переносит прикреплённые файлы с задачи на новую работу."""
    if not task_id:
        return
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return
    for att in task.attachments.all():
        att.task = None
        setattr(att, fk_field, work)
        att.save()


class ScientificWorkViewSet(viewsets.ModelViewSet):
    queryset = ScientificWork.objects.select_related(
        'employee', 'verification_request',
        'publication__article', 'publication__monograph',
        'dissertation', 'project_participation', 'software',
    ).all()
    serializer_class = ScientificWorkSerializer

    def get_queryset(self):
        """Каждый видит только свои работы."""
        qs = super().get_queryset()
        if hasattr(self.request.user, 'employee'):
            qs = qs.filter(employee=self.request.user.employee)
        return qs

    def perform_create(self, serializer):
        work = serializer.save()
        employee = work.employee
        _transfer_task_attachments(
            self.request.data.get('source_task'), work, 'scientific_work',
        )
        # Руководитель/админ — работа сразу подтверждена
        if employee.role.role_name in ('руководитель', 'администратор'):
            work.verified = True
            work.save(update_fields=['verified'])
            # Сразу пересчитать IPI
            from datetime import date
            now = date.today()
            quarter = (now.month - 1) // 3 + 1
            calculate_ipi(employee, now.year, quarter)
        else:
            vr = VerificationRequest.objects.create(
                work_type='scientific',
                requester=employee,
            )
            work.verification_request = vr
            work.save(update_fields=['verification_request'])


# ============================================================
#  Организационные работы
# ============================================================

class OrganizationalWorkViewSet(viewsets.ModelViewSet):
    queryset = OrganizationalWork.objects.select_related('employee', 'verification_request').all()
    serializer_class = OrganizationalWorkSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'employee'):
            qs = qs.filter(employee=self.request.user.employee)
        return qs

    def perform_create(self, serializer):
        work = serializer.save()
        employee = work.employee
        _transfer_task_attachments(
            self.request.data.get('source_task'), work, 'organizational_work',
        )
        if employee.role.role_name in ('руководитель', 'администратор'):
            work.verified = True
            work.save(update_fields=['verified'])
            from datetime import date
            now = date.today()
            quarter = (now.month - 1) // 3 + 1
            calculate_ipi(employee, now.year, quarter)
        else:
            vr = VerificationRequest.objects.create(
                work_type='organizational',
                requester=employee,
            )
            work.verification_request = vr
            work.save(update_fields=['verification_request'])


# ============================================================
#  Технические работы
# ============================================================

class TechnicalWorkViewSet(viewsets.ModelViewSet):
    queryset = TechnicalWork.objects.select_related('employee', 'verification_request').all()
    serializer_class = TechnicalWorkSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request.user, 'employee'):
            qs = qs.filter(employee=self.request.user.employee)
        return qs

    def perform_create(self, serializer):
        work = serializer.save()
        employee = work.employee
        _transfer_task_attachments(
            self.request.data.get('source_task'), work, 'technical_work',
        )
        if employee.role.role_name in ('руководитель', 'администратор'):
            work.verified = True
            work.save(update_fields=['verified'])
            from datetime import date
            now = date.today()
            quarter = (now.month - 1) // 3 + 1
            calculate_ipi(employee, now.year, quarter)
        else:
            vr = VerificationRequest.objects.create(
                work_type='technical',
                requester=employee,
            )
            work.verification_request = vr
            work.save(update_fields=['verification_request'])


# ============================================================
#  KPI
# ============================================================

def _filter_by_user_department(qs, user, dept_field, request):
    """Сотрудник/руководитель видят только свой отдел; админ — все или с фильтром ?department=."""
    if not hasattr(user, 'employee'):
        return qs.none()
    role = user.employee.role.role_name
    if role == 'администратор':
        dept_param = request.query_params.get('department')
        if dept_param:
            return qs.filter(**{dept_field: dept_param})
        return qs
    return qs.filter(**{dept_field: user.employee.department_id})


class KPIGroupViewSet(viewsets.ModelViewSet):
    queryset = KPIGroup.objects.prefetch_related('indicators').all()
    serializer_class = KPIGroupSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return _filter_by_user_department(
            qs, self.request.user, 'department_id', self.request,
        )


class KPIIndicatorViewSet(viewsets.ModelViewSet):
    queryset = KPIIndicator.objects.select_related('kpi_group').all()
    serializer_class = KPIIndicatorSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return _filter_by_user_department(
            qs, self.request.user, 'kpi_group__department_id', self.request,
        )


class KPIGroupWeightViewSet(viewsets.ModelViewSet):
    queryset = KPIGroupWeight.objects.select_related('kpi_group').all()
    serializer_class = KPIGroupWeightSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = _filter_by_user_department(
            qs, self.request.user, 'kpi_group__department_id', self.request,
        )
        position_type = self.request.query_params.get('position_type')
        phd_year = self.request.query_params.get('phd_year')
        if position_type:
            qs = qs.filter(position_type=position_type)
        if phd_year is not None:
            if phd_year == '' or phd_year == 'null':
                qs = qs.filter(phd_year__isnull=True)
            else:
                qs = qs.filter(phd_year=phd_year)
        return qs

    @action(detail=False, methods=['post'])
    def upsert(self, request):
        """Создать или обновить вес группы по комбинации ключей."""
        kpi_group = request.data.get('kpi_group')
        position_type = request.data.get('position_type')
        phd_year = request.data.get('phd_year')
        weight = request.data.get('weight')
        if kpi_group is None or position_type is None or weight is None:
            return Response({'detail': 'kpi_group, position_type, weight обязательны'}, status=400)
        obj, _ = KPIGroupWeight.objects.update_or_create(
            kpi_group_id=kpi_group,
            position_type=position_type,
            phd_year=phd_year if phd_year not in (None, '', 'null') else None,
            defaults={'weight': float(weight)},
        )
        return Response(KPIGroupWeightSerializer(obj).data)


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
#  Проекты
# ============================================================

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('creator').prefetch_related('members__employee').all()

    def get_serializer_class(self):
        if self.action in ('retrieve',):
            return ProjectDetailSerializer
        return ProjectListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'employee'):
            # Видны проекты, где пользователь — создатель или участник
            qs = qs.filter(
                db_models.Q(creator=user.employee) |
                db_models.Q(members__employee=user.employee)
            ).distinct()
        return qs

    def perform_create(self, serializer):
        project = serializer.save(creator=self.request.user.employee)
        # Создатель автоматически становится участником
        ProjectMember.objects.create(project=project, employee=self.request.user.employee)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        project = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'detail': 'employee_id обязателен'}, status=400)
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'detail': 'Сотрудник не найден'}, status=404)
        member, created = ProjectMember.objects.get_or_create(project=project, employee=employee)
        if not created:
            return Response({'detail': 'Сотрудник уже участник проекта'}, status=400)
        return Response(ProjectMemberSerializer(member).data, status=201)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        project = self.get_object()
        employee_id = request.data.get('employee_id')
        try:
            member = ProjectMember.objects.get(project=project, employee_id=employee_id)
        except ProjectMember.DoesNotExist:
            return Response({'detail': 'Участник не найден'}, status=404)
        if member.employee == project.creator:
            return Response({'detail': 'Нельзя удалить создателя проекта'}, status=400)
        member.delete()
        return Response({'status': 'removed'})

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        _mark_overdue_tasks()
        project = self.get_object()
        tasks = Task.objects.filter(project=project).select_related('assigned_to', 'created_by').prefetch_related('attachments')
        return Response(TaskSerializer(tasks, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def complete_project(self, request, pk=None):
        """Завершение проекта с распределением баллов между участниками."""
        project = self.get_object()
        emp = request.user.employee

        if project.creator_id != emp.id and emp.role.role_name != 'администратор':
            return Response(
                {'detail': 'Завершить проект может только его создатель'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if project.completed_at is not None:
            return Response({'detail': 'Проект уже завершён'}, status=status.HTTP_400_BAD_REQUEST)

        kpi_group_id = request.data.get('kpi_group')
        work_type_key = request.data.get('work_type_key') or ''
        distribution = request.data.get('distribution') or {}

        try:
            kpi_group = KPIGroup.objects.get(id=kpi_group_id)
        except (KPIGroup.DoesNotExist, TypeError, ValueError):
            return Response({'detail': 'Группа показателей не найдена'}, status=400)

        kind = _work_kind_from_group(kpi_group)
        from datetime import date as _d
        today = _d.today()

        member_ids = set(project.members.values_list('employee_id', flat=True))
        created = []

        for raw_id, raw_points in distribution.items():
            try:
                member_id = int(raw_id)
                points = float(raw_points)
            except (TypeError, ValueError):
                continue
            if member_id not in member_ids or points <= 0:
                continue
            executor = Employee.objects.get(id=member_id)
            title = f'Проект «{project.name}»'
            if kind == 'scientific':
                work = ScientificWork.objects.create(
                    employee=executor, title=title, work_type=work_type_key,
                    points=points, verified=True,
                )
            elif kind == 'organizational':
                work = OrganizationalWork.objects.create(
                    employee=executor, title=title, work_type=work_type_key,
                    event_date=today, points=points, verified=True,
                )
            else:
                work = TechnicalWork.objects.create(
                    employee=executor, title=title, work_type=work_type_key,
                    work_date=today, points=points, verified=True,
                )
            created.append(work)

        project.completed_at = today
        project.save(update_fields=['completed_at'])

        # Пересчёт IPI для каждого получателя баллов за квартал работы
        quarter = (today.month - 1) // 3 + 1
        for work in created:
            calculate_ipi(work.employee, today.year, quarter)

        return Response({
            'status': 'completed',
            'completed_at': today.isoformat(),
            'works_created': len(created),
        })


# ============================================================
#  Задачи
# ============================================================

def _mark_overdue_tasks():
    """Перевести все непросроченные задачи, у которых истёк дедлайн, в статус 'overdue'."""
    from datetime import date
    Task.objects.filter(
        deadline__lt=date.today(),
    ).exclude(
        status__in=('completed', 'overdue'),
    ).update(status='overdue')


def _work_kind_from_group(kpi_group):
    """Определяет тип работы по имени группы показателей."""
    if not kpi_group:
        return 'scientific'
    name_lower = kpi_group.name.lower()
    if 'науч' in name_lower:
        return 'scientific'
    if 'организ' in name_lower:
        return 'organizational'
    if 'техн' in name_lower:
        return 'technical'
    return 'scientific'


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('assigned_to', 'created_by', 'project').prefetch_related('attachments').all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        _mark_overdue_tasks()
        qs = super().get_queryset()
        user = self.request.user
        if not hasattr(user, 'employee'):
            return qs.none()
        emp = user.employee
        role = emp.role.role_name

        if role == 'администратор':
            return qs

        if role == 'руководитель':
            dept = emp.department
            qs = qs.filter(
                db_models.Q(created_by__department=dept) |
                db_models.Q(assigned_to__department=dept) |
                db_models.Q(project__creator__department=dept)
            ).distinct()
            return qs

        # Роль «сотрудник»
        proj_q = (
            db_models.Q(project__members__employee=emp) |
            db_models.Q(project__creator=emp)
        )
        my_free_q = db_models.Q(project__isnull=True, assigned_to=emp)
        pool_free_q = db_models.Q(
            project__isnull=True,
            assigned_to__isnull=True,
            created_by__department=emp.department,
        )
        return qs.filter(proj_q | my_free_q | pool_free_q).distinct()

    def perform_create(self, serializer):
        emp = getattr(self.request.user, 'employee', None)
        if emp is None:
            raise serializers.ValidationError('Требуется авторизация')

        project = serializer.validated_data.get('project')
        role = emp.role.role_name

        # Свободные задачи (без проекта) — только руководитель/админ
        if project is None and role == 'сотрудник':
            raise serializers.ValidationError({
                'project': 'Сотрудники могут создавать задачи только внутри собственных проектов',
            })

        # Проектные задачи — только создатель проекта (или администратор)
        if project is not None and role != 'администратор' and project.creator != emp:
            raise serializers.ValidationError({
                'project': 'Задачи в проекте может создавать только его создатель',
            })

        serializer.save(created_by=emp)

    @action(detail=True, methods=['post'])
    def take(self, request, pk=None):
        task = self.get_object()
        if task.assigned_to is not None:
            return Response({'detail': 'Задача уже назначена'}, status=status.HTTP_400_BAD_REQUEST)
        emp = request.user.employee
        # Свободную задачу в пуле может взять сотрудник того же подразделения
        if task.project is None and task.created_by and task.created_by.department_id != emp.department_id:
            return Response(
                {'detail': 'Задача доступна только сотрудникам подразделения создателя'},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Проектную задачу может взять только участник проекта
        if task.project is not None and not task.project.members.filter(employee=emp).exists():
            return Response(
                {'detail': 'Только участники проекта могут взять задачу'},
                status=status.HTTP_403_FORBIDDEN,
            )
        task.assigned_to = emp
        task.status = 'assigned'
        task.save()
        return Response(TaskSerializer(task, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        task = self.get_object()
        task.status = 'in_progress'
        task.save()
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        if task.status == 'completed':
            return Response({'detail': 'Задача уже завершена'}, status=status.HTTP_400_BAD_REQUEST)
        task.status = 'completed'
        task.save()
        return Response(TaskSerializer(task, context={'request': request}).data)


# ============================================================
#  Вложения (файлы)
# ============================================================

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.select_related('uploaded_by').all()
    serializer_class = AttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        # Фильтры: к какой сущности прикреплены файлы
        for param in ('scientific_work', 'organizational_work', 'technical_work', 'task'):
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{param: value})
        return qs

    def perform_create(self, serializer):
        upload = self.request.data.get('file')
        if not upload:
            raise serializers.ValidationError({'file': 'Файл обязателен'})
        employee = getattr(self.request.user, 'employee', None)
        serializer.save(
            uploaded_by=employee,
            original_name=getattr(upload, 'name', ''),
            size=getattr(upload, 'size', 0),
        )


# ============================================================
#  IPI расчёт
# ============================================================

@api_view(['POST'])
def calculate_ipi_view(request):
    """Рассчитать IPI для сотрудника за указанный период."""
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
    """Пересчитать IPI для всех сотрудников за указанный период."""
    year = request.data.get('year')
    quarter = request.data.get('quarter')
    results = recalculate_all(
        year=int(year) if year else None,
        quarter=int(quarter) if quarter else None,
    )
    return Response(KPIResultSerializer(results, many=True).data)


@api_view(['GET'])
def ipi_breakdown_view(request):
    """Полная разбивка IPI по формуле для интерфейса."""
    from datetime import date as _d
    employee_id = request.query_params.get('employee_id') or (
        request.user.employee.id if hasattr(request.user, 'employee') else None
    )
    if not employee_id:
        return Response({'detail': 'employee_id обязателен'}, status=400)
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'detail': 'Сотрудник не найден'}, status=404)

    today = _d.today()
    year = int(request.query_params.get('year') or today.year)
    quarter = int(request.query_params.get('quarter') or ((today.month - 1) // 3 + 1))

    breakdown = calculate_breakdown(employee, year, quarter)
    return Response(breakdown)


@api_view(['GET'])
def department_employee_detail_view(request, employee_id):
    """Детальные данные сотрудника: работы, задачи, проекты за период."""
    from datetime import date as _d
    user = request.user
    if not hasattr(user, 'employee'):
        return Response({'detail': 'Только для сотрудников'}, status=403)
    me = user.employee
    if me.role.role_name not in ('руководитель', 'администратор'):
        return Response({'detail': 'Только для руководителя/админа'}, status=403)
    try:
        emp = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'detail': 'Сотрудник не найден'}, status=404)
    if me.role.role_name == 'руководитель' and emp.department_id != me.department_id:
        return Response({'detail': 'Сотрудник из другого подразделения'}, status=403)

    today = _d.today()
    period = request.query_params.get('period', 'quarter')
    year = int(request.query_params.get('year') or today.year)

    if period == 'month':
        month = int(request.query_params.get('month') or today.month)
        start_date = _d(year, month, 1)
        end_date = _d(year, 12, 31) if month == 12 else _d(year, month + 1, 1)
    elif period == 'year':
        start_date = _d(year, 1, 1)
        end_date = _d(year, 12, 31)
    else:
        quarter = int(request.query_params.get('quarter') or ((today.month - 1) // 3 + 1))
        q_start_month = (quarter - 1) * 3 + 1
        start_date = _d(year, q_start_month, 1)
        end_date = _d(year, quarter * 3, 28) if quarter * 3 != 12 else _d(year, 12, 31)

    sci = ScientificWork.objects.filter(
        employee=emp, created_at__date__gte=start_date, created_at__date__lte=end_date,
    )
    org = OrganizationalWork.objects.filter(
        employee=emp, event_date__gte=start_date, event_date__lte=end_date,
    )
    tech = TechnicalWork.objects.filter(
        employee=emp, work_date__gte=start_date, work_date__lte=end_date,
    )

    works = []
    for w in sci:
        works.append({
            'id': w.id, 'kind': 'scientific', 'category': 'Научная',
            'title': w.title, 'work_type': w.work_type,
            'points': w.points, 'verified': w.verified,
            'date': str(w.created_at.date()) if w.created_at else None,
        })
    for w in org:
        works.append({
            'id': w.id, 'kind': 'organizational', 'category': 'Организационная',
            'title': w.title, 'work_type': w.work_type,
            'points': w.points, 'verified': w.verified,
            'date': str(w.event_date) if w.event_date else None,
        })
    for w in tech:
        works.append({
            'id': w.id, 'kind': 'technical', 'category': 'Техническая',
            'title': w.title, 'work_type': w.work_type,
            'points': w.points, 'verified': w.verified,
            'date': str(w.work_date) if w.work_date else None,
        })

    tasks_qs = Task.objects.filter(
        assigned_to=emp,
        deadline__gte=start_date, deadline__lte=end_date,
    ).select_related('project')
    tasks = [{
        'id': t.id, 'title': t.title,
        'status': t.status, 'priority': t.priority, 'deadline': str(t.deadline),
        'project_id': t.project_id, 'project_name': t.project.name if t.project else None,
        'points': t.points,
    } for t in tasks_qs]

    projects = list(Project.objects.filter(
        members__employee=emp,
    ).distinct().values('id', 'name', 'start_date', 'end_date', 'completed_at'))
    for p in projects:
        p['start_date'] = str(p['start_date']) if p['start_date'] else None
        p['end_date'] = str(p['end_date']) if p['end_date'] else None
        p['completed_at'] = str(p['completed_at']) if p['completed_at'] else None

    return Response({
        'employee_id': emp.id,
        'full_name': emp.full_name,
        'works': works,
        'tasks': tasks,
        'tasks_completed': sum(1 for t in tasks if t['status'] == 'completed'),
        'tasks_overdue': sum(1 for t in tasks if t['status'] == 'overdue'),
        'projects': projects,
    })


@api_view(['GET'])
def department_stats_view(request):
    """Сводная статистика по сотрудникам подразделения."""
    from datetime import date as _d
    user = request.user
    if not hasattr(user, 'employee'):
        return Response({'detail': 'Только для сотрудников'}, status=403)
    emp = user.employee
    if emp.role.role_name not in ('руководитель', 'администратор'):
        return Response({'detail': 'Только для руководителя/админа'}, status=403)

    today = _d.today()
    period = request.query_params.get('period', 'quarter')  # month/quarter/year
    year = int(request.query_params.get('year') or today.year)

    if period == 'month':
        month = int(request.query_params.get('month') or today.month)
        start_date = _d(year, month, 1)
        if month == 12:
            end_date = _d(year, 12, 31)
        else:
            end_date = _d(year, month + 1, 1)
        # IPI сохраняется поквартально, для отображения берём квартал, в который попадает месяц
        ipi_quarter = (month - 1) // 3 + 1
    elif period == 'year':
        start_date = _d(year, 1, 1)
        end_date = _d(year, 12, 31)
        ipi_quarter = (today.month - 1) // 3 + 1 if today.year == year else 4
    else:  # quarter
        quarter = int(request.query_params.get('quarter') or ((today.month - 1) // 3 + 1))
        q_start_month = (quarter - 1) * 3 + 1
        start_date = _d(year, q_start_month, 1)
        end_date = _d(year, quarter * 3, 28) if quarter * 3 != 12 else _d(year, 12, 31)
        ipi_quarter = quarter

    employees = Employee.objects.filter(department=emp.department).select_related('role')

    rows = []
    for e in employees:
        # Работы за период
        sci = ScientificWork.objects.filter(
            employee=e, created_at__date__gte=start_date, created_at__date__lte=end_date,
        )
        org = OrganizationalWork.objects.filter(
            employee=e, event_date__gte=start_date, event_date__lte=end_date,
        )
        tech = TechnicalWork.objects.filter(
            employee=e, work_date__gte=start_date, work_date__lte=end_date,
        )
        works_total = sci.count() + org.count() + tech.count()
        works_verified = sci.filter(verified=True).count() + \
            org.filter(verified=True).count() + tech.filter(verified=True).count()
        works_pending = works_total - works_verified

        # Задачи за период (по дедлайну)
        tasks_qs = Task.objects.filter(
            assigned_to=e, deadline__gte=start_date, deadline__lte=end_date,
        )
        tasks_total = tasks_qs.count()
        tasks_completed = tasks_qs.filter(status='completed').count()
        tasks_overdue = tasks_qs.filter(status='overdue').count()

        projects_count = ProjectMember.objects.filter(employee=e).count()

        # IPI за квартал
        ipi_obj = KPIResult.objects.filter(employee=e, year=year, quarter=ipi_quarter).first()
        total_ipi = ipi_obj.total_ipi if ipi_obj else 0

        rows.append({
            'employee_id': e.id,
            'full_name': e.full_name,
            'position': e.position,
            'position_type': e.position_type,
            'phd_year': e.phd_year,
            'works_total': works_total,
            'works_verified': works_verified,
            'works_pending': works_pending,
            'tasks_total': tasks_total,
            'tasks_completed': tasks_completed,
            'tasks_overdue': tasks_overdue,
            'projects_count': projects_count,
            'total_ipi': round(total_ipi, 2),
            'activity_score': works_verified * 2 + tasks_completed - tasks_overdue,
        })

    rows.sort(key=lambda r: r['activity_score'], reverse=True)

    return Response({
        'period': period,
        'year': year,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'rows': rows,
    })


# ============================================================
#  Экспорт отчётов (Excel/Word) — plain Django views
# ============================================================

from django.http import HttpResponse, JsonResponse
from urllib.parse import quote
from rest_framework_simplejwt.authentication import JWTAuthentication
from .report_builder import build_department_report, build_employee_report, resolve_period
from .report_excel import render_department_excel, render_employee_excel
from .report_word import render_department_word, render_employee_word


XLSX_CT = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
DOCX_CT = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


def _attach_filename(response, filename):
    quoted = quote(filename)
    response['Content-Disposition'] = (
        f"attachment; filename=\"{quoted}\"; filename*=UTF-8''{quoted}"
    )


def _authenticate_jwt(request):
    """JWT-аутентификация. Возвращает Employee или (None, JsonResponse-с-ошибкой)."""
    auth = JWTAuthentication()
    try:
        result = auth.authenticate(request)
    except Exception as e:
        return None, JsonResponse({'detail': f'Ошибка токена: {e}'}, status=401)
    if result is None:
        return None, JsonResponse({'detail': 'Требуется авторизация'}, status=401)
    user, _ = result
    if not hasattr(user, 'employee'):
        return None, JsonResponse({'detail': 'Нет связанного сотрудника'}, status=403)
    return user.employee, None


def _parse_period_params(request):
    from datetime import date as _d
    period = request.GET.get('period', 'quarter')
    today = _d.today()
    year = int(request.GET.get('year') or today.year)
    month_p = request.GET.get('month')
    quarter_p = request.GET.get('quarter')
    month = int(month_p) if month_p else None
    quarter = int(quarter_p) if quarter_p else None
    fmt = (request.GET.get('format') or 'excel').lower()
    return period, year, month, quarter, fmt


def department_report_view(request):
    emp, err = _authenticate_jwt(request)
    if err:
        return err
    if emp.role.role_name not in ('руководитель', 'администратор'):
        return JsonResponse({'detail': 'Только для руководителя/админа'}, status=403)

    period, year, month, quarter, fmt = _parse_period_params(request)
    department = emp.department

    try:
        data = build_department_report(department, period, year,
                                        month=month, quarter=quarter)
    except ValueError as e:
        return JsonResponse({'detail': str(e)}, status=400)

    period_label = data['period']['label']
    base = f'Отчёт_{department.department_short_name}_{period_label}'

    if fmt == 'word':
        content = render_department_word(data)
        resp = HttpResponse(content, content_type=DOCX_CT)
        _attach_filename(resp, f'{base}.docx')
        return resp
    else:
        content = render_department_excel(data)
        resp = HttpResponse(content, content_type=XLSX_CT)
        _attach_filename(resp, f'{base}.xlsx')
        return resp


def employee_report_view(request, employee_id):
    requester, err = _authenticate_jwt(request)
    if err:
        return err

    try:
        target = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({'detail': 'Сотрудник не найден'}, status=404)

    role = requester.role.role_name
    is_owner = requester.id == target.id
    is_dept_manager = (role in ('руководитель', 'администратор')
                      and requester.department_id == target.department_id)
    is_admin = role == 'администратор'
    if not (is_owner or is_dept_manager or is_admin):
        return JsonResponse({'detail': 'Нет доступа'}, status=403)

    period, year, month, quarter, fmt = _parse_period_params(request)

    try:
        start, end, period_label = resolve_period(period, year,
                                                   month=month, quarter=quarter)
    except ValueError as e:
        return JsonResponse({'detail': str(e)}, status=400)

    from datetime import date as _date
    emp_data = build_employee_report(target, start, end, period, year,
                                      quarter=quarter, month=month)
    generated_at = _date.today()
    base = f'Отчёт_{target.full_name}_{period_label}'

    if fmt == 'word':
        content = render_employee_word(emp_data, target.department.department_short_name,
                                         period_label, generated_at)
        resp = HttpResponse(content, content_type=DOCX_CT)
        _attach_filename(resp, f'{base}.docx')
        return resp
    else:
        content = render_employee_excel(emp_data, target.department.department_short_name,
                                          period_label, generated_at)
        resp = HttpResponse(content, content_type=XLSX_CT)
        _attach_filename(resp, f'{base}.xlsx')
        return resp
