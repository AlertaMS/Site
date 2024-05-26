from flask import Flask, render_template,request
import requests
import pandas as pd
import plotly.graph_objects as go


def get_raw_file_data(repo_url, pasta='',formato = '.csv', token=None):
    # Obtém a URL do repositório
    if not repo_url.endswith('/'):
        repo_url += '/'
    api_url = repo_url.replace('github.com', 'api.github.com/repos') + 'contents/' + pasta

    # Prepara os cabeçalhos com o token de acesso pessoal para autenticação
    headers = {'Authorization': f'token {token}'} if token else {}

    # Envia uma solicitação GET para a API do GitHub para obter os conteúdos do repositório
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print("Erro ao acessar o repositório:", response.status_code)
        return {}

    # Analisa a resposta JSON
    contents = response.json()

    # Extrai os dados brutos dos arquivos
    raw_file_data = {}
    for item in contents:
        if item['type'] == 'file' and item['name'].endswith(formato):  # Adapte para o formato do seu arquivo
            file_url = item['download_url']
            file_name = item['name']
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                raw_file_data[file_name] = file_url  # Supondo que seja um arquivo de texto
            else:
                print(f"Erro ao obter o arquivo '{file_name}':", file_response.status_code)

    return raw_file_data
dict_modelos = {
    "ecmwf_cf": "ECMWF CF",
    "ecmwf_fc": "ECMWF FC",
    "GFS_thredds": "GFS",
    "rjtd_cf": "JMA",
    "dwd_fc": "DWD"
}
dic_temp = {'temp_max':'max','temp_min':'min'}
plotly_buttons = [
    "zoom2d",                   # Ferramenta de zoom para gráficos 2D
    "pan2d",                    # Ferramenta de panorâmica para gráficos 2D
    "lasso2d",                  # Ferramenta de seleção laço para gráficos 2D
    "zoomIn2d",                 # Ferramenta de zoom in para gráficos 2D
    "zoomOut2d",                # Ferramenta de zoom out para gráficos 2D
    "autoScale2d",              # Reajustar automaticamente o gráfico 2D
    "hoverClosestCartesian",    # Mostrar o ponto mais próximo no gráfico cartesiano
    "hoverCompareCartesian",    # Mostrar a comparação dos valores no gráfico cartesiano
    "hoverClosestGl2d",         # Mostrar o ponto mais próximo no gráfico WebGL 2D
    "hoverClosestPie",          # Mostrar o ponto mais próximo no gráfico de pizza
    "toggleHover",              # Alternar a exibição das etiquetas de hover
    "resetViewMapbox"           # Redefinir a vista do gráfico Mapbox
]                                
def plot_graf_temp(estacoes,previsoes,cidade, modelos):
    nome_arq = [i for i in estacoes if i.startswith(cidade) and i.endswith('.txt')][0]
    estacoes = pd.read_table(estacoes[nome_arq],sep='\t')['Estacao']
    estacoes = estacoes.astype(str)
    print('\n',estacoes,nome_arq)
    fig = go.Figure()
    for modelo in modelos:
        df = pd.read_table(previsoes[[i for i in previsoes if i.startswith(modelo)][0]],sep='\t')
        df['Cod_estacao'] = df['Cod_estacao'].astype(str)
        for estacao in estacoes:
            for temp in ['temp_max','temp_min']:
                df_ = df[df['Cod_estacao'] == estacao]
                print(df_)
                fig.add_trace(go.Scatter(
                    x=df_['date_time'],
                    y=df_[temp],
                    mode='markers',
                    name=dic_temp[temp]+'-'+str(estacao)+'-'+str(dict_modelos[modelo]))
                    )
                fig.update_layout(
                    xaxis_title="Data e Hora",
                    yaxis_title="Temperatura (°C)",
                    legend_title="Modelos",
                    legend=dict(
                        orientation="h",  # Define a orientação da legenda para horizontal (em cima)
                        yanchor="top",  # Define o ponto de ancoragem da legenda como o topo
                        y=1.15,  # Define a posição vertical da legenda
                        xanchor="left",  # Define o ponto de ancoragem horizontal da legenda como a direita
                        x=-0.015  # Define a posição horizontal da legenda
                        ),
                    margin=dict(l=2, r=1, t=20, b=2),
                    showlegend=True,  # Mantém a legenda visível
                    )
    fig.write_html(f"./templates/grafico.html",config={'modeBarButtonsToRemove': plotly_buttons,'displaylogo': False})






app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/AMSPrevisao',methods=['GET'])
def AMSprev():
    cidade = request.args.get('capital')
    modelos = request.args.getlist('model')

    if cidade and modelos:
        previsoes = get_raw_file_data(repo_url='https://github.com/AlertaMS/Previsao',pasta='previsao_2024-05-26')
        estacoes = get_raw_file_data(repo_url='https://github.com/AlertaMS/Previsao',pasta='Estacoes',formato='.txt')
        plot_graf_temp(estacoes,previsoes,cidade, modelos)
    return render_template('AMSprev.html',cidade=cidade,modelos=modelos)

if __name__ == '__main__':
    app.run(debug=True)
