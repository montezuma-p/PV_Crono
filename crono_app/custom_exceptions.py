# -*- coding: utf-8 -*-
# custom_exceptions.py

"""
Define a hierarquia de exceções personalizadas para a aplicação,
permitindo um tratamento de erros mais específico e informativo.
"""

class ErroCronometragem(Exception):
    """Exceção base para todos os erros controlados da aplicação."""
    pass

class ErroDadosAtleta(ErroCronometragem):
    """Exceção base para erros relacionados com os dados de um atleta."""
    pass

class ErroFormatoInvalido(ErroDadosAtleta):
    """Lançada quando um formato de dados (ex: data, número) é inválido."""
    pass

class DadosObrigatoriosFaltando(ErroDadosAtleta):
    """Lançada quando um campo obrigatório de um atleta está vazio."""
    pass

class AtletaNaoEncontradoError(ErroDadosAtleta):
    """Lançada quando uma operação tenta aceder a um atleta que não existe."""
    pass

class ErroImportacaoCSV(ErroCronometragem):
    """Exceção base para erros durante a importação de um ficheiro CSV."""
    pass

class CabecalhoInvalidoError(ErroImportacaoCSV):
    """Lançada quando o cabeçalho do CSV não contém as colunas obrigatórias."""
    pass

class ErroLogicaCorrida(ErroCronometragem):
    """Lançada para erros de lógica de negócio (ex: chegada antes da largada)."""
    pass

class ChegadaJaRegistradaError(ErroLogicaCorrida):
    """Lançada quando se tenta registrar uma chegada para um atleta que já finalizou."""
    pass

class VoltaInvalidaError(ErroLogicaCorrida):
    """Lançada quando uma volta registrada é inválida (ex: número de volta incorreto)."""
    pass