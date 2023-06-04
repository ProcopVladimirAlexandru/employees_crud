from django.urls import path

from .views import employees_view
from .views import statistics

urlpatterns = [
    path("employees", employees_view.EmployeeView.as_view(), name="crud_employee"),
    path("interesting_statistics", statistics.interesting_statistics, name="get_interesting_statistics"),
    path("avg_industry_age", statistics.avg_industry_age, name="get_avg_industry_age"),
    path("avg_industry_salary", statistics.avg_industry_salary, name="get_avg_industry_salary"),
    path("avg_experience_salary", statistics.avg_experience_salary, name="get_avg_experience_salary"),
]