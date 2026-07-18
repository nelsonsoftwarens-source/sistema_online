let itens = [];


// =====================================
// ADICIONAR PRODUTO
// =====================================

function adicionarProduto(el){

    let card = el.closest(".card-produto");


    let id = card.dataset.id;
    let nome = card.dataset.nome;


    let campoQtd = document.getElementById(
        "qtd-" + id
    );


    let qtd = parseInt(campoQtd.value) || 1;



    let existente = itens.find(
        item => item.id == id
    );



    if(existente){


        existente.qtd += qtd;


    }else{


        itens.push({

            id:id,

            nome:nome,

            qtd:qtd

        });


    }



    renderItens();


    campoQtd.value = 1;


}





// =====================================
// REMOVER ITEM
// =====================================

function removerProduto(id){


    itens = itens.filter(
        item => item.id != id
    );


    renderItens();

}





// =====================================
// ALTERAR QUANTIDADE
// =====================================

function alterarQtd(id, valor){


    let item = itens.find(
        i => i.id == id
    );


    if(item){


        item.qtd = parseInt(valor) || 1;


    }


    renderItens();


}





// =====================================
// MOSTRAR CARRINHO
// =====================================

function renderItens(){


    let tbody = document.querySelector(
        "#tabela-carrinho tbody"
    );


    tbody.innerHTML = "";



    let total = 0;



    itens.forEach(item => {


        total += item.qtd;



        tbody.innerHTML += `


        <tr>


            <td>

                ${item.nome}

            </td>


            <td>


                <input

                type="number"

                min="1"

                value="${item.qtd}"

                onchange="
                alterarQtd('${item.id}',this.value)
                "

                style="
                width:60px;
                ">


            </td>



            <td>


                <button

                class="btn btn-danger btn-sm"

                onclick="
                removerProduto('${item.id}')
                ">

                ❌

                </button>


            </td>


        </tr>


        `;



    });



    document.getElementById(
        "total-geral"
    ).innerHTML = total + " itens";



}







// =====================================
// FILTRO PRODUTOS
// =====================================


document
.getElementById("filtro-produtos")
.addEventListener(
"keyup",
function(){



    let texto =
    this.value.toLowerCase();



    let cards =
    document.querySelectorAll(
        ".card-produto"
    );



    cards.forEach(card => {



        let nome =
        card.dataset.nome
        .toLowerCase();



        if(nome.includes(texto)){


            card.style.display =
            "block";


        }else{


            card.style.display =
            "none";


        }



    });



});








// =====================================
// GUARDAR REQUISIÇÃO
// =====================================
function guardarRequisicao(){


    if(itens.length == 0){

        alert(
            "Adicione produtos primeiro"
        );

        return;

    }



    let destino =
    document.getElementById(
        "destino"
    ).value;



    let fiel =
    document.getElementById(
        "fiel_armazem"
    ).value;



    let fiel_nome =
    document.getElementById(
        "fiel_armazem"
    ).options[
        document.getElementById(
            "fiel_armazem"
        ).selectedIndex
    ].text;



    let responsavel =
    document.getElementById(
        "responsavel"
    ).value
    .trim()
    .toUpperCase();



    let observacao =
    document.getElementById(
        "observacao"
    ).value;



    if(!destino){

        alert(
            "Selecione o setor"
        );

        return;

    }



    if(!fiel){

        alert(
            "Selecione o Fiel de Armazém"
        );

        document.getElementById(
            "fiel_armazem"
        ).focus();

        return;

    }



    if(!responsavel){

        alert(
            "Informe o responsável do setor"
        );

        document.getElementById(
            "responsavel"
        ).focus();

        return;

    }



    let dados = {


        destino: destino,


        fiel_uuid: fiel,


        fiel_nome: fiel_nome,


        responsavel: responsavel,


        observacao: observacao,


        itens: itens


    };



    fetch(
        "/api/enviar_requisicao",
        {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"

            },

            body:
            JSON.stringify(dados)

        }

    )


    .then(
        response => response.json()
    )


    .then(
        resultado => {


            if(resultado.sucesso){


                alert(
                    "📦 Requisição enviada com sucesso!"
                );


                itens = [];


                document.getElementById(
                    "responsavel"
                ).value = "";


                document.getElementById(
                    "observacao"
                ).value = "";


                document.getElementById(
                    "fiel_armazem"
                ).selectedIndex = 0;


                renderItens();



            }else{


                alert(
                    resultado.mensagem ||
                    "Erro ao guardar"
                );


            }


        }

    )


    .catch(
        erro => {


            console.error(
                erro
            );


            alert(
                "Erro de comunicação"
            );


        }

    );

}