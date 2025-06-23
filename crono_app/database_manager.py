# -*- coding: utf-8 -*-
import sqlite3
import logging
from typing import List, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # CORREÇÃO: A lista de observadores deve ser inicializada como uma lista vazia.
        self._observers: List[Any] = []
        # Configura a base de dados ao inicializar o gerenciador
        logger.debug(f"Inicializando DatabaseManager com o caminho: {db_path}")
        if not db_path:
            raise ValueError("O caminho do banco de dados não pode ser vazio.")
        if not isinstance(db_path, str):
            raise TypeError("O caminho do banco de dados deve ser uma string.")
        # A chamada para setup_database() foi removida daqui.
        # A inicialização do banco de dados agora é de responsabilidade exclusiva
        # do método _inicializacao_pos_ui na classe AppCrono, garantindo que
        # não haja bloqueio da UI durante a construção do objeto.
        logger.info(f"DatabaseManager pronto para o caminho: {db_path}")

    def attach(self, observer: Any):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Any):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    # OBSERVER PATTERN: O ponto central de notificação.
    # Chamado após qualquer operação que altere os dados.
    def _notify(self):
        logger.debug(f"Notificando {len(self._observers)} observador(es)...")
        for observer in self._observers:
            observer.update(self)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Adicione esta linha!
        return conn

    def setup_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Garantir que as tabelas principais existam
            sql_criar_tabela_atletas = """
            CREATE TABLE IF NOT EXISTS atletas (
                num INTEGER PRIMARY KEY, nome TEXT NOT NULL, sexo TEXT NOT NULL CHECK(sexo IN ('M', 'F')),
                data_nascimento TEXT NOT NULL, modalidade TEXT NOT NULL,
                tempo_absoluto_chegada TEXT, tempo_liquido REAL
            );"""
            sql_criar_tabela_estado = "CREATE TABLE IF NOT EXISTS estado_corrida (chave TEXT PRIMARY KEY, valor TEXT);"
            cursor.execute(sql_criar_tabela_atletas)
            cursor.execute(sql_criar_tabela_estado)

            # 2. Adicionar a coluna 'categoria' se ela não existir (operação de migração)
            try:
                # Esta consulta falhará se a coluna já existir, caindo no bloco except
                cursor.execute("ALTER TABLE atletas ADD COLUMN categoria TEXT NOT NULL DEFAULT 'GERAL'")
                logger.info("Coluna 'categoria' adicionada à tabela 'atletas'.")
            except sqlite3.OperationalError as e:
                # Ignora o erro apenas se for 'duplicate column name', caso contrário, lança a exceção
                if "duplicate column name" not in str(e):
                    logger.error(f"Erro inesperado ao tentar alterar a tabela 'atletas': {e}")
                    raise
                # Se a coluna já existe, o erro é esperado e ignorado.
                pass
            
            conn.commit()

    def adicionar_atletas_em_lote(self, atletas_data: List):
        # O número de '?' deve corresponder ao número de colunas na tabela
        # A coluna 'categoria' foi adicionada
        sql = "INSERT OR REPLACE INTO atletas (num, nome, sexo, data_nascimento, modalidade, categoria) VALUES (?,?,?,?,?,?);"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, atletas_data)
                conn.commit()
            logging.info(f"{len(atletas_data)} atletas inseridos/atualizados em lote.")
            self._notify() # Notifica a UI sobre a mudança
        except sqlite3.Error as e:
            logging.error(f"Erro ao inserir atletas em lote: {e}")
            raise

    def atualizar_tempo_atleta(self, num: int, tempo_chegada_iso: str, tempo_liquido_seg: float):
        sql = "UPDATE atletas SET tempo_absoluto_chegada =?, tempo_liquido =? WHERE num =?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (tempo_chegada_iso, tempo_liquido_seg, num))
                conn.commit()
            logging.info(f"Tempo do atleta #{num} atualizado na base de dados.")
            self._notify() # Notifica a UI sobre a mudança
        except sqlite3.Error as e:
            logging.error(f"Erro ao atualizar tempo do atleta #{num}: {e}")
            raise

    def obter_atleta_por_id(self, num: int) -> sqlite3.Row | None:
        sql = "SELECT * FROM atletas WHERE num =?"
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(sql, (num,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Erro ao obter atleta #{num}: {e}")
            return None
            
    def obter_todos_atletas_para_tabela(self, coluna_ordem: str, reverso: bool) -> List:
        mapa_colunas = {
            'Nº': 'num',
            'Nome': 'nome',
            'Sexo': 'sexo',
            'Idade': 'data_nascimento',
            'Categoria': 'categoria',
            'Modalidade': 'modalidade',
            'Tempo Bruto': 'tempo_liquido' # Alinhado com a UI
        }
        coluna_sql = mapa_colunas.get(coluna_ordem, 'num')
        direcao = "DESC" if reverso else "ASC"
        clausula_ordem = f"CASE WHEN tempo_liquido IS NULL THEN 1 ELSE 0 END, tempo_liquido {direcao}" if coluna_sql == 'tempo_liquido' else f"{coluna_sql} {direcao}"
        sql = f"SELECT num, nome, sexo, data_nascimento, categoria, modalidade, tempo_liquido FROM atletas ORDER BY {clausula_ordem}"
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(sql)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Erro ao obter todos os atletas: {e}")
            return [] # CORREÇÃO: Retorna lista vazia para evitar TypeError.

    def reiniciar_prova(self):
        """Apaga TODOS os dados das tabelas 'atletas' e 'estado_corrida'."""
        sql_delete_atletas = "DELETE FROM atletas;"
        sql_delete_estado = "DELETE FROM estado_corrida;"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # CORREÇÃO: A tabela de atletas também precisa ser limpa.
                cursor.execute(sql_delete_atletas)
                cursor.execute(sql_delete_estado)
                conn.commit()
            logger.warning("Prova reiniciada: todos os atletas e estados foram apagados.")
            self._notify()
        except sqlite3.Error as e:
            logger.error(f"Erro ao reiniciar a prova no banco de dados: {e}")

    def salvar_estado_corrida(self, chave: str, valor: Any):
        sql = "INSERT OR REPLACE INTO estado_corrida (chave, valor) VALUES (?, ?);"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (chave, str(valor) if valor is not None else None))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao salvar estado '{chave}': {e}")

    def carregar_estado_corrida(self, chave: str, default: Any = None) -> Any:
        sql = "SELECT valor FROM estado_corrida WHERE chave =?"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (chave,))
                resultado = cursor.fetchone()
                if resultado and resultado[0] is not None:
                    return resultado[0]
                return default
        except sqlite3.Error as e:
            logging.error(f"Erro ao carregar estado '{chave}': {e}")
            return default