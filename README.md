1 - 🚀 Execute o script scraper_anac.py
Este script faz o download automático de todos os arquivos CSV do site da ANAC:
https://siros.anac.gov.br/siros/registros/diversos/vra/
Os arquivos serão salvos em subpastas dentro do diretório dados_vra_anac.

2 - 📁 Organize os arquivos para análise
Após o download, reúna todos os arquivos CSV das subpastas de dados_vra_anac e mova-os para a pasta all, localizada na raiz do projeto.
Se a pasta all não existir, crie-a manualmente ou rode o script results.py uma vez para que ela seja criada automaticamente.

3 - 📊 Execute o script results.py
Este script irá processar todos os arquivos CSV da pasta all e gerar a página dashboard_cancelamentos_voos.html, que apresenta um resumo visual e estatístico dos voos cancelados.

4 - 🌐 Visualize o resultado
Abra o arquivo dashboard_cancelamentos_voos.html no seu navegador para acessar o dashboard interativo.
