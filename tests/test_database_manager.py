# -*- coding: utf-8 -*-
import pytest
import sqlite3
from unittest.mock import Mock, patch

from crono_app.database_manager import DatabaseManager

# Fixture para criar um DatabaseManager com um banco de dados em memória para cada teste.
# A chave aqui é manter a mesma conexão para toda a duração do teste.
@pytest.fixture
def db_manager():
    """
    Cria uma instância de DatabaseManager com um banco de dados em memória.
    Garante que a mesma conexão seja usada durante todo o teste para evitar
    que o banco de dados em memória seja recriado.
    """
    conn = sqlite3.connect(':memory:')
    manager = DatabaseManager(db_path=':memory:')
    
    # Sobrescreve o método _get_connection para sempre retornar a mesma conexão
    manager._get_connection = lambda: conn
    
    manager.setup_database()  # Garante que as tabelas sejam criadas na conexão persistente
    yield manager
    
    conn.close() # Limpa a conexão após o teste

# Fixture para um manager que NÃO executa o setup automaticamente
@pytest.fixture
def db_manager_no_setup():
    """Cria uma instância de DatabaseManager sem configurar o banco de dados inicial."""
    conn = sqlite3.connect(':memory:')
    manager = DatabaseManager(db_path=':memory:')
    manager._get_connection = lambda: conn
    yield manager
    conn.close()


class TestDatabaseManagerInitialization:
    """Testes focados na inicialização e configuração do DatabaseManager."""

    def test_instanciacao_com_caminho_valido(self, db_manager_no_setup):
        """Verifica se a instância é criada corretamente com um caminho válido."""
        assert db_manager_no_setup.db_path == ':memory:'
        assert isinstance(db_manager_no_setup, DatabaseManager)

    def test_instanciacao_com_caminho_vazio_lanca_erro(self):
        """Verifica se um ValueError é levantado quando o caminho é vazio."""
        with pytest.raises(ValueError, match="O caminho do banco de dados não pode ser vazio."):
            DatabaseManager(db_path='')

    def test_instanciacao_com_tipo_invalido_lanca_erro(self):
        """Verifica se um TypeError é levantado para tipos de caminho inválidos."""
        with pytest.raises(TypeError, match="O caminho do banco de dados deve ser uma string."):
            DatabaseManager(db_path=123)

    def test_setup_database_cria_tabelas_corretamente(self, db_manager_no_setup):
        """Verifica se o setup_database cria as tabelas 'atletas' e 'estado_corrida'."""
        manager = db_manager_no_setup
        manager.setup_database()

        with manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='atletas';")
            assert cursor.fetchone() is not None, "A tabela 'atletas' não foi criada."
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estado_corrida';")
            assert cursor.fetchone() is not None, "A tabela 'estado_corrida' não foi criada."

    def test_setup_database_adiciona_coluna_categoria_de_forma_idempotente(self, db_manager_no_setup):
        """Verifica se a coluna 'categoria' é adicionada e se execuções repetidas não causam erro."""
        manager = db_manager_no_setup
        manager.setup_database()
        
        try:
            manager.setup_database()
        except sqlite3.OperationalError as e:
            pytest.fail(f"A execução repetida de setup_database causou um erro inesperado: {e}")

        with manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(atletas);")
            colunas = [row[1] for row in cursor.fetchall()] # O nome da coluna é o segundo item
            assert 'categoria' in colunas, "A coluna 'categoria' não foi adicionada à tabela 'atletas'."


class TestDatabaseOperations:
    """Testes para as operações de CRUD e manipulação de dados."""

    def test_adicionar_atletas_em_lote_com_sucesso(self, db_manager):
        """Verifica se os atletas são adicionados em lote corretamente."""
        atletas_para_adicionar = [
            (1, 'Atleta Um', 'M', '1990-01-01', '5km', 'GERAL'),
            (2, 'Atleta Dois', 'F', '1992-05-10', '10km', 'GERAL')
        ]
        db_manager.adicionar_atletas_em_lote(atletas_para_adicionar)

        with db_manager._get_connection() as conn:
            conn.row_factory = sqlite3.Row # Garante que podemos acessar por nome de coluna
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM atletas ORDER BY num;")
            resultado = cursor.fetchall()
            assert len(resultado) == 2
            assert resultado[0]['nome'] == 'Atleta Um'
            assert resultado[1]['nome'] == 'Atleta Dois'

    def test_adicionar_atletas_em_lote_notifica_observadores(self, db_manager):
        """Verifica se o padrão observer é acionado ao adicionar atletas."""
        mock_observer = Mock()
        db_manager.attach(mock_observer)
        
        atletas = [(1, 'Observado', 'M', '1999-12-31', '5km', 'GERAL')]
        db_manager.adicionar_atletas_em_lote(atletas)

        mock_observer.update.assert_called_once_with(db_manager)

    def test_obter_atleta_por_id_existente(self, db_manager):
        """Verifica se um atleta existente é retornado corretamente."""
        db_manager.adicionar_atletas_em_lote([(10, 'Atleta Dez', 'F', '1988-11-11', '21km', 'MASTER')])
        atleta = db_manager.obter_atleta_por_id(10)
        assert atleta is not None
        assert atleta['nome'] == 'Atleta Dez'

    def test_obter_atleta_por_id_inexistente(self, db_manager):
        """Verifica se None é retornado para um atleta que não existe."""
        atleta = db_manager.obter_atleta_por_id(999)
        assert atleta is None

    def test_obter_atleta_por_id_em_caso_de_erro_retorna_none(self, db_manager_no_setup):
        """Verifica se o método retorna None em caso de um erro de banco de dados simulado."""
        manager = db_manager_no_setup

        # Usamos patch como um context manager para substituir _get_connection
        with patch.object(manager, '_get_connection') as mock_get_connection:
            # Configura o mock para simular a falha
            mock_cursor = Mock()
            mock_cursor.execute.side_effect = sqlite3.Error("Erro simulado")
            
            # O objeto retornado por _get_connection é o context manager.
            # Configuramos seu método __enter__ para retornar um objeto
            # que, ao ter seu método cursor() chamado, retorna nosso cursor mockado.
            mock_get_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor

            resultado = manager.obter_atleta_por_id(1)
            assert resultado is None

    def test_atualizar_tempo_atleta_com_sucesso(self, db_manager):
        """Verifica se o tempo de um atleta é atualizado corretamente."""
        db_manager.adicionar_atletas_em_lote([(25, 'Corredor Rápido', 'M', '2000-01-01', '5km', 'GERAL')])
        
        tempo_chegada = "2025-06-22T10:30:00"
        tempo_liquido = 1800.5
        db_manager.atualizar_tempo_atleta(25, tempo_chegada, tempo_liquido)

        atleta_atualizado = db_manager.obter_atleta_por_id(25)
        assert atleta_atualizado['tempo_absoluto_chegada'] == tempo_chegada
        assert atleta_atualizado['tempo_liquido'] == tempo_liquido

    def test_atualizar_tempo_atleta_notifica_observadores(self, db_manager):
        """Verifica se a atualização de tempo notifica os observadores."""
        db_manager.adicionar_atletas_em_lote([(25, 'Corredor Notificado', 'M', '2000-01-01', '5km', 'GERAL')])
        mock_observer = Mock()
        db_manager.attach(mock_observer)

        db_manager.atualizar_tempo_atleta(25, "2025-06-22T11:00:00", 2000.0)
        mock_observer.update.assert_called_once_with(db_manager)

    def test_obter_todos_atletas_retorna_lista_vazia(self, db_manager):
        """Verifica se uma lista vazia é retornada se não houver atletas."""
        atletas = db_manager.obter_todos_atletas_para_tabela('Nº', False)
        assert atletas == []

    def test_obter_todos_atletas_ordenacao_padrao(self, db_manager):
        """Verifica a ordenação padrão por número do atleta."""
        atletas_data = [
            (10, 'Dez', 'M', '1990-01-01', '5km', 'GERAL'),
            (1, 'Um', 'F', '1992-05-10', '10km', 'GERAL'),
            (5, 'Cinco', 'M', '1985-03-15', '5km', 'MASTER')
        ]
        db_manager.adicionar_atletas_em_lote(atletas_data)
        
        resultado = db_manager.obter_todos_atletas_para_tabela('Nº', False) # ASC
        assert [row['num'] for row in resultado] == [1, 5, 10]

        resultado_reverso = db_manager.obter_todos_atletas_para_tabela('Nº', True) # DESC
        assert [row['num'] for row in resultado_reverso] == [10, 5, 1]

    def test_reiniciar_prova_limpa_dados_e_notifica(self, db_manager):
        """Verifica se reiniciar a prova apaga todos os dados e notifica."""
        db_manager.adicionar_atletas_em_lote([(1, 'Atleta', 'M', '1990-01-01', '5km', 'GERAL')])
        db_manager.salvar_estado_corrida("status", "iniciada")
        
        mock_observer = Mock()
        db_manager.attach(mock_observer)

        db_manager.reiniciar_prova()

        atletas = db_manager.obter_todos_atletas_para_tabela('Nº', False)
        status = db_manager.carregar_estado_corrida("status")

        assert atletas == []
        assert status is None
        mock_observer.update.assert_called_once_with(db_manager)

    def test_salvar_e_carregar_estado_corrida(self, db_manager):
        """Verifica se o estado da corrida é salvo e carregado corretamente."""
        chave, valor = "tempo_inicio", "2025-06-22T09:00:00"
        db_manager.salvar_estado_corrida(chave, valor)
        
        valor_carregado = db_manager.carregar_estado_corrida(chave)
        assert valor_carregado == valor

    def test_carregar_estado_inexistente_retorna_default(self, db_manager):
        """Verifica se o valor padrão é retornado para uma chave inexistente."""
        valor = db_manager.carregar_estado_corrida("chave_que_nao_existe", default="padrao")
        assert valor == "padrao"
