import string
import random
import json
import os
from flask import Flask, render_template_string, redirect, request, abort

app = Flask(__name__)

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)

# Nome do arquivo onde os links serão salvos
ARQUIVO_BD = "links.json"

def carregar_dados():
    """Carrega os links do arquivo JSON. Se o arquivo não existir, retorna um dicionário vazio."""
    if os.path.exists(ARQUIVO_BD):
        try:
            with open(ARQUIVO_BD, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Se o arquivo estiver corrompido ou vazio, retorna vazio
            return {}
    return {}

def salvar_dados(dados):
    """Salva o dicionário de links atualizado no arquivo JSON."""
    with open(ARQUIVO_BD, "w", encoding="utf-8") as f:
        # indent=4 deixa o arquivo fácil de ler se você abri-lo no bloco de notas
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Inicializa o "banco de dados" carregando o que já estava salvo no arquivo
url_banco_dados = carregar_dados()

def gerar_codigo_unico():
    """Gera um código aleatório de 5 caracteres (letras e números)"""
    caracteres = string.ascii_letters + string.digits
    while True:
        codigo = ''.join(random.choice(caracteres) for _ in range(5))
        if codigo not in url_banco_dados:
            return codigo

# Template HTML simples embutido para não precisar de arquivos extras agora
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Encurtador de URL</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='estilo.css') }}">
</head>
<body>
    <h2>Encurtador de URL</h2>
    <form method="POST">
        <input type="url" name="url_longa" placeholder="Cole sua URL longa aqui (ex: https://google.com)" required>
        <input type="submit" value="Encurtar">
    </form>


    <h4>Precisa de ajuda? Clique <a href="{{ url_for('static', filename='ajuda.html') }}" style="text-decoration: none">aqui</a> para saber mais</h4>

    {% if url_encurtada %}
        <div class="resultado">
            <strong>URL Encurtada:</strong> <a href="{{ url_encurtada }}" target="_blank">{{ url_encurtada }}</a>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    url_encurtada = None
    if request.method == "POST":
        url_longa = request.form.get("url_longa")
        
        if not url_longa.startswith(("http://", "https://")):
            url_longa = "https://" + url_longa
            
        codigo = gerar_codigo_unico()
        
        # 1. Adiciona no dicionário em memória
        url_banco_dados[codigo] = url_longa
        
        # 2. Salva o dicionário atualizado no arquivo local (.json)
        salvar_dados(url_banco_dados)
        
        url_encurtada = request.host_url + codigo

    return render_template_string(HTML_TEMPLATE, url_encurtada=url_encurtada)

@app.route("/<codigo>")
def redirecionar(codigo):
    # Busca o código no "banco de dados"
    url_longa = url_banco_dados.get(codigo)
    if url_longa:
        return redirect(url_longa)
    else:
        return abort(404, description="URL não encontrada")

if __name__ == "__main__":
    app.run(debug=True)
