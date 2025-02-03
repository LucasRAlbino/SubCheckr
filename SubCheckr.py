import requests
import concurrent.futures
import argparse
from termcolor import colored

# Função para exibir a arte inicial
def exibir_arte_inicial():
    arte = """
    ███████ ██    ██ ██████   ██████ ██   ██ ███████  ██████ ██   ██ ██████  
    ██      ██    ██ ██   ██ ██      ██   ██ ██      ██      ██  ██  ██   ██ 
    ███████ ██    ██ ██████  ██      ███████ █████   ██      █████   ██████  
         ██ ██    ██ ██   ██ ██      ██   ██ ██      ██      ██  ██  ██   ██ 
    ███████  ██████  ██████   ██████ ██   ██ ███████  ██████ ██   ██ ██   ██ 

    """
    print(colored(arte, "cyan"))
    print(colored("GitHub: https://github.com/LucasRAlbino", "magenta"))
    print("-" * 80)

# Lê os subdomínios do arquivo
def ler_subdominios(arquivo):
    try:
        with open(arquivo, "r") as f:
            return [linha.strip() for linha in f.readlines() if linha.strip()]
    except FileNotFoundError:
        print(f"Arquivo '{arquivo}' não encontrado.")
        return []

# Faz a requisição HTTP e retorna o status
def verificar_subdominio(url, verbose=False):
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        if verbose:
            print(colored(f"Testando: {url}", "white"))
        response = requests.get(url, timeout=5)
        status_code = response.status_code

        # Exibir somente Not Found (404) ou status 3xx
        if 300 <= status_code < 400:
            return colored(f"{url.split('://')[-1]} [{status_code}]", "cyan")
        elif status_code == 404:
            return colored(f"{url.split('://')[-1]} [Not Found]", "yellow")
        return colored(f"{url.split('://')[-1]} [{status_code}]", "green") if status_code == 200 else None
    except requests.RequestException:
        return None

# Função principal para varrer subdomínios com multithreading
def varrer_subdominios(subdominios, verbose=False):
    max_threads = min(50, len(subdominios))  # Aumenta o número máximo de threads para melhor desempenho

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futuros = {executor.submit(verificar_subdominio, subdominio, verbose): subdominio for subdominio in subdominios}
        for futuro in concurrent.futures.as_completed(futuros):
            try:
                resultado = futuro.result()
                if resultado and "Erro" not in resultado:
                    print(resultado)
            except Exception:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verificador de status HTTP para subdomínios.")
    parser.add_argument("arquivo", help="Arquivo com a lista de subdomínios a verificar.")
    parser.add_argument("--verbose", action="store_true", help="Mostra cada subdomínio testado em tempo real.")
    args = parser.parse_args()

    # Exibir a arte inicial
    exibir_arte_inicial()

    subdominios = ler_subdominios(args.arquivo)
    if subdominios:
        varrer_subdominios(subdominios, args.verbose)
    else:
        print("Nenhum subdomínio encontrado para verificar.")
