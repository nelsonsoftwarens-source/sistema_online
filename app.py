from flask import Flask, request, jsonify, render_template, redirect, session
from conexao import conectar
import uuid
app = Flask(__name__)
app.secret_key = "nvsistema2025"

@app.route("/")
def inicio():

    if "login_id" not in session:
        return redirect("/login")

    return redirect("/painel")


@app.route("/api/salvar_empresa", methods=["POST"])
def salvar_empresa():

    dados = request.json

    login_id = dados.get("login_id")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM empresa
        WHERE login_id=%s
    """, (login_id,))

    existe = cur.fetchone()

    if existe:

        cur.execute("""
            UPDATE empresa
            SET
                nome=%s,
                nuit=%s,
                endereco=%s,
                telefone=%s
            WHERE login_id=%s
        """, (
            dados.get("nome"),
            dados.get("nuit"),
            dados.get("endereco"),
            dados.get("telefone"),
            login_id
        ))

    else:

        cur.execute("""
            INSERT INTO empresa (
                login_id,
                nome,
                nuit,
                endereco,
                telefone
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (
            login_id,
            dados.get("nome"),
            dados.get("nuit"),
            dados.get("endereco"),
            dados.get("telefone")
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "sucesso": True
    })
# ======================================================
# LOGIN
# ======================================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT le.id, e.id, e.nome
            FROM logins_empresa le
            JOIN empresa e ON e.login_id = le.id
            WHERE le.email = %s
            AND le.senha = %s
        """, (email, senha))

        row = cur.fetchone()

        if row:
            session["login_id"] = row[0]
            session["empresa_id"] = row[1]
            session["empresa_nome"] = row[2]

            return redirect("/")

        return "LOGIN INVALIDO"

    return render_template("login.html")
# ======================================================
# LOGOUT
# ======================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ======================================================
# VERIFICAR LOGIN
# ======================================================
def verificar_login():
    return "empresa_id" in session

# ======================================================
# PRODUTOS
# ======================================================
@app.route("/api/produtos")
def api_produtos():

    token = request.args.get("token")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT empresa_id
        FROM logins_empresa
        WHERE token = %s
    """, (token,))

    row = cur.fetchone()

    if not row:
        return jsonify({"erro": "TOKEN INVALIDO"}), 401

    empresa_id = row[0]

    cur.execute("""
        SELECT
            uuid,
            descricao,
            preco_venda,
            preco_compra,
            categoria,
            barcode,
            ativo
        FROM produtos
        WHERE empresa_id = %s
    """, (empresa_id,))

    produtos = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "uuid": p[0],
            "descricao": p[1],
            "preco_venda": float(p[2] or 0),
            "preco_compra": float(p[3] or 0),
            "categoria": p[4],
            "barcode": p[5],
            "ativo": p[6]
        }
        for p in produtos
    ])


@app.route("/produtos")
def produtos():

    if not verificar_login():
        return redirect("/login")

    empresa_id = session["empresa_id"]

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,
               descricao,
               preco_venda,
               preco_compra,
               categoria,
               barcode,
               ativo
        FROM produtos
        WHERE empresa_id = %s
        ORDER BY descricao
    """, (empresa_id,))

    produtos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "produtos.html",
        produtos=produtos
    )
# ======================================================
# SALVAR PRODUTO
# ======================================================
@app.route("/api/salvar_produto", methods=["POST"])
def salvar_produto():

    try:

        dados = request.json
        print("DADOS:", dados)
        print("UUID:", dados.get("uuid"))

        token = dados.get("token")

        empresa = obter_empresa_por_token(token)

        if not empresa:
            return jsonify({
                "erro": "TOKEN INVALIDO"
            }), 401

        empresa_id = empresa[0]

        conn = conectar()
        cur = conn.cursor()

        uuid_produto = dados.get("uuid")

        cur.execute("""
            SELECT id
            FROM produtos
            WHERE uuid = %s
              AND empresa_id = %s
        """, (
            uuid_produto,
            empresa_id
        ))

        existe = cur.fetchone()

        if existe:

            cur.execute("""
                UPDATE produtos
                SET
                    descricao=%s,
                    preco_venda=%s,
                    preco_compra=%s,
                    categoria=%s,
                    barcode=%s,
                    ativo=%s
                WHERE id=%s
            """, (
                dados.get("descricao"),
                dados.get("preco_venda"),
                dados.get("preco_compra"),
                dados.get("categoria"),
                dados.get("barcode"),
                dados.get("ativo"),
                existe[0]
            ))

        else:

            cur.execute("""
                INSERT INTO produtos (
                    uuid,
                    empresa_id,
                    descricao,
                    preco_venda,
                    preco_compra,
                    categoria,
                    barcode,
                    ativo
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                uuid_produto,
                empresa_id,
                dados.get("descricao"),
                dados.get("preco_venda"),
                dados.get("preco_compra"),
                dados.get("categoria"),
                dados.get("barcode"),
                dados.get("ativo")
            ))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        print("ERRO PRODUTO:", e)

        return jsonify({
            "error": str(e)
        }), 500

@app.route("/salvar_produto", methods=["POST"])
def salvar_produto_html():

    descricao = request.form.get("descricao")
    preco_venda = request.form.get("preco_venda")
    preco_compra = request.form.get("preco_compra")
    categoria = request.form.get("categoria")
    barcode = request.form.get("barcode")

    empresa_id = session["empresa_id"]

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO produtos
        (empresa_id, descricao, preco_venda, preco_compra, categoria, barcode, ativo)
        VALUES (%s,%s,%s,%s,%s,%s,TRUE)
    """, (
        empresa_id,
        descricao,
        preco_venda,
        preco_compra,
        categoria,
        barcode
    ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/produtos")

@app.route("/editar_produto/<int:id>")
def editar_produto(id):

    if "empresa_id" not in session:
        return redirect("/login")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, descricao, preco_venda, preco_compra, categoria, barcode
        FROM produtos
        WHERE id = %s AND empresa_id = %s
    """, (id, session["empresa_id"]))

    produto = cur.fetchone()

    cur.close()
    conn.close()

    if not produto:
        return "Produto não encontrado"

    return render_template("editar_produto.html", produto=produto)

@app.route("/atualizar_produto", methods=["POST"])
def atualizar_produto():

    if "empresa_id" not in session:
        return redirect("/login")

    id = request.form.get("id")
    descricao = request.form.get("descricao")
    preco_venda = request.form.get("preco_venda")
    preco_compra = request.form.get("preco_compra")
    categoria = request.form.get("categoria")
    barcode = request.form.get("barcode")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        UPDATE produtos
        SET descricao = %s,
            preco_venda = %s,
            preco_compra = %s,
            categoria = %s,
            barcode = %s
        WHERE id = %s AND empresa_id = %s
    """, (
        descricao,
        preco_venda,
        preco_compra,
        categoria,
        barcode,
        id,
        session["empresa_id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/produtos")

@app.route("/eliminar_produto/<int:id>")
def eliminar_produto(id):

    if "empresa_id" not in session:
        return redirect("/login")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM produtos
        WHERE id = %s AND empresa_id = %s
    """, (id, session["empresa_id"]))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/produtos")

def obter_empresa_por_token(token):

    token = token.strip()

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT empresa_id
        FROM logins_empresa
        WHERE TRIM(token) = TRIM(%s)
    """, (token,))

    empresa = cur.fetchone()

    cur.close()
    conn.close()

    return empresa
# ======================================================
# VENDAS
# ======================================================
@app.route("/vendas")
def vendas():

    if not verificar_login():
        return redirect("/login")

    empresa_id = session["empresa_id"]

    print("SESSION COMPLETA:", dict(session))
    print("EMPRESA ID:", session.get("empresa_id"))

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,
               descricao,
               preco_venda,
               categoria
        FROM produtos
        WHERE empresa_id = %s
        AND ativo = TRUE
        ORDER BY descricao
    """, (empresa_id,))

    produtos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "vendas.html",
        produtos=produtos
    )

@app.route("/vendas_online")
def vendas_online():

    if "empresa_id" not in session:
        return redirect("/login")

    empresa_id = session["empresa_id"]

    conn = conectar()
    cur = conn.cursor()

    query = """
        SELECT
            id,
            item,
            cliente,
            total,
            tiket_num,
            data_venda,
            forma_pagamento
        FROM vendas
        WHERE empresa_id = %s
    """

    params = [empresa_id]

    # filtros
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")
    produto = request.args.get("produto")
    ticket = request.args.get("ticket")

    if data_inicio and data_fim:
        query += " AND DATE(data_venda) BETWEEN %s AND %s"
        params += [data_inicio, data_fim]

    if produto:
        query += " AND item ILIKE %s"
        params.append(f"%{produto}%")

    if ticket:
        query += " AND tiket_num = %s"
        params.append(ticket)

    query += " ORDER BY id DESC"

    cur.execute(query, params)
    vendas = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("vendas_online.html", vendas=vendas)

@app.route("/api/vendas", methods=["GET"])
def api_vendas():

    token = request.args.get("token")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT empresa_id
        FROM logins_empresa
        WHERE token = %s
    """, (token,))

    empresa = cur.fetchone()

    if not empresa:
        return jsonify({"erro": "TOKEN INVALIDO"}), 401

    empresa_id = empresa[0]

    cur.execute("""
        SELECT
            barcode,
            cliente,
            item,
            tipo,
            preco,
            quantidade,
            total,
            pago,
            data_venda,
            registrado_por,
            forma_pagamento,
            tiket_num,
            origem,
            mesa_id,
            desconto,
            troco,
            impressoes,
            codigo_sessao
        FROM vendas
        WHERE empresa_id = %s
    """, (empresa_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "barcode": r[0],
            "cliente": r[1],
            "item": r[2],
            "tipo": r[3],
            "preco": r[4],
            "quantidade": r[5],
            "total": r[6],
            "pago": r[7],
            "data_venda": r[8],
            "registrado_por": r[9],
            "forma_pagamento": r[10],
            "tiket_num": r[11],
            "origem": r[12],
            "mesa_id": r[13],
            "desconto": r[14],
            "troco": r[15],
            "impressoes": r[16],
            "codigo_sessao": r[17]
        }
        for r in rows
    ])

@app.route("/api/salvar_venda", methods=["POST"])
def api_salvar_venda():

    try:
        dados = request.json
        token = dados.get("token")

        conn = conectar()
        cur = conn.cursor()

        # ==========================================
        # VALIDAR TOKEN
        # ==========================================
        cur.execute("""
            SELECT empresa_id
            FROM logins_empresa
            WHERE token = %s
        """, (token,))

        empresa = cur.fetchone()

        if not empresa:
            return jsonify({"erro": "TOKEN INVALIDO"}), 401

        empresa_id = empresa[0]

        # ==========================================
        # VERIFICAR DUPLICADO (ticket + item + barcode)
        # ==========================================
        cur.execute("""
            SELECT id
            FROM vendas
            WHERE empresa_id = %s
            AND tiket_num = %s
            AND barcode = %s
        """, (
            empresa_id,
            dados.get("tiket_num"),
            dados.get("barcode")
        ))

        existe = cur.fetchone()

        if existe:
            return jsonify({"status": "existente"}), 200

        # ==========================================
        # INSERT VENDA
        # ==========================================
        cur.execute("""
            INSERT INTO vendas (
                barcode,
                cliente,
                item,
                tipo,
                preco,
                quantidade,
                total,
                pago,
                data_venda,
                registrado_por,
                forma_pagamento,
                tiket_num,
                origem,
                mesa_id,
                desconto,
                troco,
                impressoes,
                codigo_sessao,
                empresa_id
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,
                %s,%s,NOW(),%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s
            )
        """, (
            dados.get("barcode"),
            dados.get("cliente"),
            dados.get("item"),
            "VENDA",
            dados.get("preco"),
            dados.get("quantidade"),
            dados.get("total"),
            dados.get("pago"),
            dados.get("registrado_por"),
            dados.get("forma_pagamento"),
            dados.get("tiket_num"),
            dados.get("origem"),
            dados.get("mesa_id"),
            dados.get("desconto"),
            dados.get("troco"),
            dados.get("impressoes"),
            dados.get("codigo_sessao"),
            empresa_id
        ))

        conn.commit()

        return jsonify({"status": "ok"})

    except Exception as e:
        print("ERRO VENDAS:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cur.close()
        conn.close()

@app.route("/finalizar_venda", methods=["POST"])
def finalizar_venda():

    if not verificar_login():
        return jsonify({"erro": "nao autenticado"}), 401

    empresa_id = session["empresa_id"]

    dados = request.json
    cliente = dados.get("cliente", "Consumidor Final")
    total = dados.get("total", 0)
    itens = dados.get("itens", [])

    conn = conectar()
    cur = conn.cursor()

    try:

        # ==========================================
        # PEDIDO WEB
        # ==========================================
        cur.execute("""
            INSERT INTO pedidos_web (
                empresa_id,
                cliente,
                total,
                estado
            )
            VALUES (%s,%s,%s,%s)
            RETURNING id
        """, (
            empresa_id,
            cliente,
            total,
            "PENDENTE"
        ))

        pedido_id = cur.fetchone()[0]

        # ==========================================
        # ITENS PEDIDO WEB
        # ==========================================
        for item in itens:

            cur.execute("""
                INSERT INTO pedidos_web_itens (
                    empresa_id,
                    pedido_id,
                    produto,
                    quantidade,
                    preco,
                    total
                )
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                empresa_id,
                pedido_id,
                item.get("nome"),
                item.get("qtd", 1),
                item.get("preco", 0),
                item.get("total", 0)
            ))

        # ==========================================
        # GERAR TICKET
        # ==========================================
        cur.execute("""
            SELECT COALESCE(MAX(tiket_num),0) + 1
            FROM tickets
            WHERE empresa_id = %s
        """, (empresa_id,))

        tiket_num = cur.fetchone()[0]

        # ==========================================
        # TICKET
        # ==========================================
        cur.execute("""
            INSERT INTO tickets (
                empresa_id,
                tiket_num,
                mesa,
                cliente,
                total,
                pago,
                data_venda,
                registrado_por,
                desconto,
                forma_pagamento,
                impressoes,
                tipo,
                valor_usado
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,
                NOW(),%s,%s,%s,%s,%s,%s
            )
        """, (
            empresa_id,
            tiket_num,
            "WEB",
            cliente,
            total,
            True,
            session.get("usuario", "WEB"),
            0,
            "WEB",
            0,
            "VENDA",
            0
        ))

        # ==========================================
        # VENDAS (HISTÓRICO ONLINE)
        # ==========================================
        for item in itens:

            cur.execute("""
                INSERT INTO vendas (
                    barcode,
                    cliente,
                    item,
                    tipo,
                    preco,
                    quantidade,
                    total,
                    pago,
                    data_venda,
                    registrado_por,
                    forma_pagamento,
                    tiket_num,
                    origem,
                    mesa_id,
                    desconto,
                    troco,
                    impressoes,
                    codigo_sessao,
                    empresa_id
                )
                VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,
                    NOW(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
            """, (
                item.get("barcode"),
                cliente,
                item.get("nome"),
                "VENDA",
                item.get("preco", 0),
                item.get("qtd", 1),
                item.get("total", 0),
                item.get("pago", item.get("total", 0)),  # FIX AQUI
                session.get("usuario", "WEB"),
                "WEB",
                tiket_num,
                "WEB",
                "WEB",
                0,
                0,
                0,
                "WEB",
                empresa_id
            ))

        # ==========================================
        # COMMIT FINAL
        # ==========================================
        conn.commit()

        return jsonify({
            "status": "ok",
            "pedido_id": pedido_id,
            "tiket_num": tiket_num
        })

    except Exception as e:
        conn.rollback()
        print("❌ ERRO FINALIZAR VENDA:", e)
        return jsonify({"erro": str(e)}), 500

    finally:
        cur.close()
        conn.close()

@app.route("/api/salvar_login", methods=["POST"])
def salvar_login():

    dados = request.json

    email = dados.get("email")
    senha = dados.get("senha")
    token = dados.get("token")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM logins_empresa
        WHERE email=%s
    """, (email,))

    row = cur.fetchone()

    if row:

        login_id = row[0]

        cur.execute("""
            UPDATE logins_empresa
            SET senha=%s,
                token=%s
            WHERE id=%s
        """, (senha, token, login_id))

    else:

        cur.execute("""
            INSERT INTO logins_empresa (
                email,
                senha,
                token
            )
            VALUES (%s,%s,%s)
            RETURNING id
        """, (
            email,
            senha,
            token
        ))

        login_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({
        "sucesso": True,
        "login_id": login_id
    })


# ======================================================
# RELATORIOS
# ======================================================
@app.route("/relatorios")
def relatorios():

    if "empresa_id" not in session:
        return redirect("/login")

    empresa_id = session["empresa_id"]

    conn = conectar()
    cur = conn.cursor()

    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    filtro = """
        WHERE empresa_id = %s
    """

    parametros = [empresa_id]

    if data_inicio and data_fim:

        filtro += """
            AND DATE(data)
            BETWEEN %s AND %s
        """

        parametros.extend([data_inicio, data_fim])

    # ==========================================
    # MOVIMENTOS
    # ==========================================

    cur.execute(f"""
        SELECT
            id,
            tipo,
            descricao,
            valor_entrada,
            valor_saida,
            usuario,
            data
        FROM movimentos_financeiros
        {filtro}
        ORDER BY id DESC
    """, parametros)

    movimentos = cur.fetchall()

    # ==========================================
    # TOTAL ENTRADAS
    # ==========================================

    cur.execute(f"""
        SELECT COALESCE(SUM(valor_entrada),0)
        FROM movimentos_financeiros
        {filtro}
    """, parametros)

    total_entrada = cur.fetchone()[0]

    # ==========================================
    # TOTAL SAIDAS
    # ==========================================

    cur.execute(f"""
        SELECT COALESCE(SUM(valor_saida),0)
        FROM movimentos_financeiros
        {filtro}
    """, parametros)

    total_saida = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        "relatorios.html",
        movimentos=movimentos,
        total_entrada=total_entrada,
        total_saida=total_saida
    )


# ======================================================
# API SALVAR MOVIMENTO FINANCEIRO
# ======================================================
@app.route("/api/salvar_movimento", methods=["POST"])
def api_salvar_movimento():

    try:

        dados = request.json

        token = dados.get("token")

        conn = conectar()
        cur = conn.cursor()

        # ==========================================
        # VALIDAR TOKEN
        # ==========================================

        cur.execute("""
            SELECT empresa_id
            FROM logins_empresa
            WHERE token = %s
        """, (token,))

        empresa = cur.fetchone()

        if not empresa:

            cur.close()
            conn.close()

            return jsonify({
                "erro": "TOKEN INVALIDO"
            }), 401

        empresa_id = empresa[0]

        # ==========================================
        # VERIFICAR DUPLICADO
        # ==========================================

        cur.execute("""
            SELECT id
            FROM movimentos_financeiros
            WHERE id = %s
            AND empresa_id = %s
        """, (
            dados.get("id"),
            empresa_id
        ))

        existe = cur.fetchone()

        # ==========================================
        # INSERT
        # ==========================================

        if not existe:

            cur.execute("""
                INSERT INTO movimentos_financeiros (

                    empresa_id,
                    id,
                    tipo,
                    descricao,
                    cliente_id,
                    data,
                    usuario,
                    valor_saida,
                    valor_entrada,
                    referencia_id,
                    valor_deposito,
                    revertido,
                    codigo_sessao

                )
                VALUES (

                    %s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s

                )
            """, (

                empresa_id,

                dados.get("id"),

                dados.get("tipo"),

                dados.get("descricao"),

                dados.get("cliente_id"),

                dados.get("data"),

                dados.get("usuario"),

                dados.get("valor_saida", 0),

                dados.get("valor_entrada", 0),

                dados.get("referencia_id"),

                dados.get("valor_deposito"),

                dados.get("revertido", False),

                dados.get("codigo_sessao")

            ))

            conn.commit()

            print(
                "✅ MOVIMENTO INSERIDO:",
                dados.get("id")
            )

        else:

            print(
                "⚠️ MOVIMENTO JA EXISTE:",
                dados.get("id")
            )

        cur.close()
        conn.close()

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        print("❌ ERRO API MOVIMENTO:", e)

        return jsonify({
            "erro": str(e)
        }), 500

@app.route("/")
@app.route("/painel")
def painel():

    if "empresa_id" not in session:
        return redirect("/login")

    empresa_id = session["empresa_id"]

    # ==========================
    # FILTROS
    # ==========================
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")
    usuario_filtro = request.args.get("usuario")

    conn = conectar()
    cur = conn.cursor()

    # ==========================
    # EMPRESA
    # ==========================
    cur.execute("""
        SELECT nome, moeda
        FROM empresa
        WHERE id = %s
    """, (empresa_id,))

    empresa = cur.fetchone()
    empresa_nome = empresa[0] if empresa else ""
    empresa_moeda = empresa[1] if empresa else "MT"

    # =========================================================
    # WHERE BASE (VENDAS)
    # =========================================================
    where_vendas = """
        v.empresa_id = %s
        AND NOT EXISTS (
            SELECT 1
            FROM tickets t
            WHERE t.tiket_num = v.tiket_num
            AND t.tipo = 'consumo_interno'
        )
    """

    params_vendas = [empresa_id]

    if inicio and fim:
        where_vendas += " AND v.data_venda BETWEEN %s AND %s"
        params_vendas.extend([inicio, fim])

    if usuario_filtro:
        where_vendas += " AND v.registrado_por = %s"
        params_vendas.append(usuario_filtro)

    # ==========================
    # TOTAL VENDAS
    # ==========================
    cur.execute(f"""
        SELECT COALESCE(SUM(v.total),0)
        FROM vendas v
        WHERE {where_vendas}
    """, params_vendas)

    total_vendas = cur.fetchone()[0] or 0

    # ==========================
    # VENDAS POR UTILIZADOR
    # ==========================
    cur.execute(f"""
        SELECT
            COALESCE(v.registrado_por,'Desconhecido'),
            SUM(COALESCE(v.total,0))
        FROM vendas v
        WHERE {where_vendas}
        GROUP BY v.registrado_por
        ORDER BY 2 DESC
    """, params_vendas)

    vendas_por_usuario = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "painel.html",
        empresa_nome=empresa_nome,
        empresa_moeda=empresa_moeda,
        total_vendas=total_vendas,
        vendas_por_usuario=vendas_por_usuario
    )
@app.route("/stock")
def stock():

    if "empresa_id" not in session:
        return redirect("/login")

    empresa_id = session["empresa_id"]

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.uuid,
            p.descricao,
            a.local AS armazem,
            COALESCE(SUM(s.quantidade),0) AS saldo,
            MAX(s.ultima_atualizacao) AS ultima_atualizacao
        FROM stock s
        JOIN produtos p ON p.uuid = s.produto_uuid
        LEFT JOIN armazem a ON a.uuid = s.armazem_uuid
        WHERE s.empresa_id = %s
        GROUP BY p.uuid, p.descricao, a.local
        ORDER BY p.descricao
    """, (empresa_id,))

    stock_data = cur.fetchall()

    cur.execute("""
        SELECT uuid, local
        FROM armazem
        WHERE empresa_id = %s
        ORDER BY local
    """, (empresa_id,))

    armazens = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "stock.html",
        stock=stock_data,
        armazens=armazens
    )

@app.route("/api/stock", methods=["GET"])
def api_stock():

    try:
        token = request.args.get("token")

        if not token:
            return {"error": "token missing"}, 401

        empresa = obter_empresa_por_token(token)

        if not empresa:
            return {"error": "token invalido"}, 401

        empresa_id = empresa[0]

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                s.id,
                p.uuid,
                p.descricao,

                s.armazem_uuid,
                a.local AS armazem_nome,

                s.quantidade,
                s.data,
                s.ultima_atualizacao,
                s.uuid,
                s.tipo_movimentacao,
                s.empresa_id

            FROM stock s
            JOIN produtos p ON p.uuid = s.produto_uuid
            LEFT JOIN armazem a ON a.uuid = s.armazem_uuid
            WHERE s.empresa_id = %s
            ORDER BY s.data DESC
        """, (empresa_id,))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify([
            {
                "id": r[0],
                "produto_uuid": r[1],
                "produto": r[2],

                "armazem_uuid": r[3],
                "armazem": r[4],

                "quantidade": float(r[5]),
                "data": str(r[6]) if r[6] else None,
                "ultima_atualizacao": str(r[7]) if r[7] else None,

                "uuid": r[8],
                "tipo_movimentacao": r[9],
                "empresa_id": r[10]
            }
            for r in rows
        ])

    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route("/api/stock_filtrado", methods=["GET"])
def api_stock_filtrado():

    try:
        token = request.args.get("token")
        produto = request.args.get("produto")
        armazem = request.args.get("armazem")

        empresa = obter_empresa_por_token(token)

        if not empresa:
            return {"error": "token invalido"}, 401

        empresa_id = empresa[0]

        conn = conectar()
        cur = conn.cursor()

        sql = """
            SELECT
                p.descricao,
                a.local,
                COALESCE(SUM(s.quantidade),0) AS saldo,
                MAX(s.ultima_atualizacao)
            FROM stock s
            JOIN produtos p ON p.uuid = s.produto_uuid
            LEFT JOIN armazem a ON a.uuid = s.armazem_uuid
            WHERE s.empresa_id = %s
        """

        params = [empresa_id]

        if produto:
            sql += " AND p.descricao ILIKE %s"
            params.append(f"%{produto}%")

        if armazem:
            sql += " AND a.local ILIKE %s"
            params.append(f"%{armazem}%")

        sql += """
            GROUP BY p.descricao, a.local
            ORDER BY p.descricao
        """

        cur.execute(sql, params)
        dados = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify([
            {
                "produto": r[0],
                "armazem": r[1],
                "quantidade": float(r[2]),
                "ultima_atualizacao": str(r[3]) if r[3] else None
            }
            for r in dados
        ])

    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route("/api/salvar_stock", methods=["POST"])
def api_salvar_stock():

    conn = None
    cur = None

    try:
        dados = request.json

        token = dados.get("token")
        empresa = obter_empresa_por_token(token)

        if not empresa:
            return jsonify({"erro": "TOKEN INVALIDO"}), 401

        empresa_id = empresa[0]

        conn = conectar()
        cur = conn.cursor()

        uuid_stock = dados.get("uuid")
        produto_uuid = dados.get("produto_uuid")
        armazem_uuid = dados.get("armazem_uuid")

        cur.execute("""
            SELECT id
            FROM produtos
            WHERE uuid = %s AND empresa_id = %s
        """, (produto_uuid, empresa_id))

        produto = cur.fetchone()

        if not produto:
            return jsonify({"error": "Produto não encontrado"}), 400

        produto_id = produto[0]

        # validar armazem
        if armazem_uuid:
            cur.execute("""
                SELECT id
                FROM armazem
                WHERE uuid = %s AND empresa_id = %s
            """, (armazem_uuid, empresa_id))

            if not cur.fetchone():
                return jsonify({"error": "Armazém não encontrado"}), 400

        cur.execute("""
            SELECT id
            FROM stock
            WHERE uuid = %s AND empresa_id = %s
        """, (uuid_stock, empresa_id))

        existe = cur.fetchone()

        if existe:

            cur.execute("""
                UPDATE stock
                SET
                    produto = %s,
                    produto_uuid = %s,
                    armazem_uuid = %s,
                    quantidade = %s,
                    ultima_atualizacao = NOW(),
                    tipo_movimentacao = %s
                WHERE id = %s
            """, (
                produto_id,
                produto_uuid,
                armazem_uuid,
                dados.get("quantidade"),
                dados.get("tipo_movimentacao"),
                existe[0]
            ))

        else:

            cur.execute("""
                INSERT INTO stock (
                    uuid,
                    produto,
                    produto_uuid,
                    armazem_uuid,
                    quantidade,
                    data,
                    ultima_atualizacao,
                    tipo_movimentacao,
                    empresa_id
                )
                VALUES (%s,%s,%s,%s,%s,NOW(),NOW(),%s,%s)
            """, (
                uuid_stock,
                produto_id,
                produto_uuid,
                armazem_uuid,
                dados.get("quantidade"),
                dados.get("tipo_movimentacao"),
                empresa_id
            ))

        conn.commit()

        return jsonify({"status": "ok"})

    except Exception as e:

        if conn:
            conn.rollback()

        return jsonify({"error": str(e)}), 500

    finally:

        if cur:
            cur.close()
        if conn:
            conn.close()

from decimal import Decimal
import uuid

def safe_str(v):
    return str(v).strip() if v is not None else ""


from decimal import Decimal
import uuid
from flask import request, jsonify, session


@app.route("/api/transferir_stock", methods=["POST"])
def transferir_stock():

    conn = None
    cur = None

    try:
        dados = request.json

        print("\n========== DEBUG TRANSFER INICIO ==========")
        print("RAW DADOS:", dados)
        print("TIPO:", type(dados))

        # =========================
        # EMPRESA
        # =========================
        empresa_id = session.get("empresa_id")

        print("EMPRESA_ID SESSION:", empresa_id)

        if not empresa_id:
            return jsonify({"error": "NAO AUTENTICADO"}), 401

        # =========================
        # DADOS
        # =========================
        produto_uuid = dados.get("produto_uuid")
        origem_uuid = dados.get("origem")
        destino_uuid = dados.get("destino")

        armazem_origem_uuid = dados.get("armazem_origem_uuid")
        armazem_destino_uuid = dados.get("armazem_destino_uuid")

        print("produto_uuid:", produto_uuid)
        print("origem_uuid:", origem_uuid)
        print("destino_uuid:", destino_uuid)
        print("armazem_origem_uuid:", armazem_origem_uuid)
        print("armazem_destino_uuid:", armazem_destino_uuid)

        # =========================
        # VALIDAÇÕES BASE
        # =========================
        if not produto_uuid:
            return jsonify({"error": "produto_uuid inválido"}), 400

        if not armazem_origem_uuid or not armazem_destino_uuid:
            return jsonify({"error": "armazem inválido"}), 400

        if origem_uuid == destino_uuid:
            return jsonify({"error": "Origem e destino não podem ser iguais"}), 400

        # =========================
        # QUANTIDADE
        # =========================
        try:
            qtd = Decimal(str(dados.get("quantidade")))
            print("QUANTIDADE OK:", qtd)
        except Exception as e:
            print("ERRO QUANTIDADE:", repr(e))
            return jsonify({"error": "Quantidade inválida"}), 400

        if qtd <= 0:
            return jsonify({"error": "Quantidade deve ser maior que zero"}), 400

        # =========================
        # DB
        # =========================
        conn = conectar()
        cur = conn.cursor()

        # =========================
        # PRODUTO
        # =========================
        print("DEBUG: BUSCANDO PRODUTO...")

        cur.execute("""
            SELECT id, descricao
            FROM produtos
            WHERE uuid = %s AND empresa_id = %s
        """, (produto_uuid, empresa_id))

        produto = cur.fetchone()

        print("PRODUTO RESULT:", produto)

        if not produto:
            return jsonify({"error": "Produto não encontrado"}), 400

        produto_id, produto_nome = produto

        # =========================
        # ARMAZÉM ORIGEM
        # =========================
        print("DEBUG: BUSCANDO ARMAZEM ORIGEM...")

        cur.execute("""
            SELECT id, local, uuid
            FROM armazem
            WHERE uuid = %s AND empresa_id = %s
        """, (armazem_origem_uuid, empresa_id))

        armazem_origem = cur.fetchone()

        print("ARMAZEM ORIGEM RESULT:", armazem_origem)

        if not armazem_origem:
            return jsonify({
                "error": "Armazém origem não encontrado",
                "debug_uuid": armazem_origem_uuid
            }), 400

        origem_nome = armazem_origem[1]

        # =========================
        # ARMAZÉM DESTINO
        # =========================
        print("DEBUG: BUSCANDO ARMAZEM DESTINO...")

        cur.execute("""
            SELECT id, local, uuid
            FROM armazem
            WHERE uuid = %s AND empresa_id = %s
        """, (armazem_destino_uuid, empresa_id))

        armazem_destino = cur.fetchone()

        print("ARMAZEM DESTINO RESULT:", armazem_destino)

        if not armazem_destino:
            return jsonify({
                "error": "Armazém destino não encontrado",
                "debug_uuid": armazem_destino_uuid
            }), 400

        destino_nome = armazem_destino[1]

        # =========================
        # SAÍDA
        # =========================
        print("DEBUG: INSERINDO SAÍDA...")

        cur.execute("""
            INSERT INTO stock (
                produto,
                produto_uuid,
                armazem_uuid,
                local,
                quantidade,
                tipo_movimentacao,
                uuid,
                data,
                ultima_atualizacao,
                empresa_id
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),%s)
        """, (
            produto_id,
            produto_uuid,
            armazem_origem_uuid,
            origem_nome,
            -qtd,
            "transferencia_saida",
            str(uuid.uuid4()),
            empresa_id
        ))

        # =========================
        # ENTRADA
        # =========================
        print("DEBUG: INSERINDO ENTRADA...")

        cur.execute("""
            INSERT INTO stock (
                produto,
                produto_uuid,
                armazem_uuid,
                local,
                quantidade,
                tipo_movimentacao,
                uuid,
                data,
                ultima_atualizacao,
                empresa_id
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NOW(),%s)
        """, (
            produto_id,
            produto_uuid,
            armazem_destino_uuid,
            destino_nome,
            qtd,
            "transferencia_entrada",
            str(uuid.uuid4()),
            empresa_id
        ))

        conn.commit()

        print("✔ TRANSFERÊNCIA OK")
        print("========== DEBUG TRANSFER FIM ==========\n")

        return jsonify({
            "status": "ok",
            "produto": produto_nome,
            "origem": origem_nome,
            "destino": destino_nome,
            "quantidade": float(qtd)
        })

    except Exception as e:

        print("❌ ERRO TRANSFERÊNCIA:", repr(e))

        if conn:
            conn.rollback()

        return jsonify({
            "error": str(e),
            "debug": "erro interno transfer_stock"
        }), 500

    finally:
        try:
            if cur:
                cur.close()
        except:
            pass

        try:
            if conn:
                conn.close()
        except:
            pass

@app.route("/api/sincronizar_armazens", methods=["POST"])
def sincronizar_armazens():

    try:

        dados = request.get_json()

        token = dados.get("token")

        empresa = obter_empresa_por_token(token)

        if not empresa:
            return jsonify({
                "error": "TOKEN INVALIDO"
            }), 401

        empresa_id = empresa[0]

        uuid_armazem = dados.get("uuid")
        local = dados.get("local")
        origem = dados.get("origem", "PDV")

        if not uuid_armazem:
            return jsonify({
                "error": "uuid obrigatorio"
            }), 400

        if not local:
            return jsonify({
                "error": "local obrigatorio"
            }), 400

        conn = conectar()
        cur = conn.cursor()

        # ==========================================
        # PROCURA UUID
        # ==========================================

        cur.execute("""
            SELECT id
            FROM armazem
            WHERE uuid = %s
            AND empresa_id = %s
        """, (
            uuid_armazem,
            empresa_id
        ))

        existe = cur.fetchone()

        # ==========================================
        # UPDATE
        # ==========================================

        if existe:

            cur.execute("""
                UPDATE armazem
                SET
                    local = %s,
                    origem = %s
                WHERE id = %s
            """, (
                local,
                origem,
                existe[0]
            ))

        # ==========================================
        # INSERT
        # ==========================================

        else:

            cur.execute("""
                INSERT INTO armazem
                (
                    uuid,
                    local,
                    empresa_id,
                    ativo,
                    origem
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                uuid_armazem,
                local,
                empresa_id,
                True,
                origem
            ))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

@app.route("/api/salvar_armazem", methods=["POST"])
def salvar_armazem():

    try:

        dados = request.json

        print("DADOS RECEBIDOS:", dados)

        token = dados.get("token")

        empresa = obter_empresa_por_token(token)

        if not empresa:

            print("TOKEN INVALIDO")

            return jsonify({
                "erro": "TOKEN INVALIDO"
            }), 401

        empresa_id = empresa[0]

        local = dados.get("local")

        if not local:

            return jsonify({
                "erro": "Local obrigatório"
            }), 400

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, uuid
            FROM armazem
            WHERE lower(local)=lower(%s)
            AND empresa_id=%s
        """, (
            local,
            empresa_id
        ))

        existe = cur.fetchone()

        if not existe:

            novo_uuid = str(uuid.uuid4())

            cur.execute("""
                INSERT INTO armazem
                (
                    uuid,
                    empresa_id,
                    local,
                    ativo,
                    origem
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                novo_uuid,
                empresa_id,
                local,
                True,
                "ONLINE"
            ))

            conn.commit()

            print(
                "ARMAZEM INSERIDO:",
                local
            )

        cur.close()
        conn.close()

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        print(
            "ERRO SALVAR ARMAZEM:",
            e
        )

        return jsonify({
            "erro": str(e)
        }), 500
    
@app.route("/api/armazens", methods=["GET"])
def api_armazens():

    try:

        token = request.args.get("token")

        empresa = obter_empresa_por_token(token)

        if not empresa:
            return jsonify([])

        empresa_id = empresa[0]

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                uuid,
                local,
                empresa_id,
                ativo,
                origem
            FROM armazem
            WHERE empresa_id = %s
            ORDER BY local
        """, (
            empresa_id,
        ))

        dados = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify([
            {
                "id": r[0],
                "uuid": r[1],
                "local": r[2],
                "empresa_id": r[3],
                "ativo": r[4],
                "origem": r[5]
            }
            for r in dados
        ])

    except Exception as e:

        return jsonify({
            "erro": str(e)
        }), 500

@app.route("/api/salvar_ticket", methods=["POST"])
def api_salvar_ticket():

    try:
        dados = request.json or {}
        token = dados.get("token")

        if not token:
            return jsonify({"erro": "TOKEN EM FALTA"}), 400

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT empresa_id
            FROM logins_empresa
            WHERE token = %s
        """, (token,))

        empresa = cur.fetchone()

        if not empresa:
            return jsonify({"erro": "TOKEN INVALIDO"}), 401

        empresa_id = empresa[0]

        # DUPLICADO
        cur.execute("""
            SELECT id
            FROM tickets
            WHERE tiket_num = %s AND empresa_id = %s
        """, (
            dados.get("tiket_num"),
            empresa_id
        ))

        if not cur.fetchone():

            cur.execute("""
                INSERT INTO tickets (
                    empresa_id,
                    tiket_num,
                    mesa,
                    cliente,
                    total,
                    pago,
                    data_venda,
                    registrado_por,
                    desconto,
                    forma_pagamento,
                    impressoes,
                    tipo,
                    valor_usado
                )
                VALUES (
                    %s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s
                )
            """, (
                empresa_id,
                dados.get("tiket_num"),
                dados.get("mesa"),
                dados.get("cliente"),
                dados.get("total"),
                dados.get("pago"),
                dados.get("data_venda"),
                dados.get("registrado_por"),
                dados.get("desconto"),
                dados.get("forma_pagamento"),
                dados.get("impressoes"),
                dados.get("tipo"),
                dados.get("valor_usado")
            ))

            conn.commit()

            print("✅ TICKET INSERIDO:", dados.get("tiket_num"))

        else:
            print("⚠️ TICKET JA EXISTE:", dados.get("tiket_num"))

        cur.close()
        conn.close()

        return jsonify({"status": "ok"})

    except Exception as e:
        print("❌ ERRO API TICKET:", str(e))
        return jsonify({"erro": str(e)}), 500

@app.route("/api/tickets", methods=["GET"])
def api_tickets():

    try:

        token = request.args.get("token")

        if not token:
            return jsonify({"erro": "TOKEN EM FALTA"}), 400

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT empresa_id
            FROM logins_empresa
            WHERE token = %s
        """, (token,))

        empresa = cur.fetchone()

        if not empresa:
            return jsonify({"erro": "TOKEN INVALIDO"}), 401

        empresa_id = empresa[0]

        cur.execute("""
            SELECT
                tiket_num,
                mesa,
                cliente,
                total,
                pago,
                data_venda,
                registrado_por,
                desconto,
                forma_pagamento,
                impressoes,
                tipo,
                valor_usado
            FROM tickets
            WHERE empresa_id = %s
            ORDER BY tiket_num
        """, (empresa_id,))

        dados = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify([
            {
                "tiket_num": t[0],
                "mesa": t[1],
                "cliente": t[2],
                "total": t[3],
                "pago": t[4],
                "data_venda": t[5],
                "registrado_por": t[6],
                "desconto": t[7],
                "forma_pagamento": t[8],
                "impressoes": t[9],
                "tipo": t[10],
                "valor_usado": t[11],
            }
            for t in dados
        ])

    except Exception as e:
        print("❌ ERRO API GET TICKETS:", str(e))
        return jsonify({"erro": str(e)}), 500

@app.route("/api/salvar_painel", methods=["POST"])
def api_salvar_painel():

    try:

        dados = request.json

        token = dados.get("token")

        # ==========================================
        # VALIDAR TOKEN
        # ==========================================

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT id
            FROM logins_empresa
            WHERE token = %s
        """, (token,))

        empresa = cur.fetchone()

        if not empresa:

            cur.close()
            conn.close()

            return jsonify({
                "erro": "TOKEN INVALIDO"
            }), 401

        # ==========================================
        # VERIFICAR DUPLICADO
        # ==========================================

        cur.execute("""
            SELECT id
            FROM painel
            WHERE referencia = %s
            AND tipo = %s
        """, (
            dados.get("referencia"),
            dados.get("tipo")
        ))

        existe = cur.fetchone()

        # ==========================================
        # INSERT
        # ==========================================

        if not existe:

            cur.execute("""
                INSERT INTO painel (

                    tipo,
                    referencia,
                    valor_total,
                    data_registro,
                    status,
                    usuario

                )
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (

                dados.get("tipo"),

                dados.get("referencia"),

                dados.get("valor_total", 0),

                dados.get("data_registro"),

                dados.get("status"),

                dados.get("usuario")

            ))

            conn.commit()

            print(
                "✅ PAINEL INSERIDO:",
                dados.get("referencia")
            )

        else:

            print(
                "⚠️ JA EXISTE:",
                dados.get("referencia")
            )

        cur.close()
        conn.close()

        return jsonify({
            "status": "ok"
        })

    except Exception as e:

        print("❌ ERRO API PAINEL:", e)

        return jsonify({
            "erro": str(e)
        }), 500

@app.route("/tickets")
def tickets():

    if "empresa_id" not in session:
        return redirect("/login")

    empresa_id = session["empresa_id"]

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            tiket_num,
            mesa,
            cliente,
            total,
            pago,
            data_venda,
            registrado_por,
            desconto,
            forma_pagamento,
            impressoes,
            tipo
        FROM tickets
        WHERE empresa_id = %s
        ORDER BY id DESC
    """, (empresa_id,))

    tickets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "tickets.html",
        tickets=tickets
    )


@app.route("/compras")
def compras():

    if "empresa_id" not in session:
        return redirect("/login")

    conn = conectar()
    cur = conn.cursor()

    # fornecedores
    cur.execute("""
        SELECT id,nome
        FROM fornecedores
        ORDER BY nome
    """)
    fornecedores = cur.fetchall()

    # produtos
    cur.execute("""
        SELECT uuid,descricao
        FROM produtos
        ORDER BY descricao
    """)
    produtos = cur.fetchall()

    # armazens
    cur.execute("""
        SELECT uuid,local
        FROM armazem
        WHERE empresa_id=%s
        ORDER BY local
    """,(session["empresa_id"],))

    armazens = cur.fetchall()

    # resumo compras
    cur.execute("""
        SELECT
            c.registro_id,
            f.nome,
            c.data,
            SUM(c.valor_total)
        FROM compras c
        LEFT JOIN fornecedores f
            ON f.id=c.fornecedor
        GROUP BY
            c.registro_id,
            f.nome,
            c.data
        ORDER BY c.registro_id DESC
    """)

    compras = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "compras.html",
        fornecedores=fornecedores,
        produtos=produtos,
        armazens=armazens,
        compras=compras
    )

from decimal import Decimal
import uuid
from flask import request, jsonify, session
@app.route("/api/compras", methods=["POST"])
def salvar_compra():

    conn = None
    cur = None

    try:
        print("\n========== COMPRA DEBUG ==========")
        dados = request.json
        print("RAW:", dados)

        empresa_id = session.get("empresa_id")
        if not empresa_id:
            return jsonify({"error": "NAO AUTENTICADO"}), 401

        itens = dados.get("itens", [])

        if not isinstance(itens, list) or len(itens) == 0:
            return jsonify({"error": "Nenhum item na compra"}), 400

        fornecedor = dados.get("fornecedor")
        armazem_uuid = dados.get("armazem_uuid")

        conn = conectar()
        cur = conn.cursor()

        # ================= EMPRESA =================
        cur.execute("SELECT nome FROM empresa WHERE id=%s", (empresa_id,))
        empresa = cur.fetchone()
        nome_empresa = empresa[0] if empresa else ""

        # ================= REGISTRO =================
        cur.execute("SELECT COALESCE(MAX(registro_id),0)+1 FROM compras")
        registro_id = cur.fetchone()[0]
        numero_fatura = f"CMP-{registro_id}"

        # ================= LOOP ITENS =================
        for item in itens:

            print("ITEM:", item)

            produto_uuid = item.get("produto_uuid")

            if not produto_uuid:
                print("❌ ITEM SEM produto_uuid:", item)
                continue

            try:
                quantidade = Decimal(str(item.get("quantidade", 0)))
                valor_unit = Decimal(str(item.get("valor_unit", 0)))
            except:
                continue

            valor_total = quantidade * valor_unit

            # produto
            cur.execute("""
                SELECT id FROM produtos
                WHERE uuid=%s AND empresa_id=%s
            """, (produto_uuid, empresa_id))

            prod = cur.fetchone()

            if not prod:
                print("❌ PRODUTO NÃO ENCONTRADO:", produto_uuid)
                continue

            produto_id = prod[0]

            # armazem
            cur.execute("""
                SELECT local FROM armazem
                WHERE uuid=%s AND empresa_id=%s
            """, (armazem_uuid, empresa_id))

            arm = cur.fetchone()

            if not arm:
                return jsonify({"error": "Armazém inválido"}), 400

            local_nome = arm[0]

            # ================= INSERT COMPRA =================
            cur.execute("""
                INSERT INTO compras (
                    fornecedor,
                    produto,
                    produto_uuid,
                    valor_unit,
                    valor_total,
                    quantidade,
                    local,
                    data,
                    usuario_logado,
                    pago,
                    pagamento,
                    registro_id,
                    numero_fatura,
                    empresa_id,
                    uuid,
                    armazem_uuid
                )
                VALUES (
                    %s,%s,%s,%s,%s,%s,%s,
                    CURRENT_DATE,
                    %s,
                    'Sim',
                    'Pronto Pagamento',
                    %s,%s,%s,%s,%s
                )
            """, (
                fornecedor,
                produto_id,
                produto_uuid,   # 🔥 GARANTIDO AQUI
                valor_unit,
                valor_total,
                quantidade,
                local_nome,
                nome_empresa,
                registro_id,
                numero_fatura,
                empresa_id,
                str(uuid.uuid4()),
                armazem_uuid
            ))

            # ================= STOCK =================
            cur.execute("""
                INSERT INTO stock (
                    produto,
                    produto_uuid,
                    armazem_uuid,
                    local,
                    quantidade,
                    tipo_movimentacao,
                    uuid,
                    data,
                    ultima_atualizacao,
                    empresa_id
                )
                VALUES (
                    %s,%s,%s,%s,%s,
                    'compra',
                    %s,
                    NOW(),
                    NOW(),
                    %s
                )
            """, (
                produto_id,
                produto_uuid,
                armazem_uuid,
                local_nome,
                quantidade,
                str(uuid.uuid4()),
                empresa_id
            ))

        conn.commit()

        print("✔ COMPRA OK")

        return jsonify({
            "status": "ok",
            "registro_id": registro_id,
            "numero_fatura": numero_fatura
        })

    except Exception as e:

        if conn:
            conn.rollback()

        print("❌ ERRO COMPRA:", repr(e))

        return jsonify({"error": str(e)}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route("/api/compra/<int:registro_id>")
def detalhe_compra(registro_id):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.descricao,
            c.quantidade,
            c.valor_unit,
            c.valor_total,
            c.local
        FROM compras c
        JOIN produtos p
            ON p.id=c.produto
        WHERE c.registro_id=%s
    """,(registro_id,))

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "produto":r[0],
            "quantidade":float(r[1]),
            "valor_unit":float(r[2]),
            "valor_total":float(r[3]),
            "armazem":r[4]
        }
        for r in dados
    ])

@app.route("/fornecedores")
def fornecedores():

    if "empresa_id" not in session:
        return redirect("/login")

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            nome,
            telefone,
            email,
            endereco,
            documento
        FROM fornecedores
        ORDER BY nome
    """)

    fornecedores = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "fornecedores.html",
        fornecedores=fornecedores
    )

import uuid

@app.route("/api/fornecedores", methods=["POST"])
def api_fornecedores():

    conn = None
    cur = None

    try:

        dados = request.json

        nome = dados.get("nome")
        telefone = dados.get("telefone")
        email = dados.get("email")
        endereco = dados.get("endereco")
        documento = dados.get("documento")

        empresa_id = session.get("empresa_id")

        if not nome:
            return jsonify({
                "error":"Nome obrigatório"
            }),400

        conn = conectar()
        cur = conn.cursor()

        # =========================
        # UUID
        # =========================

        fornecedor_uuid = dados.get("uuid")

        if not fornecedor_uuid:
            fornecedor_uuid = str(uuid.uuid4())

        print("\n========== FORNECEDOR ==========")
        print("UUID:", fornecedor_uuid)
        print("NOME:", nome)

        # =========================
        # VERIFICA SE JÁ EXISTE
        # =========================

        cur.execute("""
            SELECT id
            FROM fornecedores
            WHERE uuid=%s
        """,(fornecedor_uuid,))

        existe = cur.fetchone()

        if existe:

            print("FORNECEDOR JÁ EXISTE")

            return jsonify({
                "status":"existe",
                "id":existe[0],
                "uuid":fornecedor_uuid
            })

        # =========================
        # INSERT
        # =========================

        cur.execute("""
            INSERT INTO fornecedores
            (
                uuid,
                nome,
                telefone,
                email,
                endereco,
                documento,
                empresa_id
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,%s
            )
            RETURNING id
        """,(
            fornecedor_uuid,
            nome,
            telefone,
            email,
            endereco,
            documento,
            empresa_id
        ))

        fornecedor_id = cur.fetchone()[0]

        conn.commit()

        print("✔ FORNECEDOR SALVO")

        return jsonify({
            "status":"ok",
            "id":fornecedor_id,
            "uuid":fornecedor_uuid
        })

    except Exception as e:

        if conn:
            conn.rollback()

        print("ERRO FORNECEDOR:", repr(e))

        return jsonify({
            "error":str(e)
        }),500

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()

@app.route("/api/fornecedor/<int:id>")
def api_fornecedor(id):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            nome,
            telefone,
            email,
            endereco,
            documento
        FROM fornecedores
        WHERE id=%s
    """,(id,))

    r = cur.fetchone()

    cur.close()
    conn.close()

    if not r:
        return jsonify({
            "error":"Fornecedor não encontrado"
        }),404

    return jsonify({
        "id":r[0],
        "nome":r[1],
        "telefone":r[2],
        "email":r[3],
        "endereco":r[4],
        "documento":r[5]
    })



from flask import session, request, redirect
@app.before_request
def proteger_rotas():

    rotas_livres = [
        "login",
        "static",

        "api_produtos",
        "salvar_produto",

        "api_armazens",
        "salvar_armazem",
        "sincronizar_armazens",

        "api_stock",
        "api_salvar_stock",

        "api_tickets",
        "api_vendas",
        "api_salvar_venda",
    ]

    if request.endpoint in rotas_livres:
        return

    if "login_id" not in session:
        return redirect("/login")
# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
