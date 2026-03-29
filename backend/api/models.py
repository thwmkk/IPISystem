from django.db import models


class Department(models.Model):
    department_name = models.CharField(max_length=300)
    department_short_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'department'


class UserRole(models.Model):
    role_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'user_role'


class Employee(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=120, unique=True)
    position = models.CharField(max_length=50)
    age = models.IntegerField()
    experience = models.IntegerField()
    is_phd_student = models.BooleanField(default=False)
    academic_degree = models.CharField(max_length=50, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT)

    class Meta:
        db_table = 'employee'