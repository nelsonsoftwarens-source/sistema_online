import psycopg2

def conectar():

    return psycopg2.connect(
        host="ep-wild-mountain-aq1zicdl-pooler.c-8.us-east-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_2DJBuRIdt5jC",
        port="5432",
        sslmode="require"
    )