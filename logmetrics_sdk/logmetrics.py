import json
import logging
import datetime

from functools import wraps
from json import JSONDecodeError
from typing import Dict

from logmetrics_sdk.utils.importer import LazyImport
from logmetrics_sdk.utils.message import message, clear_message
from logmetrics_sdk.utils.constants import *
from logmetrics_sdk.utils.timer import TimeUtil, preferred_clock

flask = LazyImport('flask')
logging.basicConfig(level=logging.INFO)


def LogMetrics(_fn: object = None) -> object:
    """
    """

    def new_func(fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            start = preferred_clock()
            clear_message()
            message['Action'] = FRONTEND
            message['MessageType'] = LOGMETRICS_MESSAGE
            message['StartDateTime'] = str(datetime.datetime.now())

            if flask.has_request_context():
                message['Query'] = flask.request.query_string
                message['RequestBody'] = flask.request.data
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
                    message['ResponseBody'] = json.dumps(data)
                    message['ContentType'] = response.content_type
                except (JSONDecodeError, TypeError):
                    message['ResponseBody'] = json.dumps(data)

            elif isinstance(return_value, Dict):
                if 'statusCode' in return_value:
                    status = int(return_value['statusCode'])
                    message['HttpStatus'] = status
                    message['Fault'] = not (status == 200 or status == 300)
                    if 'body' in return_value:
                        try:
                            message['ResponseBody'] = json.dumps(json.loads(return_value['body']))
                        except (JSONDecodeError, TypeError):
                            message['ResponseBody'] = return_value['body']
                else:
                    try:
                        status = int(getattr(return_value, 'status_code', 200))
                        message['HttpStatus'] = status
                        message['Fault'] = not (status == 200 or status == 300)
                    except (ValueError, TypeError):
                        pass
            message['Duration'] = TimeUtil.get_duration(start, end)

            logging.info(message)
            return return_value

        wrap._original = fn
        return wrap

    if _fn is None:
        return new_func

    return new_func(_fn)
