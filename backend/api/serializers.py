from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Department, UserRole, Employee,
    VerificationRequest,
    ScientificWork, Publication, Article, Monograph,
    Dissertation, ProjectParticipation, Software,
    OrganizationalWork, TechnicalWork,
    KPIGroup, KPIWeight, KPIResult,
    Task,
)


# ============================================================
#  Auth
# ============================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


# ============================================================
#  Справочники
# ============================================================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'


# ============================================================
#  Сотрудник
# ============================================================

class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_short_name', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'email', 'position', 'age',
            'experience', 'is_phd_student', 'academic_degree',
            'department', 'department_name', 'role', 'role_name',
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    role = UserRoleSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True
    )
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(), source='role', write_only=True
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'email', 'position', 'age',
            'experience', 'is_phd_student', 'academic_degree',
            'department', 'department_id', 'role', 'role_id',
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Used by manager/admin to create employee and send credentials."""

    class Meta:
        model = Employee
        fields = [
            'full_name', 'email', 'position', 'age',
            'experience', 'is_phd_student', 'academic_degree',
            'department', 'role',
        ]


# ============================================================
#  Верификация
# ============================================================

class VerificationRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.full_name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.full_name', read_only=True)

    class Meta:
        model = VerificationRequest
        fields = '__all__'
        read_only_fields = ['request_date']


# ============================================================
#  Научные работы
# ============================================================

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ['id']


class MonographSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monograph
        exclude = ['id']


class PublicationSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(required=False)
    monograph = MonographSerializer(required=False)

    class Meta:
        model = Publication
        exclude = ['scientific_work']


class DissertationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dissertation
        exclude = ['scientific_work']


class ProjectParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectParticipation
        exclude = ['scientific_work']


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        exclude = ['scientific_work']


class ScientificWorkSerializer(serializers.ModelSerializer):
    publication = PublicationSerializer(required=False)
    dissertation = DissertationSerializer(required=False)
    project_participation = ProjectParticipationSerializer(required=False)
    software = SoftwareSerializer(required=False)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = ScientificWork
        fields = '__all__'
        read_only_fields = ['verified', 'verification_request', 'created_at']


# ============================================================
#  Организационные работы
# ============================================================

class OrganizationalWorkSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = OrganizationalWork
        fields = '__all__'
        read_only_fields = ['verified', 'verification_request', 'created_at']


# ============================================================
#  Технические работы
# ============================================================

class TechnicalWorkSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = TechnicalWork
        fields = '__all__'
        read_only_fields = ['verified', 'verification_request', 'created_at']


# ============================================================
#  KPI
# ============================================================

class KPIGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIGroup
        fields = '__all__'


class KPIWeightSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='kpi_group.name', read_only=True)

    class Meta:
        model = KPIWeight
        fields = '__all__'


class KPIResultSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = KPIResult
        fields = '__all__'
        read_only_fields = ['created_at']


# ============================================================
#  Задачи
# ============================================================

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True, default=None)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at']
