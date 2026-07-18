import requests


URL_WHATSAPP = "https://sistema-online-icnn.onrender.com/enviar"


def enviar_whatsapp(
        empresa_id,
        telefone,
        mensagem
):

    try:

        resposta = requests.post(

            URL_WHATSAPP,

            json={

                "empresa_id": empresa_id,

                "telefone": telefone,

                "mensagem": mensagem

            },

            timeout=15

        )

        return resposta.json()

    except Exception as e:

        print("ERRO WHATSAPP:", e)

        return {

            "sucesso": False,

            "mensagem": str(e)

        }