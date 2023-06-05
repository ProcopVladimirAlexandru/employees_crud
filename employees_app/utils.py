import json
from django.core.exceptions import ValidationError
from django.http import (HttpResponseBadRequest, HttpResponseServerError)


def check_json(request):
    if 'Content-Type' not in request.headers:
        return HttpResponseBadRequest('Missing Content-Type header.')
    if request.headers['Content-Type'] != 'application/json':
        return HttpResponseBadRequest('Expected Content-Type application/json.')
    return


def parse_json(request):
    try:
        obj = json.loads(request.body)
    except Exception as ex:
        return False, HttpResponseBadRequest('Could not parse body as JSON.')
    return True, obj


def validate_model_object(obj):
    try:
        obj.full_clean()
    except ValidationError as ex:
        return HttpResponseBadRequest(str(ex))
    except Exception as ex:
        return HttpResponseServerError('Unexpected error during validation.')
    return


def get_zodiac_sign(month, day):
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
