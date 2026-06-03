from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'roles', views.UserRoleViewSet)
router.register(r'employees', views.EmployeeViewSet)
router.register(r'verification-requests', views.VerificationRequestViewSet)
router.register(r'scientific-works', views.ScientificWorkViewSet)
router.register(r'organizational-works', views.OrganizationalWorkViewSet)
router.register(r'technical-works', views.TechnicalWorkViewSet)
router.register(r'kpi-groups', views.KPIGroupViewSet)
router.register(r'kpi-indicators', views.KPIIndicatorViewSet)
router.register(r'kpi-group-weights', views.KPIGroupWeightViewSet)
router.register(r'kpi-results', views.KPIResultViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'attachments', views.AttachmentViewSet)

urlpatterns = [
    # Auth
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.me_view, name='me'),

    # IPI calculation
    path('ipi/calculate/', views.calculate_ipi_view, name='calculate_ipi'),
    path('ipi/recalculate-all/', views.recalculate_all_view, name='recalculate_all'),
    path('ipi/breakdown/', views.ipi_breakdown_view, name='ipi_breakdown'),

    # Department stats (для «Мой отдел»)
    path('department/stats/', views.department_stats_view, name='department_stats'),
    path('department/employee/<int:employee_id>/details/', views.department_employee_detail_view, name='department_employee_detail'),

    # Экспорт отчётов
    path('department/report/', views.department_report_view, name='department_report'),
    path('department/employee/<int:employee_id>/report/', views.employee_report_view, name='employee_report'),

    # CRUD
    path('', include(router.urls)),
]
