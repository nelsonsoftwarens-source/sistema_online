// =====================================
// NOVO UTILIZADOR
// =====================================

function novoUtilizador(){

    limparFormulario();

}



// =====================================
// LIMPAR FORMULÁRIO
// =====================================

function limparFormulario(){


    document.getElementById("uuid").value = "";

    document.getElementById("nome").value = "";

    document.getElementById("utilizador").value = "";

    document.getElementById("senha").value = "";

    document.getElementById("confirmar_senha").value = "";

    document.getElementById("cargo").value = "";

    document.getElementById("telefone").value = "";

    document.getElementById("email").value = "";


    document.getElementById("activo").checked = true;

    document.getElementById("administrador").checked = false;


}




// =====================================
// GUARDAR UTILIZADOR
// =====================================

function guardarUtilizador(){


    let dados = {


        nome:
        document.getElementById("nome").value,


        utilizador:
        document.getElementById("utilizador").value,


        senha:
        document.getElementById("senha").value,


        confirmar_senha:
        document.getElementById("confirmar_senha").value,


        cargo:
        document.getElementById("cargo").value,


        telefone:
        document.getElementById("telefone").value,


        email:
        document.getElementById("email").value,


        activo:
        document.getElementById("activo").checked,


        administrador:
        document.getElementById("administrador").checked


    };



    if(dados.senha !== dados.confirmar_senha){

        alert(
            "As palavras-passe não coincidem!"
        );

        return;

    }




    fetch("/api/utilizador",{


        method:"POST",


        headers:{


            "Content-Type":
            "application/json"


        },


        body:
        JSON.stringify(dados)


    })


    .then(r=>r.json())


    .then(d=>{


        if(d.sucesso){


            alert(
                "Utilizador registado com sucesso!"
            );


            location.reload();



        }else{


            alert(
                d.mensagem
            );


        }


    });



}






// =====================================
// ABRIR UTILIZADOR
// =====================================

function abrirUtilizador(uuid){



    fetch(
        "/api/utilizador/"+uuid
    )


    .then(
        r=>r.json()
    )


    .then(
        d=>{


            document.getElementById("uuid").value =
            d.uuid;



            document.getElementById("nome").value =
            d.nome || "";



            document.getElementById("utilizador").value =
            d.utilizador || "";



            document.getElementById("cargo").value =
            d.cargo || "";



            document.getElementById("telefone").value =
            d.telefone || "";



            document.getElementById("email").value =
            d.email || "";



            document.getElementById("activo").checked =
            d.activo;



            document.getElementById("administrador").checked =
            d.administrador;



            document.getElementById("senha").value = "";

            document.getElementById("confirmar_senha").value = "";



            window.scrollTo({

                top:0,

                behavior:"smooth"

            });



        }

    );


}






// =====================================
// ATUALIZAR UTILIZADOR
// =====================================

function atualizarUtilizador(){



    let uuid =
    document.getElementById("uuid").value;



    if(!uuid){


        alert(
            "Selecione um utilizador primeiro"
        );


        return;


    }





    let dados = {


        uuid:uuid,


        nome:
        document.getElementById("nome").value,


        utilizador:
        document.getElementById("utilizador").value,


        senha:
        document.getElementById("senha").value,


        cargo:
        document.getElementById("cargo").value,


        telefone:
        document.getElementById("telefone").value,


        email:
        document.getElementById("email").value,


        activo:
        document.getElementById("activo").checked,


        administrador:
        document.getElementById("administrador").checked


    };





    fetch("/api/utilizador/atualizar",{


        method:"POST",


        headers:{


            "Content-Type":
            "application/json"


        },


        body:
        JSON.stringify(dados)



    })


    .then(r=>r.json())


    .then(d=>{


        if(d.sucesso){


            alert(
                "Utilizador atualizado!"
            );


            location.reload();


        }else{


            alert(
                d.mensagem
            );


        }


    });



}






// =====================================
// PESQUISA
// =====================================


document
.getElementById("filtro-utilizador")
.addEventListener(
"keyup",
function(){


    let texto =
    this.value.toLowerCase();




    document
    .querySelectorAll(
        "#tbody-utilizadores tr"
    )
    .forEach(
    linha=>{


        let nome =
        linha.dataset.nome;



        let user =
        linha.dataset.utilizador;



        if(

            nome.includes(texto)

            ||

            user.includes(texto)

        ){


            linha.style.display="";


        }else{


            linha.style.display="none";


        }



    });



});






// =====================================
// MODAL
// =====================================


function fecharModalUtilizador(){


    document
    .getElementById(
        "modalUtilizador"
    )
    .style.display="none";


}