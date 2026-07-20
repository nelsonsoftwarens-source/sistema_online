const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;
// =====================================
// Estruturas em memória
// =====================================

const empresas = {};
const qrcodes = {};
const estados = {};

const { Pool } = require("pg");

const db = new Pool({

    host:"ep-wild-mountain-aq1zicdl-pooler.c-8.us-east-1.aws.neon.tech",

    user:"neondb_owner",

    password:"npg_2DJBuRIdt5jC",

    database:"neondb",

    port:5432,

    ssl:{
        rejectUnauthorized:false
    }

});



module.exports = {

    db

};

// =====================================
// Pastas
// =====================================

const {

    conectarEmpresa,

    obterSessao,

    enviarMensagem,

    restaurarSessoes

} = require("./whatsapp");


const SESSION_PATH = path.join(
    __dirname,
    "sessions"
);

const LOG_PATH = path.join(
    __dirname,
    "logs"
);

if (!fs.existsSync(SESSION_PATH))
    fs.mkdirSync(SESSION_PATH);

if (!fs.existsSync(LOG_PATH))
    fs.mkdirSync(LOG_PATH);


// =====================================
// Logger
// =====================================

function log(texto){

    const agora = new Date();

    const linha =
        "[" +
        agora.toLocaleString() +
        "] " +
        texto +
        "\n";

    console.log(linha);

    fs.appendFileSync(

        path.join(
            LOG_PATH,
            "service.log"
        ),

        linha

    );

}


// =====================================
// Empresa
// =====================================

function criarEmpresa(id){

    if(empresas[id])
        return;

    empresas[id]={

        id:id,

        conectado:false,

        telefone:null,

        qr:null,

        socket:null,

        ultimaLigacao:null,

        mensagens:0

    };

}


// =====================================
// STATUS
// =====================================

app.get(

"/status/:empresa",

(req,res)=>{

    const sessao =
    obterSessao(

        req.params.empresa

    );

    if(!sessao){

        return res.json({

            conectado:false

        });

    }

    res.json({

        conectado:
        sessao.conectado,

        telefone:
        sessao.telefone

    });

});


// =====================================
// QR
// =====================================

app.get(

"/qr/:empresa",

(req,res)=>{

    const sessao =
    obterSessao(

        req.params.empresa

    );

    if(!sessao){

        return res.json({

            qr:null

        });

    }

    res.json({

        qr:
        sessao.qr

    });

});


// =====================================
// CONECTAR
// =====================================

app.post(

"/conectar",

async(req,res)=>{

    try{

        const empresa =
        String(
            req.body.empresa_id
        );

        await conectarEmpresa(
            empresa
        );

        res.json({

            sucesso:true,

            mensagem:"Ligação iniciada"

        });

    }

    catch(e){

        console.log(e);

        res.json({

            sucesso:false,

            erro:e.message

        });

    }

});


// =====================================
// DESCONECTAR
// =====================================

app.post(

"/desconectar",

(req,res)=>{

    const empresa=req.body.empresa_id;

    criarEmpresa(
        empresa
    );

    empresas[empresa].conectado=false;

    empresas[empresa].telefone=null;

    empresas[empresa].socket=null;

    empresas[empresa].qr=null;

    log(

        "Empresa "
        +empresa+
        " desconectada"

    );

    res.json({

        sucesso:true

    });

});


// =====================================
// ROOT
// =====================================

app.get(

"/",

(req,res)=>{

    res.json({

        sistema:
        "NV WhatsApp Service",

        status:
        "ONLINE",

        empresas:

        Object.keys(
            empresas
        ).length

    });

});

// =====================================
// ENVIAR WHATSAPP
// =====================================

app.post(
"/enviar",
async(req,res)=>{

    try{

        const empresa =
        String(
            req.body.empresa_id
        );

        const telefone =
        req.body.telefone;

        const mensagem =
        req.body.mensagem;


        if(
            !empresa ||
            !telefone ||
            !mensagem
        ){

            return res.json({

                sucesso:false,

                mensagem:
                "Dados incompletos"

            });

        }


        await enviarMensagem(

            empresa,

            telefone,

            mensagem

        );


        res.json({

            sucesso:true,

            mensagem:
            "Mensagem enviada"

        });


    }
    catch(e){

        console.log(
            "ERRO WHATSAPP:",
            e.message
        );


        res.json({

            sucesso:false,

            mensagem:
            e.message

        });

    }

});

restaurarSessoes();

// =====================================

app.listen(

PORT,

()=>{

log(

"=================================="

);

log(

"NV WHATSAPP SERVICE"

);

log(

"PORTA "+PORT

);

log(

"ONLINE"

);

log(

"=================================="

);

});