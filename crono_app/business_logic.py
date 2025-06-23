# -*- coding: utf-8 -*-
# # business_logic.py
import csv
from datetime import datetime, date, timedelta
import logging
from .custom_exceptions import (
    ErroFormatoInvalido, DadosObrigatoriosFaltando, CabecalhoInvalidoError, ErroDadosAtleta
)

logger = logging.getLogger(__name__)

class Atleta:
    """
    Representa a entidade de dados de um atleta.
    Agora é principalmente uma estrutura de dados, com a lógica de validação
    e cálculo de idade.
    """
    def __init__(self, num: any, nome: str, sexo: str, data_nascimento_str: str, modalidade: str, categoria: str, data_evento: date):
        self.num = self._validar_num(num)
        self.nome = self._validar_texto(nome, "Nome")
        self.sexo = self._validar_sexo(sexo)
        self.data_nascimento_str = self._validar_texto(data_nascimento_str, "Data de Nascimento")
        self.modalidade = self._validar_texto(modalidade, "Modalidade")
        self.categoria = self._validar_categoria(categoria)
        self.idade = Atleta._calcular_idade(self.data_nascimento_str, data_evento)

    def _validar_num(self, num_str: any) -> int:
        try:
            num = int(num_str)
            if num <= 0:
                raise ValueError()
            return num
        except (ValueError, TypeError):
            raise ErroFormatoInvalido(f"Número do atleta inválido: '{num_str}'. Deve ser um inteiro positivo.")

    def _validar_texto(self, texto: str, nome_campo: str) -> str:
        if not texto or not str(texto).strip():
            raise DadosObrigatoriosFaltando(f"O campo '{nome_campo}' não pode ser vazio.")
        return str(texto).strip()

    def _validar_sexo(self, sexo: str) -> str:
        sexo_upper = str(sexo).upper().strip()
        if sexo_upper not in ['M', 'F']:
            raise ErroFormatoInvalido(f"Sexo inválido: '{sexo}'. Use 'M' ou 'F'.")
        return sexo_upper

    def _validar_categoria(self, categoria: str) -> str:
        """Valida a categoria, retornando 'GERAL' se vazia ou nula."""
        if not categoria or not str(categoria).strip():
            return "GERAL"
        return str(categoria).strip().upper()

    @staticmethod
    def _calcular_idade(data_nascimento_str: str, data_evento: date) -> int:
        try:
            nascimento = datetime.strptime(data_nascimento_str, '%d/%m/%Y').date()
            if nascimento > data_evento:
                raise ValueError("Data de nascimento não pode ser posterior à data do evento.")
            return data_evento.year - nascimento.year - ((data_evento.month, data_evento.day) < (nascimento.month, nascimento.day))
        except (ValueError, TypeError):
            raise ErroFormatoInvalido(f"Formato de data de nascimento inválido: '{data_nascimento_str}'. Use dd/mm/aaaa.")

class GerenciadorDeCorrida:
    """
    Classe de negócio refatorada. Contém a lógica de negócio principal,
    delegando a persistência de dados para o Database Manager.
    """
    def __init__(self, db_manager, logger_obj: logging.Logger):
        self.db = db_manager
        self.logger = logger_obj

    def carregar_atletas_csv(self, caminho_arquivo: str, data_evento: date) -> tuple[int, list[str]]:
        erros = []
        sucesso = 0
        atletas_para_banco = []
        numeros_vistos = set()

        try:
            # CORREÇÃO: Lógica de leitura de CSV simplificada e mais robusta
            with open(caminho_arquivo, mode='r', encoding='utf-8-sig', newline='') as arquivo:
                # Usamos o DictReader diretamente, que é o padrão para CSV com cabeçalho
                leitor_dict = csv.DictReader(arquivo)
                
                # Validação do cabeçalho
                header = [h.lower().strip() for h in leitor_dict.fieldnames] if leitor_dict.fieldnames else []
                obrigatorias = ['num', 'nome', 'sexo', 'data_nascimento', 'modalidade']
                if not all(c in header for c in obrigatorias):
                    colunas_faltantes = [c for c in obrigatorias if c not in header]
                    raise CabecalhoInvalidoError(f"Cabeçalho do CSV inválido. Colunas obrigatórias não encontradas: {colunas_faltantes}")

                for i, linha in enumerate(leitor_dict, start=2):
                    try:
                        num_str = linha.get('num')
                        if not num_str:
                            raise ValueError("Número do atleta ausente.")
                        num = int(num_str)
                        if num in numeros_vistos:
                            raise ValueError(f"Número de atleta duplicado no arquivo: {num}")
                        
                        atleta = Atleta(
                            num=num,
                            nome=linha.get('nome'),
                            sexo=linha.get('sexo'),
                            data_nascimento_str=linha.get('data_nascimento'),
                            modalidade=linha.get('modalidade'),
                            categoria=linha.get('categoria'), # Passa a categoria do CSV
                            data_evento=data_evento
                        )
                        
                        # Adiciona a tupla completa para inserção no banco
                        atletas_para_banco.append((
                            atleta.num,
                            atleta.nome,
                            atleta.sexo,
                            atleta.data_nascimento_str,
                            atleta.modalidade,
                            atleta.categoria
                        ))
                        numeros_vistos.add(num)
                        sucesso += 1
                    except ErroDadosAtleta as e:
                        erros.append(f"Linha {i}: Atleta #{linha.get('num', 'N/A')} - {e}")
                    except Exception as e:
                        erros.append(f"Linha {i}: Erro inesperado - {e}")

            if atletas_para_banco:
                self.db.adicionar_atletas_em_lote(atletas_para_banco)

        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        except UnicodeDecodeError:
            raise Exception("Erro de codificação. Salve o arquivo CSV com codificação UTF-8.")
        except Exception as e:
            self.logger.critical(f"Erro crítico ao processar o arquivo CSV: {e}")
            raise

        return sucesso, erros