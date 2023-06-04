import datetime
import numpy as np
import pandas as pd
from ..models import Employee
from django.http import JsonResponse, HttpResponseServerError


def avg_industry_age(request):
    # TODO add validation for NaN
    try:
        df = pd.DataFrame(Employee.objects.all().values())
        df['age'] = (datetime.datetime.now() - pd.to_datetime(df['date_of_birth'], format='%Y-%m-%d')).apply(lambda d: d.days//365)
        stats = df.groupby(['industry'])['age'].mean().to_dict()
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistic.')
    return JsonResponse(stats)


def avg_industry_salary(request):
    # TODO add validation for NaN
    try:
        df = pd.DataFrame(Employee.objects.all().values())
        stats = df.groupby(['industry'])['salary'].mean().to_dict()
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistic.')
    return JsonResponse(stats)


def avg_experience_salary(request):
    # TODO add binning
    try:
        df = pd.DataFrame(Employee.objects.all().values())
        stats = df.groupby(['years_of_experience'])['salary'].mean().to_dict()
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistic.')
    return JsonResponse(stats)


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
        stats['median_gender_salary'] = df.groupby(['gender'])['salary'].median().to_dict()

        df['zodiac_sign'] = pd.to_datetime(df['date_of_birth'], format='%Y-%m-%d').apply(lambda d: get_sign(d.month, d.day))
        stats['median_zodiac_sign_salary_descending'] = sorted([(k, v) for k, v in df.groupby(['zodiac_sign'])['salary'].median().to_dict().items()],
            key=lambda tup: tup[1], reverse=True)
    except Exception as ex:
        return HttpResponseServerError('Unexpected error. Could not compute statistics.')
    return JsonResponse(stats)


def get_sign(month, day):
    astro_sign = 'unknown'
    if month == 12:
        astro_sign = 'sagittarius' if (day < 22) else 'capricorn'
    elif month == 1:
        astro_sign = 'capricorn' if (day < 20) else 'aquarius'
    elif month == 2:
        astro_sign = 'aquarius' if (day < 19) else 'pisces'
    elif month == 3:
        astro_sign = 'pisces' if (day < 21) else 'aries'
    elif month == 4:
        astro_sign = 'aries' if (day < 20) else 'taurus'
    elif month == 5:
        astro_sign = 'taurus' if (day < 21) else 'gemini'
    elif month == 6:
        astro_sign = 'gemini' if (day < 21) else 'cancer'
    elif month == 7:
        astro_sign = 'cancer' if (day < 23) else 'leo'
    elif month == 8:
        astro_sign = 'leo' if (day < 23) else 'virgo'
    elif month == 9:
        astro_sign = 'virgo' if (day < 23) else 'libra'
    elif month == 10:
        astro_sign = 'libra' if (day < 23) else 'scorpio'
    elif month == 11:
        astro_sign = 'scorpio' if (day < 22) else 'sagittarius'
    return astro_sign