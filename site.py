from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/vender", methods=["POST"])
def vender():

    cliente = request.form.get("cliente")
    total = request.form.get("total")

    requests.post(
        "http://127.0.0.1:3000/novo_pedido",
        json={
            "cliente": cliente,
            "total": total
        }
    )

    return "VENDA ENVIADA PARA O SISTEMA!"

if __name__ == "__main__":
    app.run(port=3000, debug=True)