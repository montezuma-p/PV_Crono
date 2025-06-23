# test_custom_exceptions.py
import pytest
import sys
import os

# Adiciona o diretório da aplicação principal ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from crono_app.custom_exceptions import (
    ErroFormatoInvalido,
    DadosObrigatoriosFaltando,
    CabecalhoInvalidoError,
    ErroDadosAtleta,
    ErroImportacaoCSV,
    ErroCronometragem
)

# --- Testes das Exceções Customizadas ---

def test_erro_formato_invalido():
    """Testa a exceção ErroFormatoInvalido."""
    mensagem = "Formato de data inválido"
    with pytest.raises(ErroFormatoInvalido) as excinfo:
        raise ErroFormatoInvalido(mensagem)
    
    assert str(excinfo.value) == mensagem
    assert isinstance(excinfo.value, ErroDadosAtleta)

def test_dados_obrigatorios_faltando():
    """Testa a exceção DadosObrigatoriosFaltando."""
    mensagem = "Campo nome é obrigatório"
    with pytest.raises(DadosObrigatoriosFaltando) as excinfo:
        raise DadosObrigatoriosFaltando(mensagem)
    
    assert str(excinfo.value) == mensagem
    assert isinstance(excinfo.value, ErroDadosAtleta)

def test_cabecalho_invalido_error():
    """Testa a exceção CabecalhoInvalidoError."""
    mensagem = "Cabeçalho do CSV inválido"
    with pytest.raises(CabecalhoInvalidoError) as excinfo:
        raise CabecalhoInvalidoError(mensagem)
    
    assert str(excinfo.value) == mensagem
    assert isinstance(excinfo.value, ErroImportacaoCSV)

def test_erro_dados_atleta():
    """Testa a exceção ErroDadosAtleta."""
    mensagem = "Dados do atleta inválidos"
    with pytest.raises(ErroDadosAtleta) as excinfo:
        raise ErroDadosAtleta(mensagem)
    
    assert str(excinfo.value) == mensagem
    assert isinstance(excinfo.value, ErroCronometragem)

def test_heranca_excepcoes():
    """Verifica se todas as exceções herdam da base correta."""
    from crono_app.custom_exceptions import (
        ErroCronometragem, ErroDadosAtleta, ErroImportacaoCSV
    )
    
    exceptions = [
        ErroFormatoInvalido("teste"),
        DadosObrigatoriosFaltando("teste"),
        ErroDadosAtleta("teste")
    ]
    
    for exc in exceptions:
        assert isinstance(exc, ErroDadosAtleta)
        assert isinstance(exc, ErroCronometragem)
    
    # Testa CabecalhoInvalidoError
    exc_csv = CabecalhoInvalidoError("teste")
    assert isinstance(exc_csv, ErroImportacaoCSV)
    assert isinstance(exc_csv, ErroCronometragem)

def test_mensagens_personalizadas():
    """Testa se as mensagens personalizadas são preservadas."""
    mensagens = [
        "Erro formato específico",
        "Dados obrigatórios específicos",
        "Cabeçalho específico",
        "Dados atleta específicos"
    ]
    
    exceptions = [
        ErroFormatoInvalido(mensagens[0]),
        DadosObrigatoriosFaltando(mensagens[1]),
        CabecalhoInvalidoError(mensagens[2]),
        ErroDadosAtleta(mensagens[3])
    ]
    
    for i, exc in enumerate(exceptions):
        assert str(exc) == mensagens[i]
