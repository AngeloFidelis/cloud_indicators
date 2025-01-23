from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import logging
from datetime import date
from old_projects import old_projects
from area_consultants import area_consultants
from current_projects import current_projects
from consultant_allocation import consultant_allocation

current_year = date.today().year #Pega o ano atual
logging.basicConfig(level=logging.INFO) # Registra os logs acima do INFO (como warning ou error)

app = Flask(__name__) #Inicializa o Flask com o nome do módulo (__main__)
app.secret_key = os.urandom(12) #Gera uma chave secreta aleatória para proteger os dados de sessões e cookies
app.folder_static = "static" #Define a pasta onde o CSS está salvo

def catch_board_ids(board):
  print(*board)

#Cria a rota raiz que será usada para acessar a interface gráfica no browser
@app.route('/', methods=["get"])
def index():
    return render_template("home/index.html") #Renderiza a página home
  
#Rota para pegar todos os dados dos projetos antigos
@app.route('/old_projects', methods=["POST", "GET"])
def old_projects_function():
    old_projects()
    return redirect(url_for("index"))
  
#Rota para pegar todos os dados dos novos projetos
@app.route('/current_projects', methods=["POST", "GET"])
def current_projects_function():
    current_projects()
    return redirect(url_for("index"))
  
@app.route('/consultant_allocation', methods=["POST", "GET"])
def consultant_allocation_function():
    df_area_consultants = area_consultants()
    consultant_allocation(df_area_consultants)
    return redirect(url_for("index"))


#Executa a aplicação na porta 8080 com acesso a toda a Internet
if __name__ == "__main__":
  app.run(debug=True,host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))