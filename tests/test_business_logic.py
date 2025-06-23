# test_business_logic.py
import pytest
from datetime import date
import sys
import os

# Adiciona o diretório da aplicação principal ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from crono_app.business_logic import Atleta
from crono_app.custom_exceptions import ErroFormatoInvalido, DadosObrigatoriosFaltando

# --- Testes para a classe Atleta ---

# Uma 'fixture' do pytest para fornecer uma data de evento padrão para os testes
@pytest.fixture
def data_evento_padrao():
    """Retorna uma data de evento fixa para os testes."""
    return date(2024, 10, 26)

def test_calcular_idade_corretamente(data_evento_padrao):
    """
    Verifica se o cálculo de idade está correto para várias datas de nascimento.
    """
    # Caso 1: Aniversário já passou no ano do evento
    assert Atleta._calcular_idade("20/05/1990", data_evento_padrao) == 34
    
    # Caso 2: Aniversário ainda não passou no ano do evento
    assert Atleta._calcular_idade("30/12/1990", data_evento_padrao) == 33
    
    # Caso 3: Aniversário no mesmo dia do evento
    assert Atleta._calcular_idade("26/10/1990", data_evento_padrao) == 34
    
    # Caso 4: Atleta nascido no ano do evento
    assert Atleta._calcular_idade("01/01/2024", data_evento_padrao) == 0

def test_calcular_idade_formato_invalido(data_evento_padrao):
    """
    Verifica se a função levanta uma exceção para formatos de data inválidos.
    """
    with pytest.raises(ErroFormatoInvalido):
        Atleta._calcular_idade("1990-05-20", data_evento_padrao) # Formato ISO não esperado
        
    with pytest.raises(ErroFormatoInvalido):
        Atleta._calcular_idade("texto-invalido", data_evento_padrao)

def test_validacao_categoria_atleta(data_evento_padrao):
    """
    Testa a validação da categoria do atleta.
    """
    # Categoria explícita
    atleta1 = Atleta("1", "Nome", "M", "01/01/2000", "5k", "PCD", data_evento_padrao)
    assert atleta1.categoria == "PCD"

    # Categoria vazia deve virar GERAL
    atleta2 = Atleta("2", "Nome", "F", "01/01/2000", "5k", "  ", data_evento_padrao)
    assert atleta2.categoria == "GERAL"

    # Categoria nula (None) deve virar GERAL
    atleta3 = Atleta("3", "Nome", "M", "01/01/2000", "5k", None, data_evento_padrao)
    assert atleta3.categoria == "GERAL"

def test_validacao_atleta_sucesso(data_evento_padrao):
    """
    Testa a criação de um objeto Atleta com dados válidos.
    """
    atleta = Atleta(
        num="101",
        nome="  Joana d'Arc ",
        sexo="f",
        data_nascimento_str="10/02/1985",
        modalidade="Corrida 10k",
        categoria="GERAL",
        data_evento=data_evento_padrao
    )
    assert atleta.num == 101
    assert atleta.nome == "Joana d'Arc"
    assert atleta.sexo == "F" # Deve ser convertido para maiúsculo
    assert atleta.idade == 39
    assert atleta.categoria == "GERAL"

def test_validacao_atleta_falha(data_evento_padrao):
    """
    Testa se a criação do Atleta falha com dados inválidos,
    levantando as exceções corretas.
    """
    # Número inválido
    with pytest.raises(ErroFormatoInvalido):
        Atleta("abc", "Nome", "M", "01/01/2000", "5k", "GERAL", data_evento_padrao)
        
    # Nome vazio
    with pytest.raises(DadosObrigatoriosFaltando):
        Atleta("102", "  ", "F", "01/01/2000", "5k", "GERAL", data_evento_padrao)
        
    # Sexo inválido
    with pytest.raises(ErroFormatoInvalido):
        Atleta("103", "Nome", "X", "01/01/2000", "5k", "GERAL", data_evento_padrao)

# --- Como executar os testes ---
# 1. Certifique-se de que o pytest está instalado: pip install pytest
# 2. No terminal, na pasta do projeto, simplesmente execute o comando: pytest
# 3. O pytest encontrará e executará automaticamente os testes neste arquivo.
