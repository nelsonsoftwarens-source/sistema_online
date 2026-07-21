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

    empresa,

    telefone,

    mensagem

){

    try{

        const sessao =
        sessoes[empresa];

        if(!sessao){

            throw new Error(
                "WhatsApp não conectado para esta empresa."
            );

        }

        if(!sessao.conectado){

            throw new Error(
                "WhatsApp não conectado."
            );

        }

        const sock =
        sessao.socket;


        console.log("Telefone recebido:", telefone);


        let numero =
        telefone.replace(/\D/g,'');


        if(numero.length == 9){

            numero = "258" + numero;

        }


        console.log("Número final:", numero);


        const existe =
        await sock.onWhatsApp(numero);


        console.log("onWhatsApp:", existe);


        if(!existe || existe.length == 0){

            throw new Error(
                "Número não existe no WhatsApp."
            );

        }


        const jid =
        existe[0].jid;


        console.log("JID:", jid);


        await sock.sendMessage(

            jid,

            {
                text: mensagem
            }

        );


        console.log("Mensagem enviada com sucesso.");


        return true;

    }

    catch(e){

        console.log(
            "ERRO ENVIO WHATSAPP:",
            e
        );

        throw e;

    }

}

async function conectarEmpresa(empresa) {

    // Se já existe uma sessão ligada, não cria outra
    if (
        sessoes[empresa] &&
        sessoes[empresa].socket &&
        sessoes[empresa].conectado
    ) {

        console.log(
            "Sessão já conectada:",
            empresa
        );

        return sessoes[empresa].socket;

    }

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

        qr: "",

        reconectando: false

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

            console.log(
                "UPDATE:",
                connection,
                qr ? "TEM QR" : "SEM QR"
            );

            if(qr){

                sessoes[empresa].qr =
                    await QRCode.toDataURL(qr);

                console.log(
                    "QR GERADO:",
                    empresa
                );

            }

            if(connection === "open"){

                sessoes[empresa].conectado = true;

                sessoes[empresa].telefone =
                    sock.user.id;

                sessoes[empresa].reconectando = false;

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

            if(connection === "close"){

                const motivo =
                    lastDisconnect?.error?.output?.statusCode;

                console.log(
                    "CONEXÃO FECHADA:",
                    motivo
                );

                sessoes[empresa].conectado = false;

                await salvarWhatsApp(
                    empresa,
                    "",
                    "DESCONECTADO"
                );

                if(
                    motivo !== DisconnectReason.loggedOut &&
                    !sessoes[empresa].reconectando
                ){

                    sessoes[empresa].reconectando = true;

                    console.log(
                        "Tentando reconectar..."
                    );

                    setTimeout(async()=>{

                        try{

                            if(sessoes[empresa]?.socket){

                                try{

                                    sock.end();

                                }catch{}

                            }

                            delete sessoes[empresa];

                            await conectarEmpresa(
                                empresa
                            );

                        }

                        catch(e){

                            console.log(
                                "Erro reconectando:",
                                e.message
                            );

                        }

                    },5000);

                }

            }

        }

    );

    return sock;

}

function obterSessao(empresa){

    return sessoes[empresa];

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