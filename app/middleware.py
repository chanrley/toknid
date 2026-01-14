import json
import os
from pathlib import Path
from django.core.exceptions import DisallowedHost
from django.http import JsonResponse

class DebugHostMiddleware:
    """
    Middleware para debug de problemas com ALLOWED_HOSTS
    Permite healthcheck sem validação de host
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
            
            # Extrair host sem porta para validação
            host = http_host.split(':')[0] if ':' in http_host else http_host
            
            # Garantir que hosts internos estejam sempre em ALLOWED_HOSTS
            # Isso é crítico para healthchecks do Docker
            internal_hosts = ['127.0.0.1', 'localhost', 'web']
            for internal_host in internal_hosts:
                if internal_host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(internal_host)
            
            # Para healthcheck ou hosts internos, garantir que o host específico esteja permitido
            if request.path == '/health/' or host in internal_hosts or host.startswith('127.'):
                if host and host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(host)
                    print(f"DEBUG: Adicionado {host} ao ALLOWED_HOSTS no middleware", file=sys.stderr)
            
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
