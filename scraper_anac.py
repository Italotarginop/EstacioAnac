import requests
import os
from urllib.parse import urljoin
import re
from pathlib import Path

def get_csv_links_from_page(url):
    """Extrai todos os links de arquivos CSV de uma página"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Procura por arquivos .csv na página
        csv_pattern = r'(\w+\.csv)'
        csv_files = re.findall(csv_pattern, response.text)
        
        # Cria URLs completas para os arquivos CSV
        csv_urls = [urljoin(url, csv_file) for csv_file in csv_files]
        return csv_urls
    
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return []

def download_file(url, local_path):
    """Baixa um arquivo da URL para o caminho local"""
    try:
        print(f"Baixando: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        print(f"✓ Salvo em: {local_path}")
        return True
        
    except requests.RequestException as e:
        print(f"✗ Erro ao baixar {url}: {e}")
        return False

def main():
    # URLs base para cada ano
    base_urls = [
        "https://siros.anac.gov.br/siros/registros/diversos/vra/2021/",
        "https://siros.anac.gov.br/siros/registros/diversos/vra/2022/",
        "https://siros.anac.gov.br/siros/registros/diversos/vra/2023/",
        "https://siros.anac.gov.br/siros/registros/diversos/vra/2024/",
        "https://siros.anac.gov.br/siros/registros/diversos/vra/2025/"
    ]
    
    # Diretório base para salvar os arquivos
    download_dir = "dados_vra_anac"
    
    total_downloaded = 0
    total_failed = 0
    
    for base_url in base_urls:
        print(f"\n{'='*60}")
        print(f"Processando: {base_url}")
        print(f"{'='*60}")
        
        # Extrai o ano da URL
        year = base_url.split('/')[-2]
        year_dir = os.path.join(download_dir, year)
        
        # Obtém todos os links CSV da página
        csv_urls = get_csv_links_from_page(base_url)
        
        if not csv_urls:
            print(f"Nenhum arquivo CSV encontrado para {year}")
            continue
        
        print(f"Encontrados {len(csv_urls)} arquivos CSV para {year}")
        
        # Baixa cada arquivo CSV
        for csv_url in csv_urls:
            filename = os.path.basename(csv_url)
            local_path = os.path.join(year_dir, filename)
            
            # Verifica se o arquivo já existe
            if os.path.exists(local_path):
                print(f"⚠ Arquivo já existe: {local_path}")
                continue
            
            # Baixa o arquivo
            if download_file(csv_url, local_path):
                total_downloaded += 1
            else:
                total_failed += 1
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"RESUMO DO DOWNLOAD")
    print(f"{'='*60}")
    print(f"✓ Arquivos baixados com sucesso: {total_downloaded}")
    print(f"✗ Arquivos com falha: {total_failed}")
    print(f"📁 Arquivos salvos em: {os.path.abspath(download_dir)}")

if __name__ == "__main__":
    main()