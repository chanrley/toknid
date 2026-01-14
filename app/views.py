from django.shortcuts import render
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pathlib import Path
import json
import subprocess
import platform

# Create your views here.

def healthcheck(request):
    """
    Endpoint de healthcheck para Docker.
    Retorna status 200 OK sem validar host ou autenticação.
    Usado pelos healthchecks internos do Docker.
    """
    return JsonResponse({'status': 'ok', 'service': 'django'}, status=200)

@require_http_methods(["GET"])
def healthz_view(request):
    """
    Endpoint de liveness para healthcheck do Docker.
    Sempre retorna 200 OK com texto simples "ok".
    Não depende de banco de dados, cache ou autenticação.
    Usado exclusivamente para verificar se o container está vivo.
    """
    return HttpResponse("ok", content_type="text/plain", status=200)
def index(request):
    # home já renderiza o dashboard direto
    return render(
        request,
        'app/dashboard.html',
        {'page_title': 'Dashboard — tokn.id | partners'}
    )


def clientes(request):
    # MOCK de dados pra alimentar o {% for c in clientes %}
    clientes_mock = [
        {
            "nome": "João Silva",
            "vip": True,
            "contato": "+55 (11) 98888-1111 · joao@email.com",
            "moedas": 650,
            "ultima": "Recebeu 50 moedas",
            "ultima_data": "02/11/2025",
            "canal": "PDV",
            "status": "Ativo",
        },
        {
            "nome": "Maria Souza",
            "vip": False,
            "contato": "+55 (11) 97777-2222 · maria@email.com",
            "moedas": 120,
            "ultima": "Resgatou 40 moedas",
            "ultima_data": "28/10/2025",
            "canal": "WhatsApp",
            "status": "Ativo",
        },
        {
            "nome": "Carlos Lima",
            "vip": False,
            "contato": "+55 (11) 96666-3333 · carlos@email.com",
            "moedas": 0,
            "ultima": "Sem atividade recente",
            "ultima_data": "05/09/2025",
            "canal": "App",
            "status": "Inativo",
        },
    ]

    return render(
        request,
        'app/clientes.html',
        {
            'page_title': 'Clientes — tokn.id | partners',
            'clientes': clientes_mock,
        }
    )


def transacoes(request):
    # MOCK de transações para montar a tabela / cards
    transacoes_mock = [
        {
            "cliente": "João Silva",
            "tipo": "Creditada",
            "moedas": 120,
            "canal": "PDV",
            "descricao": "Compra R$ 120,00",
            "data": "02/11/2025 · 18:42",
            "referencia": "#TRX-1001",
        },
        {
            "cliente": "Maria Souza",
            "tipo": "Resgatada",
            "moedas": 40,
            "canal": "WhatsApp",
            "descricao": "Resgate 40 moedas · Desconto no pedido",
            "data": "01/11/2025 · 15:08",
            "referencia": "#TRX-0992",
        },
        {
            "cliente": "Carlos Lima",
            "tipo": "Creditada",
            "moedas": 80,
            "canal": "App / Link",
            "descricao": "Compra R$ 89,90",
            "data": "30/10/2025 · 20:17",
            "referencia": "#TRX-0981",
        },
        {
            "cliente": "João Silva",
            "tipo": "Creditada",
            "moedas": 60,
            "canal": "PDV",
            "descricao": "Campanha Outubro em Dobro",
            "data": "28/10/2025 · 11:03",
            "referencia": "#TRX-0975",
        },
    ]

    return render(
        request,
        'app/transacoes.html',
        {
            'page_title': 'Transações — tokn.id | partners',
            'transacoes': transacoes_mock,
        }
    )


def campanhas(request):
    return render(
        request,
        'app/campanhas.html',
        {'page_title': 'Campanhas — tokn.id | partners'}
    )


def configuracoes(request):
    return render(
        request,
        'app/configuracoes.html',
        {'page_title': 'Configurações – tokn.id | partners'}
    )


def configuracoes_estabelecimento(request):
    return render(request, 'app/config_estabelecimento.html')


def configuracoes_regra_padrao(request):
    return render(request, 'app/config_regra_padrao.html')


# ========= AJUDA / SUPORTE =========

def ajuda_home(request):
    # Landing principal de Ajuda / Suporte
    return render(
        request,
        'app/ajuda_suporte.html',
        {'page_title': 'Ajuda / Suporte — tokn.id | partners'}
    )


def ajuda_guia(request, slug):
    # whitelist simples pra evitar template injection
    allowed = {
        "cliente-nao-recebeu-moedas",
        "como-resgatar-no-balcao",
        "carteira-phantom-o-que-o-cliente-precisa-fazer",
        "campanhas-como-criar-e-usar",
        "integracoes-pdv-e-whatsapp",
        "ajustar-regra-padrao",
        "boas-praticas-para-crescer",
        "guias-rapidos",
        "checklist-problemas-comuns",
    }

    if slug not in allowed:
        raise Http404("Página de ajuda não encontrada")

    template_path = f'app/ajuda/{slug}.html'
    return render(
        request,
        template_path,
        {'page_title': 'Ajuda / Suporte — tokn.id | partners'}
    )


@csrf_exempt
@require_http_methods(["POST"])
def creditar_moedas(request):
    """
    View para creditar moedas chamando o script TypeScript que executa transação na Solana.
    Recebe: chave_privada, carteira_destino, valor_minimo, valor
    Retorna: JSON com sucesso e signature ou erro
    """
    try:
        # Parse do JSON recebido
        body = json.loads(request.body)
        chave_privada = body.get('chave_privada')
        carteira_destino = body.get('carteira_destino')
        valor_minimo = body.get('valor_minimo', False)
        valor = body.get('valor')
        
        # Validações
        if not chave_privada or not carteira_destino:
            return JsonResponse({
                'sucesso': False,
                'erro': 'chave_privada e carteira_destino são obrigatórios'
            }, status=400)
        
        # Caminho para o script TypeScript
        script_path = Path(__file__).parent / 'ts' / 'exec-transacao.ts'
        
        # Preparar argumentos para o script
        # No Windows, usar shell=True e construir comando como string
        use_shell = platform.system() == 'Windows'
        
        if use_shell:
            # Windows: construir comando como string
            cmd_parts = [
                'npx', 'tsx',
                f'"{script_path}"',
                f'"{chave_privada}"',
                f'"{carteira_destino}"',
                str(valor_minimo).lower(),
            ]
            if valor is not None:
                cmd_parts.append(str(valor))
            args = ' '.join(cmd_parts)
        else:
            # Linux/Mac: usar lista
            args = [
                'npx', 'tsx',
                str(script_path),
                chave_privada,
                carteira_destino,
                str(valor_minimo).lower(),
            ]
            if valor is not None:
                args.append(str(valor))
        
        # Executar o script TypeScript
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60,  # Timeout de 60 segundos
                cwd=Path(__file__).parent.parent,  # Diretório raiz do projeto
                shell=use_shell
            )
            
            # Tentar parsear a saída (stdout ou stderr)
            output = result.stdout.strip() or result.stderr.strip()
            
            if result.returncode == 0:
                # Sucesso - parsear JSON da stdout
                # Pode haver texto adicional (como console.log), extrair apenas o JSON
                try:
                    # Tentar parsear diretamente
                    data = json.loads(output)
                except json.JSONDecodeError:
                    # Se falhar, tentar pegar a última linha que contém JSON válido
                    lines = output.split('\n')
                    data = None
                    for line in reversed(lines):
                        line = line.strip()
                        if line.startswith('{') and line.endswith('}'):
                            try:
                                data = json.loads(line)
                                break
                            except json.JSONDecodeError:
                                continue
                    
                    if data is None:
                        raise json.JSONDecodeError("JSON não encontrado no output", output, 0)
                
                try:
                    if data.get('sucesso'):
                        # Adicionar link do explorer
                        signature = data.get('signature', '')
                        explorer_url = f'https://solscan.io/tx/{signature}' if signature else ''
                        return JsonResponse({
                            'sucesso': True,
                            'signature': signature,
                            'explorer': explorer_url
                        })
                    else:
                        return JsonResponse({
                            'sucesso': False,
                            'erro': data.get('erro', 'Erro desconhecido')
                        }, status=500)
                except json.JSONDecodeError:
                    return JsonResponse({
                        'sucesso': False,
                        'erro': f'Erro ao processar resposta do script: {output[:200]}'
                    }, status=500)
            else:
                # Erro - tentar parsear JSON do stderr
                try:
                    error_data = json.loads(result.stderr.strip())
                    return JsonResponse({
                        'sucesso': False,
                        'erro': error_data.get('erro', 'Erro ao executar transação')
                    }, status=500)
                except json.JSONDecodeError:
                    return JsonResponse({
                        'sucesso': False,
                        'erro': f'Erro ao executar script: {result.stderr[:200] or result.stdout[:200]}'
                    }, status=500)
                    
        except subprocess.TimeoutExpired:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Timeout ao executar transação (limite de 60 segundos)'
            }, status=500)
        except FileNotFoundError:
            return JsonResponse({
                'sucesso': False,
                'erro': 'tsx não encontrado. Certifique-se de ter Node.js e npx instalados.'
            }, status=500)
        except Exception as e:
            return JsonResponse({
                'sucesso': False,
                'erro': f'Erro ao executar script: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'sucesso': False,
            'erro': 'JSON inválido no corpo da requisição'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'erro': f'Erro ao processar requisição: {str(e)}'
        }, status=500)
