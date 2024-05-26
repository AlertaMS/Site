from flask import Flask, render_template,request
import geradordefiguras as gdf
import os
current_directory = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/AMSPrevisao',methods=['GET'])
def AMSprev():
    cidade = request.args.get('capital')
    modelos = request.args.getlist('model')

    if cidade and modelos:
        
        previsoes = gdf.get_raw_file_data(repo_url='https://github.com/AlertaMS/Previsao',pasta='previsao_2024-05-26')

        gdf.plot_graf_temp(previsoes,cidade, modelos)
    return render_template('AMSprev.html',cidade=cidade,modelos=modelos)

if __name__ == '__main__':
    app.run(debug=True)
