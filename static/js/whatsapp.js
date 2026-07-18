const API_WHATSAPP =
"http://localhost:3001";



function empresa(){

    return document
    .getElementById(
        "empresa_id"
    )
    .value;

}



// =================================
// CONECTAR
// =================================

function conectarWhatsApp(){


    fetch(

        API_WHATSAPP+
        "/conectar",

        {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"

            },

            body:JSON.stringify({

                empresa_id:
                empresa()

            })

        }

    )

    .then(r=>r.json())

    .then(d=>{


        alert(
            d.mensagem
        );


        verificarQR();


    });


}



// =================================
// BUSCAR QR
// =================================

function verificarQR(){


    let intervalo =
    setInterval(()=>{


        fetch(

        API_WHATSAPP+
        "/qr/"+
        empresa()

        )


        .then(r=>r.json())


        .then(d=>{


            if(d.qr){


                let img =
                document.getElementById(
                    "qr"
                );


                img.src =
                d.qr;


                img.style.display=
                "block";


            }


            verificarEstado();


        });


    },3000);


}



// =================================
// ESTADO
// =================================

function verificarEstado(){


    fetch(

    API_WHATSAPP+
    "/status/"+
    empresa()

    )


    .then(r=>r.json())


    .then(d=>{


        let estado =
        document.getElementById(
            "estado"
        );


        if(d.conectado){


            estado.innerHTML=
            "🟢 WhatsApp conectado";


            document
            .getElementById(
                "telefone"
            )
            .innerHTML=

            "Número: "
            +
            d.telefone;


        }
        else{


            estado.innerHTML=
            "🔴 Desligado";


        }


    });


}



// =================================
// DESLIGAR
// =================================

function desconectarWhatsApp(){


fetch(

API_WHATSAPP+
"/desconectar",

{

method:"POST",

headers:{

"Content-Type":
"application/json"

},

body:JSON.stringify({

empresa_id:
empresa()

})

}

)

.then(r=>r.json())

.then(d=>{


alert(
"WhatsApp desligado"
);


});

}


setInterval(

verificarEstado,

5000

);