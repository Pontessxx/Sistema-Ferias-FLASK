"""
database.py
-----------
Módulo responsável pela criação e gerenciamento do banco de dados SQLite
utilizado no Sistema de Escala de Férias.

Este arquivo oferece:

1. create_database()
   - Cria automaticamente todas as tabelas necessárias caso ainda não existam.
   - Centraliza e organiza a estrutura inicial do banco.
   - Garante integridade referencial com FOREIGN KEYS.

2. get_connection()
   - Fornece uma conexão ativa com o banco de dados para uso em módulos de
     serviços e rotas.

Banco utilizado:
    SQLite (arquivo local: escala.db)

Observação:
    O SQLite cria automaticamente o arquivo caso ele ainda não exista.
"""

import sqlite3

# Nome do arquivo de banco SQLite
DB_NAME = r"C:\Users\Henrique\Downloads\escala.db"


def create_database():
    """
    Cria o banco de dados e sua estrutura inicial.

    Este método deve ser executado apenas uma vez no início da aplicação, mas
    pode ser chamado quantas vezes necessário, pois utiliza CREATE TABLE IF NOT EXISTS,
    garantindo que nenhuma tabela existente seja sobrescrita.

    Estruturas criadas:

    1. funcionarios
        - Armazena colaboradores cadastrados.
        - Campos:
            id   : identificador único.
            nome : nome do funcionário.

    2. ferias
        - Registra períodos de férias completos.
        - Campos principais:
            funcionario_id               : referência ao funcionário.
            agendado_sap                 : indica se foi registrado no SAP.
            periodo_dias                 : número de dias de férias.
            abono_peculiario             : indica uso do abono pecuniário.
            data_inicio / data_fim       : período de férias.
            folga_assiduidade_*          : campos auxiliares para histórico.
            cor                          : cor usada no Gantt (opcional).

    3. folga_assiduidade
        - Registra folgas concedidas por assiduidade (nova tabela).
        - Campos:
            funcionario_id : referência ao funcionário.
            ano            : ano vigente da folga.
            data_folga     : data concedida.

    Returns:
        None
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ----------------------------------------------------------------------
    # Tabela de Funcionários
    # ----------------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        );
    """)

    # ----------------------------------------------------------------------
    # Tabela de Férias
    # ----------------------------------------------------------------------
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

    # ----------------------------------------------------------------------
    # Tabela de Folga por Assiduidade
    # ----------------------------------------------------------------------
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
    """
    Abre e retorna uma conexão ativa com o banco de dados SQLite.

    Returns:
        sqlite3.Connection: conexão pronta para uso.

    Observações importantes:
    - Sempre feche a conexão após o uso com conn.close().
    - Em operações de escrita (INSERT/UPDATE/DELETE), use conn.commit().
    """
    return sqlite3.connect(DB_NAME)
