from django.contrib import admin
from .models import (
    Department, UserRole, Employee,
    VerificationRequest,
    ScientificWork, Publication, Article, Monograph,
    Dissertation, ProjectParticipation, Software,
    OrganizationalWork, TechnicalWork,
    KPIGroup, KPIIndicator, KPIResult,
    Project, ProjectMember,
    Task, Rule,
)


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['rule_type', 'description', 'min_value', 'max_value', 'coefficient', 'priority']
    list_filter = ['rule_type']
    list_editable = ['coefficient', 'priority']
    ordering = ['rule_type', 'priority']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'department_name', 'department_short_name']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'role_name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'position', 'position_type', 'department', 'role']
    list_filter = ['department', 'role', 'position_type']
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
    list_display = ['id', 'name', 'group_weight', 'department']


class KPIIndicatorInline(admin.TabularInline):
    model = KPIIndicator
    extra = 1


@admin.register(KPIIndicator)
class KPIIndicatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'kpi_group', 'name', 'work_type_key', 'weight']
    list_filter = ['kpi_group']


@admin.register(KPIResult)
class KPIResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'year', 'quarter', 'total_ipi', 'created_at']
    list_filter = ['year', 'quarter']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'budget', 'start_date', 'end_date', 'creator']


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'employee', 'joined_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'priority', 'deadline', 'assigned_to', 'created_by', 'project']
    list_filter = ['status', 'priority']
