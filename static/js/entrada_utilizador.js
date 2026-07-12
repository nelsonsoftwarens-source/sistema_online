// ==========================================
// ENTRADA DE UTILIZADOR
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    // Mostrar/Ocultar senha
    document
        .getElementById("mostrarSenha")
        .addEventListener("change", function () {

            const senha = document.getElementById("senha");

            senha.type = this.checked ? "text" : "password";

        });

    // Botão Entrar
    document
        .getElementById("btnEntrar")
        .addEventListener("click", entrarSistema);

    // ENTER
    document
        .getElementById("utilizador")
        .addEventListener("keypress", function (e) {

            if (e.key === "Enter") {

                document.getElementById("senha").focus();

            }

        });

    document
        .getElementById("senha")
        .addEventListener("keypress", function (e) {

            if (e.key === "Enter") {

                entrarSistema();

            }

        });

    // Cursor inicial
    document.getElementById("utilizador").focus();

});


// ==========================================
// LOGIN
// ==========================================

function entrarSistema() {

    let utilizador = document
        .getElementById("utilizador")
        .value
        .trim()
        .toLowerCase();

    let senha = document
        .getElementById("senha")
        .value;

    if (utilizador === "") {

        alert("Informe o utilizador.");

        document.getElementById("utilizador").focus();

        return;

    }

    if (senha === "") {

        alert("Informe a palavra-passe.");

        document.getElementById("senha").focus();

        return;

    }

    let botao = document.getElementById("btnEntrar");

    botao.disabled = true;

    botao.innerHTML = "A entrar...";

    fetch("/api/login_utilizador", {

        method: "POST",

        headers: {

            "Content-Type": "application/json"

        },

        body: JSON.stringify({

            utilizador: utilizador,

            senha: senha

        })

    })

    .then(response => response.json())

    .then(resultado => {

        botao.disabled = false;

        botao.innerHTML = "Entrar";

        if (resultado.sucesso) {

            window.location.href = "/painel";

        }
        else {

            alert(resultado.mensagem);

            document.getElementById("senha").value = "";

            document.getElementById("senha").focus();

        }

    })

    .catch(erro => {

        console.error(erro);

        botao.disabled = false;

        botao.innerHTML = "Entrar";

        alert("Erro ao comunicar com o servidor.");

    });

}