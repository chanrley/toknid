import json
import os
from pathlib import Path
from django.core.exceptions import DisallowedHost

class DebugHostMiddleware:
    """
    Middleware para debug de problemas com ALLOWED_HOSTS
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # #region agent log
        try:
            log_path = Path(__file__).resolve().parent.parent / 'logs' / 'debug.log'
            os.makedirs(log_path.parent, exist_ok=True)
            host = request.get_host()
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'middleware.py:__call__',
                    'message': 'Host recebido na requisição',
                    'data': {
                        'host': host,
                        'HTTP_HOST': request.META.get('HTTP_HOST', ''),
                        'ALLOWED_HOSTS': getattr(request, '_allowed_hosts', 'N/A')
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
        except: pass
        # #endregion

        try:
            response = self.get_response(request)
            return response
        except DisallowedHost as e:
            # #region agent log
            try:
                log_path = Path(__file__).resolve().parent.parent / 'logs' / 'debug.log'
                from django.conf import settings
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C',
                        'location': 'middleware.py:DisallowedHost',
                        'message': 'DisallowedHost capturado',
                        'data': {
                            'host': request.get_host(),
                            'HTTP_HOST': request.META.get('HTTP_HOST', ''),
                            'ALLOWED_HOSTS': list(settings.ALLOWED_HOSTS),
                            'error': str(e)
                        },
                        'timestamp': int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            raise
