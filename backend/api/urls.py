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
router.register(r'kpi-weights', views.KPIWeightViewSet)
router.register(r'kpi-results', views.KPIResultViewSet)
router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    # Auth
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.me_view, name='me'),

    # IPI calculation
    path('ipi/calculate/', views.calculate_ipi_view, name='calculate_ipi'),
    path('ipi/recalculate-all/', views.recalculate_all_view, name='recalculate_all'),

    # Rule Engine
    path('weights/preview/<int:employee_id>/', views.preview_weights_view, name='preview_weights'),
    path('weights/assign/<int:employee_id>/', views.assign_weights_view, name='assign_weights'),
    path('weights/assign-all/', views.assign_weights_all_view, name='assign_weights_all'),

    # CRUD
    path('', include(router.urls)),
]
