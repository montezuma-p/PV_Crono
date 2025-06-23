# test_integration.py
import pytest
import logging
from datetime import date, datetime
import sys
import os

# Adiciona o diretório da aplicação principal ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Importe as classes dos seus módulos
from crono_app.database_manager import DatabaseManager
from crono_app.business_logic import GerenciadorDeCorrida, Atleta

# --- Fixtures do Pytest: Ferramentas de preparação para os testes ---

@pytest.fixture
def data_evento_padrao():
    """Retorna uma data de evento fixa para os testes."""
    return date(2024, 10, 26)

@pytest.fixture
def temp_db(tmp_path):
    """
    Cria um DatabaseManager com um arquivo de banco de dados SQLite temporário.
    O `tmp_path` é uma mágica do pytest que cria um diretório temporário.
    """
    db_path = tmp_path / "test_race.db"
    db_manager = DatabaseManager(str(db_path))
    # A setup_database precisa ser chamada explicitamente para os testes.
    db_manager.setup_database()
    return db_manager

@pytest.fixture
def gerenciador(temp_db):
    """Cria uma instância do GerenciadorDeCorrida usando o banco de dados temporário."""
    return GerenciadorDeCorrida(temp_db, logging.getLogger())


# --- Testes de Integração ---

def test_importacao_csv_e_verificacao_no_banco(gerenciador, tmp_path, data_evento_padrao):
    """
    Testa o fluxo completo: criar um CSV, importar e verificar se os dados
    foram salvos corretamente no banco de dados temporário.
    """
    # 1. Preparação: Criar um arquivo CSV de teste no diretório temporário
    csv_content = (
        "num,nome,sexo,data_nascimento,modalidade,categoria\n"
        "10,Atleta Teste 1,M,01/01/1990,10k,GERAL\n"
        "20,Atleta Teste 2,F,02/02/1995,5k,PCD\n"
        "30,Atleta Teste 3,M,03/03/2000,10k, \n" # Categoria vazia
    )
    csv_path = tmp_path / "atletas_teste.csv"
    csv_path.write_text(csv_content, encoding='utf-8')

    # 2. Execução: Chamar o método de importação
    sucesso, erros = gerenciador.carregar_atletas_csv(str(csv_path), data_evento_padrao)

    # 3. Verificação
    assert sucesso == 3
    assert len(erros) == 0

    # Verifica diretamente no banco se os atletas existem e a categoria está correta
    atleta10 = gerenciador.db.obter_atleta_por_id(10)
    assert atleta10 is not None
    assert atleta10['nome'] == "Atleta Teste 1"
    assert atleta10['modalidade'] == "10k"
    assert atleta10['categoria'] == "GERAL"

    atleta20 = gerenciador.db.obter_atleta_por_id(20)
    assert atleta20 is not None
    assert atleta20['sexo'] == "F"
    assert atleta20['categoria'] == "PCD"

    atleta30 = gerenciador.db.obter_atleta_por_id(30)
    assert atleta30 is not None
    assert atleta30['categoria'] == "GERAL" # Deve ser GERAL por padrão

def test_reiniciar_prova_limpa_dados(gerenciador, tmp_path, data_evento_padrao):
    """
    Testa se o método de reiniciar a prova realmente limpa as tabelas.
    """
    # 1. Preparação: Importar alguns dados primeiro
    csv_content = "num,nome,sexo,data_nascimento,modalidade,categoria\n1,Temp,M,01/01/2000,5k,GERAL"
    csv_path = tmp_path / "temp_atletas.csv"
    csv_path.write_text(csv_content, encoding='utf-8')
    gerenciador.carregar_atletas_csv(str(csv_path), data_evento_padrao)

    # Confirma que o atleta existe antes de reiniciar
    atleta_antes = gerenciador.db.obter_atleta_por_id(1)
    assert atleta_antes is not None

    # 2. Execução: Reiniciar a prova
    gerenciador.db.reiniciar_prova()

    # 3. Verificação: O atleta não deve mais ser encontrado
    atleta_depois = gerenciador.db.obter_atleta_por_id(1)
    assert atleta_depois is None

def test_atualizar_tempo_atleta(gerenciador, tmp_path, data_evento_padrao):
    """
    Testa a atualização do tempo de chegada de um atleta no banco de dados.
    """
    # 1. Preparação: Adicionar um atleta ao banco
    csv_content = "num,nome,sexo,data_nascimento,modalidade,categoria\n99,Veloz,F,03/03/1993,21k,PCD"
    csv_path = tmp_path / "atleta_veloz.csv"
    csv_path.write_text(csv_content, encoding='utf-8')
    gerenciador.carregar_atletas_csv(str(csv_path), data_evento_padrao)

    # 2. Execução: Atualizar o tempo do atleta 99
    tempo_chegada = datetime.now()
    tempo_liquido_segundos = 5432.1
    gerenciador.db.atualizar_tempo_atleta(99, tempo_chegada.isoformat(), tempo_liquido_segundos)

    # 3. Verificação: Buscar o atleta e conferir os tempos
    atleta_atualizado = gerenciador.db.obter_atleta_por_id(99)
    assert atleta_atualizado is not None
    assert atleta_atualizado['tempo_absoluto_chegada'] == tempo_chegada.isoformat()
    # Usar pytest.approx para comparar números de ponto flutuante com segurança
    assert atleta_atualizado['tempo_liquido'] == pytest.approx(tempo_liquido_segundos)
