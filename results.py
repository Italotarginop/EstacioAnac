import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime
import numpy as np
import base64
from io import BytesIO

def create_flight_cancellation_dashboard():
    # Configurar estilo dos gráficos
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    
    # Ler todos os CSVs da pasta 'all'
    csv_files = glob.glob(os.path.join('all', '*.csv'))
    
    if not csv_files:
        print("Nenhum arquivo CSV encontrado na pasta 'all'")
        return
    
    # Combinar todos os CSVs
    dataframes = []
    for file in csv_files:
        try:
            # Ler CSV com separador correto (ponto e vírgula)
            df = pd.read_csv(file, sep=';', encoding='utf-8')
            dataframes.append(df)
            print(f"Arquivo carregado: {file} - {len(df)} registros")
        except Exception as e:
            print(f"Erro ao carregar {file}: {e}")
    
    if not dataframes:
        print("Nenhum arquivo CSV válido encontrado")
        return
    
    # Combinar todos os dataframes
    df = pd.concat(dataframes, ignore_index=True)
    print(f"Total de registros combinados: {len(df)}")
    
    # Filtrar apenas voos cancelados
    df_cancelled = df[df['Situação Voo'] == 'CANCELADO'].copy()
    print(f"Total de voos cancelados: {len(df_cancelled)}")
    
    if len(df_cancelled) == 0:
        print("Nenhum voo cancelado encontrado nos dados")
        return
    
    # Preparar dados para análise
    df_cancelled['Data'] = pd.to_datetime(df_cancelled['Referência'], format='%Y-%m-%d', errors='coerce')
    df_cancelled['Ano'] = df_cancelled['Data'].dt.year
    df_cancelled['Mês'] = df_cancelled['Data'].dt.month
    df_cancelled['Dia_Semana'] = df_cancelled['Data'].dt.day_name()
    
    # Extrair hora da partida prevista
    df_cancelled['Hora_Partida'] = pd.to_datetime(df_cancelled['Partida Prevista'], format='%d/%m/%Y %H:%M', errors='coerce').dt.hour
    
    # Função para converter gráfico em base64
    def plot_to_base64():
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300, facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        plt.close()
        return f"data:image/png;base64,{image_base64}"
    
    # Lista para armazenar gráficos
    charts = []
    
    # 1. Empresas aéreas que mais cancelam voos
    plt.figure(figsize=(14, 8))
    airline_counts = df_cancelled['Empresa Aérea'].value_counts().head(15)
    bars = plt.bar(range(len(airline_counts)), airline_counts.values, color='#e74c3c', alpha=0.8)
    plt.title('Top 15 Empresas Aéreas com Mais Cancelamentos', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Empresa Aérea', fontsize=12)
    plt.ylabel('Número de Cancelamentos', fontsize=12)
    plt.xticks(range(len(airline_counts)), airline_counts.index, rotation=45, ha='right')
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, airline_counts.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(value), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    charts.append(('Empresas que Mais Cancelam Voos', plot_to_base64()))
    
    # 2. Porcentagem de voos cancelados por empresa
    plt.figure(figsize=(14, 8))
    total_flights = df.groupby('Empresa Aérea').size()
    cancelled_flights = df_cancelled.groupby('Empresa Aérea').size()
    cancellation_rate = (cancelled_flights / total_flights * 100).fillna(0).sort_values(ascending=False).head(15)
    
    bars = plt.bar(range(len(cancellation_rate)), cancellation_rate.values, color='#c0392b', alpha=0.8)
    plt.title('Taxa de Cancelamento por Empresa Aérea (%)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Empresa Aérea', fontsize=12)
    plt.ylabel('Porcentagem de Cancelamentos (%)', fontsize=12)
    plt.xticks(range(len(cancellation_rate)), cancellation_rate.index, rotation=45, ha='right')
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, cancellation_rate.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    charts.append(('Taxa de Cancelamento por Empresa', plot_to_base64()))
    
    # 3. Aeroportos de origem com mais cancelamentos
    plt.figure(figsize=(14, 8))
    # Usar descrição do aeroporto para melhor visualização
    origin_counts = df_cancelled['Descrição Aeroporto Origem'].value_counts().head(15)
    # Encurtar nomes muito longos
    origin_labels = [label[:50] + '...' if len(label) > 50 else label for label in origin_counts.index]
    
    bars = plt.bar(range(len(origin_counts)), origin_counts.values, color='#f39c12', alpha=0.8)
    plt.title('Top 15 Aeroportos de Origem com Mais Cancelamentos', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Aeroporto de Origem', fontsize=12)
    plt.ylabel('Número de Cancelamentos', fontsize=12)
    plt.xticks(range(len(origin_counts)), origin_labels, rotation=45, ha='right')
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, origin_counts.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(value), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    charts.append(('Aeroportos de Origem com Mais Cancelamentos', plot_to_base64()))
    
    # 4. Horários com mais cancelamentos
    plt.figure(figsize=(14, 8))
    hour_counts = df_cancelled['Hora_Partida'].value_counts().sort_index()
    bars = plt.bar(hour_counts.index, hour_counts.values, color='#9b59b6', alpha=0.8)
    plt.title('Cancelamentos por Hora do Dia', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Hora do Dia', fontsize=12)
    plt.ylabel('Número de Cancelamentos', fontsize=12)
    plt.xticks(range(0, 24, 2))
    plt.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, hour_counts.values):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    str(value), ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    charts.append(('Cancelamentos por Horário', plot_to_base64()))
    
    # 5. Épocas (meses) com mais cancelamentos
    plt.figure(figsize=(14, 8))
    month_counts = df_cancelled['Mês'].value_counts().sort_index()
    month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    bars = plt.bar(range(len(month_counts)), month_counts.values, color='#27ae60', alpha=0.8)
    plt.title('Cancelamentos por Mês', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Mês', fontsize=12)
    plt.ylabel('Número de Cancelamentos', fontsize=12)
    plt.xticks(range(len(month_counts)), [month_names[i-1] for i in month_counts.index])
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, month_counts.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(value), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    charts.append(('Cancelamentos por Mês', plot_to_base64()))
    
    # 6. Anos com mais cancelamentos
    plt.figure(figsize=(14, 8))
    year_counts = df_cancelled['Ano'].value_counts().sort_index()
    plt.plot(year_counts.index, year_counts.values, marker='o', linewidth=3, markersize=10, color='#e74c3c')
    plt.title('Evolução dos Cancelamentos por Ano', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Ano', fontsize=12)
    plt.ylabel('Número de Cancelamentos', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Adicionar valores nos pontos
    for x, y in zip(year_counts.index, year_counts.values):
        plt.text(x, y + max(year_counts.values) * 0.02, str(y), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    charts.append(('Cancelamentos por Ano', plot_to_base64()))
    
    # 7. Dia da semana com mais cancelamentos
    plt.figure(figsize=(14, 8))
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df_cancelled['Dia_Semana'].value_counts().reindex(day_order, fill_value=0)
    day_names_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    bars = plt.bar(day_names_pt, day_counts.values, color='#16a085', alpha=0.8)
    plt.title('Cancelamentos por Dia da Semana', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Dia da Semana', fontsize=12)
    plt.ylabel('Número de Cancelamentos', fontsize=12)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars, day_counts.values):
        if value > 0:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    str(value), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    charts.append(('Cancelamentos por Dia da Semana', plot_to_base64()))
    
    # 8. Gráfico de pizza - Distribuição por tipo de linha
    plt.figure(figsize=(10, 10))
    tipo_linha_counts = df_cancelled['Código Tipo Linha'].value_counts()
    tipo_linha_labels = {'I': 'Internacional', 'N': 'Nacional', 'R': 'Regional'}
    labels = [tipo_linha_labels.get(code, f'Tipo {code}') for code in tipo_linha_counts.index]
    
    colors = ['#e74c3c', '#3498db', '#f39c12']
    wedges, texts, autotexts = plt.pie(tipo_linha_counts.values, labels=labels, autopct='%1.1f%%', 
                                      colors=colors, startangle=90, textprops={'fontsize': 12})
    plt.title('Distribuição de Cancelamentos por Tipo de Linha', fontsize=16, fontweight='bold', pad=20)
    
    # Melhorar aparência dos textos
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    charts.append(('Distribuição por Tipo de Linha', plot_to_base64()))
    
    # Calcular estatísticas gerais
    total_voos = len(df)
    total_cancelados = len(df_cancelled)
    taxa_cancelamento = (total_cancelados / total_voos) * 100
    empresa_mais_cancela = df_cancelled['Empresa Aérea'].value_counts().index[0]
    aeroporto_mais_cancela = df_cancelled['Sigla ICAO Aeroporto Origem'].value_counts().index[0]
    
    # Gerar HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard de Cancelamentos de Voos - Brasil</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                text-align: center;
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 40px 20px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            .header p {{
                margin: 5px 0;
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8f9fa;
            }}
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 5px solid #e74c3c;
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                color: #e74c3c;
                margin-bottom: 5px;
            }}
            .stat-label {{
                color: #7f8c8d;
                font-size: 1.1em;
                font-weight: 500;
            }}
            .chart-container {{
                background: white;
                margin: 20px;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .chart-title {{
                font-size: 1.8em;
                font-weight: bold;
                margin-bottom: 20px;
                color: #2c3e50;
                border-bottom: 3px solid #e74c3c;
                padding-bottom: 15px;
            }}
            .chart-image {{
                width: 100%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding: 30px;
                background: #2c3e50;
                color: white;
            }}
            .footer p {{
                margin: 5px 0;
                opacity: 0.8;
            }}
            .highlight {{
                background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
                padding: 20px;
                margin: 20px;
                border-radius: 10px;
                border-left: 5px solid #e74c3c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✈️ Dashboard de Cancelamentos de Voos</h1>
                <p>Análise Completa dos Dados de Voos Brasileiros</p>
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_cancelados:,}</div>
                    <div class="stat-label">Total de Cancelamentos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(csv_files)}</div>
                    <div class="stat-label">Arquivos Processados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_voos:,}</div>
                    <div class="stat-label">Total de Voos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{taxa_cancelamento:.2f}%</div>
                    <div class="stat-label">Taxa de Cancelamento</div>
                </div>
            </div>
            
            <div class="highlight">
                <h3>🔍 Principais Insights:</h3>
                <p><strong>Empresa que mais cancela:</strong> {empresa_mais_cancela}</p>
                <p><strong>Aeroporto com mais cancelamentos:</strong> {aeroporto_mais_cancela}</p>
                <p><strong>Período analisado:</strong> {df_cancelled['Data'].min().strftime('%d/%m/%Y')} a {df_cancelled['Data'].max().strftime('%d/%m/%Y')}</p>
            </div>
    """
    
    # Adicionar gráficos ao HTML
    for title, chart_data in charts:
        html_content += f"""
        <div class="chart-container">
            <div class="chart-title">{title}</div>
            <img src="{chart_data}" alt="{title}" class="chart-image">
        </div>
        """
    
    html_content += """
            <div class="footer">
                <p><strong>Dashboard de Cancelamentos de Voos - Brasil</strong></p>
                <p>Desenvolvido com Python, Pandas, Matplotlib e Seaborn</p>
                <p>Dados processados automaticamente a partir dos arquivos CSV da ANAC</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Salvar HTML
    with open('dashboard_cancelamentos_voos.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n" + "="*60)
    print("🎉 DASHBOARD CRIADO COM SUCESSO!")
    print("="*60)
    print(f"📊 Total de voos analisados: {total_voos:,}")
    print(f"❌ Total de cancelamentos: {total_cancelados:,}")
    print(f"📈 Taxa de cancelamento: {taxa_cancelamento:.2f}%")
    print(f"🏢 Empresa que mais cancela: {empresa_mais_cancela}")
    print(f"✈️ Aeroporto com mais cancelamentos: {aeroporto_mais_cancela}")
    print(f"📁 Arquivos processados: {len(csv_files)}")
    print("="*60)
    print("📄 Abra o arquivo 'dashboard_cancelamentos_voos.html' no seu navegador!")
    print("="*60)

if __name__ == "__main__":
    # Criar pasta 'all' se não existir
    if not os.path.exists('all'):
        os.makedirs('all')
        print("📁 Pasta 'all' criada. Coloque seus arquivos CSV nela e execute novamente.")
    else:
        create_flight_cancellation_dashboard()