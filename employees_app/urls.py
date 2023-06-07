from django.urls import path

from .views import employees_view
from .views import statistics_views

urlpatterns = [
    path("employees", employees_view.EmployeeView.as_view(), name="crud_employee"),
    path("interesting_statistics", statistics_views.interesting_statistics, name="get_interesting_statistics"),
    path("avg_industry_age", statistics_views.avg_industry_age, name="get_avg_industry_age"),
    path("avg_industry_salary", statistics_views.avg_industry_salary, name="get_avg_industry_salary"),
    path("avg_experience_salary", statistics_views.avg_experience_salary, name="get_avg_experience_salary"),
]