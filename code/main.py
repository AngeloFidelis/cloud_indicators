from projects_opt import projects_opt
from consultor_allocation import consultor_allocation
from projects_old_opts import projects_old_opts
from flask import Flask, request, render_template, redirect, url_for, flash
import os
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.folder_static = "static"

@app.route('/', methods=["get"])
def index():
    return render_template("home/index.html")

@app.route('/projetos_historicos', methods=["POST", "GET"])
def projetos_historicos():
    projects_old_opts()
    return redirect(url_for("index"))

@app.route('/projetos_atuais', methods=["POST", "GET"])
def projetos_atuais():
    message = projects_opt()
    flash(message)
    return redirect(url_for("index"))

@app.route('/dados_consultores', methods=["POST", "GET"])
def dados_consultores():
    message = consultor_allocation()
    flash(message)
    return redirect(url_for("index"))


@app.route('/run-task', methods=["POST", "GET"])
def main():
    try:
        if request.method == "GET":
            consultor_allocation()
            projects_opt()  # Verifique se essa função está gerando algum erro
            return 'Sincronização feita', 200
        return 'Method Not Allowed', 405
    except Exception as e:
        logging.error(f"Erro durante execução: {e}")
        return f"Erro: {str(e)}", 500
    
if __name__ == "__main__":
  app.run(debug=True,host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))