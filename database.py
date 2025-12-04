import sqlite3

DB_NAME = "escala.db"


def create_database():
    """
    Cria o banco de dados e estrutura inicial das tabelas.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ----------------------------
    # Tabela de funcionários
    # ----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        );
    """)

    # ----------------------------
    # Tabela de férias (versão completa)
    # ----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ferias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            agendado_sap TEXT CHECK(agendado_sap IN ('sim', 'não')) DEFAULT 'não',
            periodo_dias INTEGER NOT NULL,
            abono_peculiario TEXT CHECK(abono_peculiario IN ('sim', 'não')) DEFAULT 'não',
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            folga_assiduidade_ano_anterior TEXT,
            folga_assiduidade_ano TEXT,
            cor TEXT,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        );
    """)
    # ----------------------------
    # Tabela de Folga Assiduidade (nova)
    # ----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folga_assiduidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            data_folga TEXT NOT NULL,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        );
    """)


    conn.commit()
    conn.close()


def get_connection():
    return sqlite3.connect(DB_NAME)
