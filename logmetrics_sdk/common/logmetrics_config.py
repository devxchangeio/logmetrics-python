
class LogMetricsConfig:

    enable_logmetrics = True
    enable_frontend_request = True
    enable_frontend_response = True
    enable_backend = True
    enable_backend_request = True
    enable_backend_response = True

    @classmethod
    def set_internal_state(cls, enable_logmetrics=True,
                           enable_frontend_request=True, enable_frontend_response=True,
                           enable_backend=True, enable_backend_request=True, enable_backend_response=True):
        cls.enable_logmetrics = enable_logmetrics
        cls.enable_frontend_request = enable_frontend_request
        cls.enable_frontend_response = enable_frontend_response
        cls.enable_backend = enable_backend
        cls.enable_backend_request = enable_backend_request
        cls.enable_backend_response = enable_backend_response

