import json
import logging
import datetime
from ..models import Employee
from django.views import View
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import (JsonResponse,
                         HttpResponseBadRequest, HttpResponseServerError,
                         HttpResponseNotFound, HttpResponse)


# TODO configure logger at Django project level in settings.py
LOGGER_LEVEL = logging.DEBUG
LOGGER_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, level=LOGGER_LEVEL)


class EmployeeView(View):
    LOGGER_NAME = 'employee_view_logger'
    INPUT_DATE_FORMAT = '%d/%m/%Y'
    DB_DATE_FORMAT = '%Y-%m-%d'
    DEFAULT_PAGE_SIZE = 10
    DEFAULT_PAGE_NUMBER = 1
    DEFAULT_ORDER_BY = 'id'
    DEFAULT_ORDER = 'ascending'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(EmployeeView.LOGGER_NAME)

    def post(self, request):
        error_response = Utils.check_json(request)
        if error_response:
            self._logger.error(error_response.content.decode())
            return error_response

        success, parse_result = Utils.parse_json(request)
        if not success:
            self._logger.error(parse_result.content.decode())
            return parse_result

        try:
            employee = Employee(**parse_result)
        except Exception as ex:
            err_msg = 'Could not parse body as Employee.'
            self._logger.error(f'{err_msg}. Error: {ex}', exc_info=True)
            return HttpResponseBadRequest(err_msg)

        error_response = EmployeeView.validate_employee(employee)
        if error_response:
            self._logger.error(error_response.content.decode())
            return error_response

        employee.save()
        return JsonResponse(model_to_dict(employee))

    def delete(self, request):
        _id = request.GET.get('id', None)
        if not _id:
            err_msg = 'Specify "id" query parameter.'
            self._logger.error(err_msg)
            return HttpResponseBadRequest(err_msg)

        try:
            employee = Employee.objects.get(pk=_id)
            employee.delete()
        except ObjectDoesNotExist as ex:
            err_msg = 'Could not find employee.'
            self._logger.error(f'{err_msg}. Error: {ex}', exc_info=True)
            return HttpResponseNotFound(err_msg)
        except Exception as ex:
            err_msg = 'Unexpected error. Could not delete.'
            self._logger.error(f'{err_msg}. Error: {ex}', exc_info=True)
            return HttpResponseServerError(err_msg)
        return JsonResponse({'deleted': True, 'id': _id})

    def get(self, request):
        _id = request.GET.get('id', None)
        if _id:
            # get one
            try:
                return JsonResponse(model_to_dict(Employee.objects.get(pk=_id)))
            except ObjectDoesNotExist as ex:
                err_msg = 'Could not find employee.'
                self._logger.error(f'{err_msg}. Error: {ex}', exc_info=True)
                return HttpResponseNotFound(err_msg)
            except Exception as ex:
                err_msg = 'Unexpected error. Could not get employee.'
                self._logger.error(f'{err_msg}. Error: {ex}', exc_info=True)
                return HttpResponseServerError(err_msg)
        else:
            # get all
            try:
                # index pages from 1
                # TODO add more validation
                page_number = int(request.GET.get('page', EmployeeView.DEFAULT_PAGE_NUMBER)) - 1
                page_size = int(request.GET.get('page_size', EmployeeView.DEFAULT_PAGE_SIZE))

                order_by = request.GET.get('order_by', EmployeeView.DEFAULT_ORDER_BY)
                order = request.GET.get('order', EmployeeView.DEFAULT_ORDER)
                order_by = '-' + order_by if order == 'descending' else order_by

                # TODO add more filtering logic and move filter building someplace else
                filters = dict()
                if request.GET.get('gender', None):
                    filters['gender'] = request.GET.get('gender')

                employees = Employee.objects.filter(**filters).order_by(order_by)[page_number*page_size:(page_number+1)*page_size]
                # TODO set the safe parameter back to True and impose a convention on a JSON with payload dict
                # TODO such as {'payload': [...], ...}
                return JsonResponse([v for v in employees.values()],
                                    safe=False)
            except Exception as ex:
                err_msg = 'Unexpected error. Could not get employee.'
                self._logger.error(f'{err_msg}. Error: {ex}', exc_info=True)
                return HttpResponseServerError(err_msg)

    def put(self, request):
        _id = request.GET.get('id', None)
        if not _id:
            err_msg = 'Specify "id" query parameter.'
            self._logger.error(err_msg)
            return HttpResponseBadRequest(err_msg)

        error_response = Utils.check_json(request)
        if error_response:
            self._logger.error(error_response.content.decode())
            return error_response

        success, parse_result = Utils.parse_json(request)
        if not success:
            self._logger.error(parse_result.content.decode())
            return parse_result

        try:  # TODO this won't perform application level validation and a better way must be implemented
            employees = Employee.objects.filter(pk=_id)
            if len(employees) == 0:
                err_msg = 'Could not find employee.'
                self._logger.error(err_msg)
                return HttpResponseNotFound(err_msg)
            employees.update(**parse_result)
        except Exception as ex:
            err_msg = 'Unexpected error. Could not update.'
            self._logger.error(f'{err_msg}. Error: {ex}', exc_info=True)
            return HttpResponseServerError(err_msg)
        return HttpResponse("Successful update.")

    @staticmethod
    def _convert_date(date_str):
        try:
            return True, datetime.datetime.strptime(
                date_str, EmployeeView.DB_DATE_FORMAT). \
                strftime(EmployeeView.DB_DATE_FORMAT)
        except Exception as ex:
            pass

        try:
            return True, datetime.datetime.strptime(date_str,
                                                    EmployeeView.INPUT_DATE_FORMAT) \
                .strftime(EmployeeView.DB_DATE_FORMAT)
        except Exception as ex:
            return False, HttpResponseBadRequest(f'Expected date in '
                                                 f'"{EmployeeView.INPUT_DATE_FORMAT}" or '
                                                 f'{EmployeeView.DB_DATE_FORMAT} '
                                                 f'formats.')

    @staticmethod
    def validate_employee(employee: Employee):
        if employee.email is None:
            employee.email = ''
        if employee.gender is None:
            employee.gender = ''
        if employee.industry is None:
            employee.industry = ''

        success, converted_dob = EmployeeView._convert_date(employee.date_of_birth)
        if not success:
            return converted_dob
        employee.date_of_birth = converted_dob

        error_response = Utils.validate_model_object(employee)
        if error_response:
            return error_response
        return


class Utils:
    # TODO move to utils module / package even
    @staticmethod
    def check_json(request):
        if 'Content-Type' not in request.headers:
            return HttpResponseBadRequest('Missing Content-Type header.')
        if request.headers['Content-Type'] != 'application/json':
            return HttpResponseBadRequest('Expected Content-Type application/json.')
        return

    @staticmethod
    def parse_json(request):
        try:
            obj = json.loads(request.body)
        except Exception as ex:
            return False, HttpResponseBadRequest('Could not parse body as JSON.')
        return True, obj

    @staticmethod
    def validate_model_object(obj):
        try:
            obj.full_clean()
        except ValidationError as ex:
            return HttpResponseBadRequest(str(ex))
        except Exception as ex:
            return HttpResponseServerError('Unexpected error during validation.')
        return
