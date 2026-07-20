const {
    salvarWhatsApp
}=require("./database");

const {
    default: makeWASocket,
    DisconnectReason,
    useMultiFileAuthState,
    fetchLatestBaileysVersion
} = require("@whiskeysockets/baileys");

const P = require("pino");
const path = require("path");
const QRCode = require("qrcode");

const sessoes = {};

// ======================================
// ENVIAR MENSAGEM WHATSAPP POR EMPRESA
// ======================================

async function enviarMensagem(

    empresa_id,

    telefone,

    mensagem

){


    try{


        const sock =
        sessoes[empresa_id];



        if(!sock){


            throw new Error(

                "WhatsApp não conectado para esta empresa."

            );

        }



        let numero = 
        telefone
        .replace(/\D/g,'');



        if(numero.length < 9){


            throw new Error(

                "Número de telefone inválido."

            );

        }



        const jid =
        numero + "@s.whatsapp.net";



        await sock.sendMessage(

            jid,

            {

                text: mensagem

            }

        );



        console.log(

            "Mensagem enviada:",

            empresa_id,

            telefone

        );



        return true;


    }

    catch(e){


        console.log(

            "ERRO ENVIO WHATSAPP:",

            e.message

        );


        throw e;


    }


}

async function conectarEmpresa(empresa) {

    const pastaSessao = path.join(
        __dirname,
        "sessions",
        empresa
    );

    const {
        state,
        saveCreds
    } = await useMultiFileAuthState(
        pastaSessao
    );

    const {
        version
    } = await fetchLatestBaileysVersion();

    const sock = makeWASocket({

        version,

        auth: state,

        printQRInTerminal: false,

        logger: P({
            level: "silent"
        })

    });

    sessoes[empresa] = {

        socket: sock,

        conectado: false,

        telefone: "",

        qr: ""

    };

    sock.ev.on(
        "creds.update",
        saveCreds
    );

    sock.ev.on(
        "connection.update",
        async(update)=>{

            const {

                connection,

                lastDisconnect,

                qr

            } = update;

            if(qr){

                sessoes[empresa].qr =
                    await QRCode.toDataURL(qr);

                console.log(
                    "QR GERADO:",
                    empresa
                );

            }

            if(connection=="open"){


                sessoes[empresa].conectado=true;


                sessoes[empresa].telefone =
                sock.user.id;



                await salvarWhatsApp(

                    empresa,

                    sock.user.id,

                    "CONECTADO"

                );

                console.log(

                    empresa,

                    "CONECTADO"

                );

            }

            if(connection=="close"){


                sessoes[empresa].conectado=false;



                await salvarWhatsApp(

                    empresa,

                    "",

                    "DESCONECTADO"

                );


            }

        }

    );

    return sock;

}

function obterSessao(empresa){

    return sessoes[empresa];

}



// =====================================
// ENVIAR MENSAGEM
// =====================================

async function enviarMensagem(
    empresa,
    telefone,
    mensagem
){

    const sessao =
    sessoes[empresa];


    if(!sessao){

        throw new Error(
            "Empresa sem sessão WhatsApp"
        );

    }


    if(!sessao.conectado){

        throw new Error(
            "WhatsApp não conectado"
        );

    }


    let numero =
    telefone.replace(
        /\D/g,
        ""
    );


    // Mozambique
    // adiciona 258 se necessário

    if(numero.length == 9){

        numero =
        "258" + numero;

    }



    const jid =
    numero + "@s.whatsapp.net";


    await sessao.socket.sendMessage(

        jid,

        {
            text: mensagem
        }

    );


    console.log(
        "Mensagem enviada:",
        numero
    );


    return true;

}

async function restaurarSessoes(){

    const pasta =
    path.join(
        __dirname,
        "sessions"
    );


    if(!require("fs").existsSync(pasta)){
        return;
    }


    const empresas =
    require("fs")
    .readdirSync(pasta);


    for(const empresa of empresas){

        console.log(
            "Restaurando sessão:",
            empresa
        );


        try{

            await conectarEmpresa(
                empresa
            );


        }catch(e){

            console.log(
                "Erro restaurando:",
                empresa,
                e.message
            );

        }

    }

}

module.exports = {

    conectarEmpresa,

    obterSessao,

    enviarMensagem,

    restaurarSessoes

};