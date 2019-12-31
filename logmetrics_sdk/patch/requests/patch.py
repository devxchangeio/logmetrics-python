
import json
import logging
import requests.sessions
import chardet
import datetime

from functools import wraps
from urllib.parse import urlsplit
from json import JSONDecodeError
from xml.etree.ElementTree import ParseError
from requests.structures import CaseInsensitiveDict

from logmetrics_sdk.common.logmetrics_config import LogMetricsConfig
from logmetrics_sdk.common.message import message
from logmetrics_sdk.utils.parse import parse_qs
from logmetrics_sdk.utils.constants import *
from logmetrics_sdk.utils.json_util import to_object


CONTENT_TYPE = 'content-type'

log = logging.getLogger(__name__)


def patch_requests_session():
    _patch_request()


def _patch_request():

    def time_requests_session_request(f):

        @wraps(f)
        def wrap(self, method, url, **kwargs):
            start_time = str(datetime.datetime.now())
            collect_payload_for_host = True
            parsed_url = urlsplit(url)
            query_params = (requests.sessions.merge_setting(kwargs.get('params'), self.params)
                            or parse_qs(parsed_url.query))
            request_data = kwargs.get('data') or kwargs.get('json')

            _message = {
                'TrackingID': message.get('TrackingID'),
                'MessageType': LOGMETRICS_MESSAGE,
                'FrontendMethod': message.get('FrontendMethod', None),
                'ApplicationName': message.get('ApplicationName', None),
                'BackendServiceName': None,
                'BackendSystem': parsed_url.netloc,
                'BackendMethod': parsed_url.path,
                'HttpMethod': method,
                'Action': BACKEND,
                'StartDateTime': start_time
            }

            if collect_payload_for_host and query_params:
                _message['QueryParams'] = query_params

            if request_data:
                request_headers = requests.sessions.merge_setting(
                    kwargs.get('headers'), self.headers, dict_class=CaseInsensitiveDict
                )
                if collect_payload_for_host and LogMetricsConfig.enable_backend_request:
                    payload = _process_payload_data(
                        payload=request_data,
                        payload_type='request',
                        content_type=request_headers.get(CONTENT_TYPE)
                    )
                    _message.update(payload)
            response = None
            try:
                response = f(self, method, url, **kwargs)
            except Exception as e:
                _message['Fault'] = True
                _message['ErrorMessage'] = getattr(e, 'message', str(e))
                _message['ErrorCode'] = type(e).__name__
                _message['HttpStatus'] = None
                raise e
            finally:
                if response:
                    if response.encoding is None:
                        response.encoding = chardet.detect(response.content)['encoding']
                        if collect_payload_for_host and LogMetricsConfig.enable_backend_response:
                            payload = _process_payload_data(
                                payload=response.text,
                                payload_type='response',
                                content_type=response.headers.get(CONTENT_TYPE))
                            _message.update(payload)
                    _message['HttpStatus'] = response.status_code
                    _message['Duration'] = 0
                if LogMetricsConfig.enable_backend_response:
                    logging.info(json.dumps(_message))
            return response
        return wrap

    requests.sessions.Session.request = time_requests_session_request(
        requests.sessions.Session.request
    )


def _process_payload_data(payload: str, payload_type: str, content_type: str):

    _message = {}
    metric_fieldname = payload_type.capitalize() + 'Body'
    content_is_json, content_is_xml, content_is_plaintext = False, False, False

    if content_type:
        content_is_json = '/json' in content_type
        content_is_xml = '/xml' in content_type
        content_is_plaintext = 'text/' in content_type

    if content_is_json:
        try:
            py_obj_data = to_object(payload)
            _message['ResponseBody'] = json.dumps(py_obj_data)
        except JSONDecodeError:
            _message[metric_fieldname] = payload.strip()
            _message['ErrorMessage'] = ('Error occurred while parsing JSON data for '
                                      + metric_fieldname)
            _message['ErrorCode'] = 'JSONParseError'

    elif content_is_xml:
        try:
            _message[metric_fieldname] = "{\"XML\": true}"
        except ParseError:
            _message[metric_fieldname] = payload.strip()
            _message['ErrorMessage'] = ('Error occurred while parsing XML data for '
                                      + metric_fieldname)
            _message['ErrorCode'] = 'XMLParseError'

    elif content_is_plaintext:
        _message[metric_fieldname] = payload.strip()

    else:
        try:
            py_obj_data = to_object(payload)
            _message[metric_fieldname] = json.dumps(py_obj_data)
        except JSONDecodeError:
            try:
                message[metric_fieldname] = "{\"XML\": true}"

            except ParseError:
                _message[metric_fieldname] = payload.strip()
                _message['ErrorMessage'] = ('Error occurred while parsing data as JSON & XML for '
                                          + metric_fieldname)
                _message['ErrorCode'] = 'ParseError'

    return _message
