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
        import sys
        try:
            log_path = Path(__file__).resolve().parent.parent / 'logs' / 'debug.log'
            os.makedirs(log_path.parent, exist_ok=True)
            http_host = request.META.get('HTTP_HOST', '')
            from django.conf import settings
            
            # Garantir que 127.0.0.1 e localhost estejam sempre em ALLOWED_HOSTS
            if '127.0.0.1' not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append('127.0.0.1')
                print(f"DEBUG: Adicionado 127.0.0.1 ao ALLOWED_HOSTS no middleware", file=sys.stderr)
            if 'localhost' not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append('localhost')
                print(f"DEBUG: Adicionado localhost ao ALLOWED_HOSTS no middleware", file=sys.stderr)
            
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'middleware.py:__call__',
                    'message': 'Host recebido na requisição (antes do CommonMiddleware)',
                    'data': {
                        'HTTP_HOST': http_host,
                        'ALLOWED_HOSTS': list(settings.ALLOWED_HOSTS),
                    },
                    'timestamp': int(__import__('time').time() * 1000)
                }) + '\n')
            print(f"DEBUG: HTTP_HOST={http_host}, ALLOWED_HOSTS={list(settings.ALLOWED_HOSTS)}", file=sys.stderr)
        except Exception as e:
            import sys
            print(f"DEBUG MIDDLEWARE ERROR: {e}", file=sys.stderr)
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
                            'HTTP_HOST': request.META.get('HTTP_HOST', ''),
                            'ALLOWED_HOSTS': list(settings.ALLOWED_HOSTS),
                            'error': str(e)
                        },
                        'timestamp': int(__import__('time').time() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            raise
