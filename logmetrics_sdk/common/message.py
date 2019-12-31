message: dict = {
    'TrackingID': str,
    'MessageType': str,
    'Duration': int,
    'Host': str,
    'Node': str,
    'ClientHost': str,
    'BackendSystem': str,
    'BackendMethod': str,
    'FrontendMethod': str,
    'BackendServiceName': str,
    'ApplicationName': str,
    'ServiceVersion': str,
    'StartDateTime': str,
    'EndDateTime': str,
    'Aspects': str,
    'QueryParams': str,
    'Path': str,
    'RequestBody': str,
    'ResponseBody': str,
    'HttpMethod': str,
    'HttpStatus': int,
    'ContentType': str,
    'Action': str,
    'Error': str,
    'ErrorCode': str,
    'ErrorMessage': str,
    'Environment': str
}


def clear_message():
    message['TrackingID'] = None
    message['MessageType'] = "LOGMETRICS_MESSAGE"
    message['Duration'] = 0
    message['Host'] = None
    message['Node'] = None
    message['ClientHost'] = None
    message['BackendSystem'] = None
    message['BackendMethod'] = None
    message['FrontendMethod'] = None
    message['BackendServiceName'] = None
    message['ApplicationName'] = None
    message['ServiceVersion'] = None
    message['StartDateTime'] = None
    message['EndDateTime'] = None
    message['Aspects'] = None
    message['QueryParams'] = None
    message['Path'] = None
    message['RequestBody'] = None
    message['ResponseBody'] = None
    message['HttpMethod'] = None
    message['HttpStatus'] = 0
    message['ContentType'] = None
    message['Action'] = None
    message['Error'] = None
    message['ErrorCode'] = None
    message['ErrorMessage'] = None
    message['Environment'] = None
