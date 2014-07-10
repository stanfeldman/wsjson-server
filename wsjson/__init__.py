# -*- coding: utf-8 -*-
from kiss.views.core import JsonResponse
from paop import Aspect
import logging
logger = logging.getLogger(__name__)
from kiss.views.core import BadRequest


class ErrorHandler:
	def internal_server_error(self, request):
		return JsonResponse({"success": False, "error": {"code": 1, "message": "Ошибка сервера"}}, status=500)
	def wrong_call(self, request):
		return JsonResponse({"success": False, "error": {"code": 2, "message": "Неправильное обращение к серверу"}}, status=400)


class GoodRequestAspect(Aspect):
	""" аспект проверяющий что все указанные поля пришли в запросе """
	def __init__(self, params, is_post=True):
		Aspect.__init__(self)
		self.params = params
		self.is_post = is_post

	def on_enter(self, call):
		request = call.args[1]
		input_dict = request.form
		if not self.is_post:
			input_dict = request.args
		result = GoodRequestAspect.check_request_form(input_dict, self.params)
		if result:
			return result

	@staticmethod
	def check_request_form(input_dict, params):
		if not input_dict:
			logger.warning("Mandatory parameters {0} were missed".format(params))
			raise BadRequest()
		param_missed = None
		for param in params:
			if param not in input_dict or not input_dict[param]:
				param_missed = param
				break
		if param_missed:
			logger.warning("Mandatory parameters {0} were missed".format(params))
			raise BadRequest()
