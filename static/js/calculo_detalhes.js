document.addEventListener("DOMContentLoaded", function(){


    document.querySelectorAll(".entregue")
    .forEach(function(campo){


        campo.addEventListener("input", function(){

            atualizarQuantidade(this.dataset.id, "entregue");

        });


    });



    document.querySelectorAll(".recusado")
    .forEach(function(campo){


        campo.addEventListener("input", function(){

            atualizarQuantidade(this.dataset.id, "recusado");

        });


    });



});





function atualizarQuantidade(id, origem){


    let entregue = document.querySelector(
        '.entregue[data-id="'+id+'"]'
    );


    let recusado = document.querySelector(
        '.recusado[data-id="'+id+'"]'
    );



    let pedida = parseFloat(
        entregue.dataset.pedida
    ) || 0;



    if(origem === "entregue"){


        let valor = parseFloat(
            entregue.value
        ) || 0;



        if(valor > pedida){

            valor = pedida;

            entregue.value = pedida;

        }



        recusado.value =
            (pedida - valor).toFixed(2);



    }else{



        let valor = parseFloat(
            recusado.value
        ) || 0;



        if(valor > pedida){

            valor = pedida;

            recusado.value = pedida;

        }



        entregue.value =
            (pedida - valor).toFixed(2);



    }



}