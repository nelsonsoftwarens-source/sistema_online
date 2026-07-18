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


async function salvarWhatsApp(

    empresa,

    telefone,

    estado

){

    try{


        await db.query(

        `

        INSERT INTO whatsapp_config

        (

            empresa_id,

            telefone,

            estado,

            ultima_conexao

        )

        VALUES

        (

            $1,

            $2,

            $3,

            NOW()

        )


        ON CONFLICT

        (empresa_id)

        DO UPDATE SET


            telefone = EXCLUDED.telefone,

            estado = EXCLUDED.estado,

            ultima_conexao = NOW()

        `,

        [

            empresa,

            telefone,

            estado

        ]

        );


        console.log(
            "WhatsApp gravado:",
            empresa,
            estado
        );


    }
    catch(e){

        console.log(
            "ERRO DATABASE:",
            e.message
        );

    }

}



module.exports = {

    db,

    salvarWhatsApp

};