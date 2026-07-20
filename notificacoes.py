import requests


URL_WHATSAPP = "https://whatsapp-service-yjxd.onrender.com/enviar"


def enviar_whatsapp(
        empresa_id,
        telefone,
        mensagem
):

    try:

        resposta = requests.post(

            URL_WHATSAPP,

            json={

                "empresa_id": str(empresa_id),

                "telefone": telefone,

                "mensagem": mensagem

            },

            timeout=15

        )


        print(
            "RESPOSTA NODE WHATSAPP:",
            resposta.text
        )


        return resposta.json()


    except Exception as e:

        print(
            "ERRO WHATSAPP:",
            e
        )

        return {

            "sucesso": False,

            "mensagem": str(e)

        }