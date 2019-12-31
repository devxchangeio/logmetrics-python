import json
import logging
import datetime

from functools import wraps
from json import JSONDecodeError
from typing import Dict
import uuid

from logmetrics_sdk.utils.importer import LazyImport
from logmetrics_sdk.common.message import message, clear_message
from logmetrics_sdk.utils.constants import *
from logmetrics_sdk.utils.timer import TimeUtil, preferred_clock
from logmetrics_sdk.patch.patch import patch_backend
from logmetrics_sdk.common.logmetrics_config import LogMetricsConfig

flask = LazyImport('flask')
logging.basicConfig(level=logging.INFO)


def LogMetrics(_fn=None, *, enable_logmetrics=True, enable_frontend_request=True,enable_frontend_response=True,
               enable_backend=True, enable_backend_request=True, enable_backend_response = True):

    LogMetricsConfig.set_internal_state(enable_logmetrics,
                                        enable_frontend_request,
                                        enable_frontend_response,
                                        enable_backend,
                                        enable_backend_request,
                                        enable_backend_response)
    patch_backend()

    def new_func(fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            start = preferred_clock()
            clear_message()
            message['TrackingID'] = str(uuid.uuid4())
            message['Action'] = FRONTEND
            message['MessageType'] = LOGMETRICS_MESSAGE
            message['StartDateTime'] = str(datetime.datetime.now())

            if flask.has_request_context():

                if enable_frontend_request:
                    if flask.request.data:
                        message['RequestBody'] = flask.request.data

                    if flask.request.query_string:
                        message['QueryParams'] = flask.request.query_string

                message['ClientHost'] = flask.request.remote_addr
                message['Host'] = flask.request.host
                message['HttpMethod'] = flask.request.method
                message['Path'] = flask.request.path
                message['FrontendMethod'] = flask.request.endpoint

            return_value = fn(*args, **kwargs)
            end = preferred_clock()
            message['EndDateTime'] = str(datetime.datetime.now())

            if return_value:
                response: flask.Response = return_value
                data = response.get_json()
                try:
                    status = int(response.status_code)
                    message['HttpStatus'] = status
                    message['Fault'] = status not in (200, 300)
                    if enable_frontend_response and data:
                        message['ResponseBody'] = json.dumps(data)
                    message['ContentType'] = response.content_type
                except (JSONDecodeError, TypeError):
                    if enable_frontend_response and data:
                        message['ResponseBody'] = json.dumps(data)

            elif isinstance(return_value, Dict):
                if 'statusCode' in return_value:
                    status = int(return_value['statusCode'])
                    message['HttpStatus'] = status
                    message['Fault'] = not (status == 200 or status == 300)
                    if 'body' in return_value:
                        try:
                            if enable_frontend_response:
                                message['ResponseBody'] = json.dumps(json.loads(return_value['body']))
                        except (JSONDecodeError, TypeError):
                            if enable_frontend_response:
                                message['ResponseBody'] = return_value['body']
                else:
                    try:
                        status = int(getattr(return_value, 'status_code', 200))
                        message['HttpStatus'] = status
                        message['Fault'] = not (status == 200 or status == 300)
                    except (ValueError, TypeError):
                        pass
            message['Duration'] = TimeUtil.get_duration(start, end)

            if enable_logmetrics:
                try:
                    logging.info(json.dumps(message))
                except Exception as ex:
                    logging.error(f'{ex}')

            return return_value

        wrap._original = fn
        return wrap

    if _fn is None:
        return new_func

    return new_func(_fn)
