from django.contrib import admin
from .models import (
    Department, UserRole, Employee,
    VerificationRequest,
    ScientificWork, Publication, Article, Monograph,
    Dissertation, ProjectParticipation, Software,
    OrganizationalWork, TechnicalWork,
    KPIGroup, KPIWeight, KPIResult,
    Task,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'department_name', 'department_short_name']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'role_name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'position', 'department', 'role']
    list_filter = ['department', 'role', 'is_phd_student']
    search_fields = ['full_name', 'email']


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'work_type', 'status', 'requester', 'evaluator', 'request_date']
    list_filter = ['status', 'work_type']


@admin.register(ScientificWork)
class ScientificWorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'work_type', 'points', 'verified', 'employee']
    list_filter = ['work_type', 'verified']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'year', 'pub_type']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'journal', 'doi', 'quartile', 'is_scopus']


@admin.register(Monograph)
class MonographAdmin(admin.ModelAdmin):
    list_display = ['id', 'publisher', 'isbn', 'pages_count']


@admin.register(Dissertation)
class DissertationAdmin(admin.ModelAdmin):
    list_display = ['id', 'stage', 'defense_date']


@admin.register(ProjectParticipation)
class ProjectParticipationAdmin(admin.ModelAdmin):
    list_display = ['id', 'role', 'budget', 'start_date', 'end_date']


@admin.register(Software)
class SoftwareAdmin(admin.ModelAdmin):
    list_display = ['id', 'version', 'is_commercial']


@admin.register(OrganizationalWork)
class OrganizationalWorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'work_type', 'points', 'verified', 'employee']
    list_filter = ['work_type', 'verified']


@admin.register(TechnicalWork)
class TechnicalWorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'points', 'verified', 'employee']
    list_filter = ['verified']


@admin.register(KPIGroup)
class KPIGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'metric_group', 'base_points', 'department']


@admin.register(KPIWeight)
class KPIWeightAdmin(admin.ModelAdmin):
    list_display = ['id', 'kpi_group', 'position', 'group_weight', 'weight']
    list_filter = ['position']


@admin.register(KPIResult)
class KPIResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'year', 'quarter', 'total_ipi', 'created_at']
    list_filter = ['year', 'quarter']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'priority', 'deadline', 'assigned_to', 'created_by']
    list_filter = ['status', 'priority']
