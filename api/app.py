from flask import Flask, render_template,request


app = Flask(__name__,template_folder='templates')

@app.route('/')
def index():
    # Caminho para o arquivo .bat
    # caminho_bat = r'C:\Users\HP\Desktop\CE Alerta\executarMain.bat'

    # Executa o arquivo .bat
    # subprocess.run(caminho_bat, shell=True)
    return render_template('index.html')

@app.route('/AMSPrevisao',methods=['GET'])
def AMSprev():
    cidade = request.args.get('capital')
    modelos = request.args.getlist('model')
    return render_template('AMSprev.html',cidade=cidade,modelos=modelos)

if __name__ == '__main__':
    app.run(debug=True)
