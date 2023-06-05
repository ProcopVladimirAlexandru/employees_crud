import datetime
import numpy as np
import pandas as pd
from ..models import Employee
from ..utils import get_zodiac_sign
from django.http import JsonResponse, HttpResponseServerError


def avg_industry_age(request):
    # TODO add validation for NaN
    try:
        df = pd.DataFrame(Employee.objects.all().values())
        df['age'] = (datetime.datetime.now() - pd.to_datetime(df['date_of_birth'], format='%Y-%m-%d')).apply(lambda d: d.days//365)
        stats_dict = df.groupby(['industry'])['age'].mean().to_dict()
        stats_list = [ { 'industry': k, 'average_age': v } for k, v in stats_dict.items() ]
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistic.')
    return JsonResponse({'statistics': stats_list})


def avg_industry_salary(request):
    # TODO add validation for NaN
    try:
        df = pd.DataFrame(Employee.objects.all().values())
        stats_dict = df.groupby(['industry'])['salary'].mean().to_dict()
        stats_list = [{'industry': k, 'average_salary': v} for k, v in stats_dict.items()]
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistic.')
    return JsonResponse({'statistics': stats_list})


def avg_experience_salary(request):
    # TODO add binning
    try:
        df = pd.DataFrame(Employee.objects.all().values())
        stats_dict = df.groupby(['years_of_experience'])['salary'].mean().to_dict()
        stats_list = [{'years_of_experience': k, 'average_salary': v} for k, v in stats_dict.items()]
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistic.')
    return JsonResponse({'statistics': stats_list})


def interesting_statistics(request):
    # TODO better error handling. This is too vague.
    try:
        df = pd.DataFrame(Employee.objects.all().values())
        df['age'] = (datetime.datetime.now() - pd.to_datetime(df['date_of_birth'], format='%Y-%m-%d')).apply(
            lambda d: d.days // 365)
        stats = dict()
        df_age_salary_corr = df[['age', 'salary']].dropna()
        stats['age_salary_corr'] = np.corrcoef(df_age_salary_corr['age'].dropna(),
                                               df_age_salary_corr['salary'].dropna())[0,1]

        # TODO address missing values better
        temp_dict = df.groupby(['gender'])['salary'].median().to_dict()
        stats['median_gender_salary'] = [{'gender': k, 'median_salary': v} for k, v in temp_dict.items()]

        df['zodiac_sign'] = pd.to_datetime(df['date_of_birth'], format='%Y-%m-%d').apply(lambda d: get_zodiac_sign(d.month, d.day))
        zodiac_sign_tups = sorted([(k, v) for k, v in df.groupby(['zodiac_sign'])['salary'].median().to_dict().items()],
            key=lambda tup: tup[1], reverse=True)
        stats['median_zodiac_sign_salary_descending'] = [ {'zodiac_sign': tup[0], 'median_salary': tup[1]}
                                                          for tup in zodiac_sign_tups ]
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistics.')
    return JsonResponse({'statistics': stats})
