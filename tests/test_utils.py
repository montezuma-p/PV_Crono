# test_utils.py
import pytest
from datetime import timedelta
import sys
import os

# Adiciona o diretório da aplicação principal ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from crono_app.utils import formatar_timedelta

# --- Testes do Módulo Utils ---

def test_formatar_timedelta_horas_minutos_segundos():
    """Testa formatação com horas, minutos e segundos."""
    delta = timedelta(hours=2, minutes=30, seconds=45)
    resultado = formatar_timedelta(delta)
    assert resultado == "02:30:45.000"

def test_formatar_timedelta_apenas_minutos_segundos():
    """Testa formatação apenas com minutos e segundos."""
    delta = timedelta(minutes=15, seconds=30)
    resultado = formatar_timedelta(delta)
    assert resultado == "00:15:30.000"

def test_formatar_timedelta_apenas_segundos():
    """Testa formatação apenas com segundos."""
    delta = timedelta(seconds=45)
    resultado = formatar_timedelta(delta)
    assert resultado == "00:00:45.000"

def test_formatar_timedelta_zero():
    """Testa formatação com tempo zero."""
    delta = timedelta(0)
    resultado = formatar_timedelta(delta)
    assert resultado == "00:00:00.000"

def test_formatar_timedelta_mais_de_24_horas():
    """Testa formatação com mais de 24 horas."""
    delta = timedelta(hours=25, minutes=30, seconds=15)
    resultado = formatar_timedelta(delta)
    assert resultado == "25:30:15.000"

def test_formatar_timedelta_com_microssegundos():
    """Testa formatação com microssegundos."""
    delta = timedelta(hours=1, minutes=2, seconds=3, microseconds=456789)
    resultado = formatar_timedelta(delta)
    assert resultado == "01:02:03.456"

def test_formatar_timedelta_com_dias():
    """Testa formatação com dias (convertidos para horas)."""
    delta = timedelta(days=1, hours=2, minutes=30, seconds=45)
    resultado = formatar_timedelta(delta)
    # 1 dia = 24 horas + 2 horas = 26 horas
    assert resultado == "26:30:45.000"

def test_formatar_timedelta_formato_padrao():
    """Testa se o formato está sempre com 2 dígitos para horas, minutos e segundos."""
    delta = timedelta(hours=1, minutes=5, seconds=9)
    resultado = formatar_timedelta(delta)
    assert resultado == "01:05:09.000"

def test_formatar_timedelta_none():
    """Testa formatação com valor None."""
    resultado = formatar_timedelta(None)
    assert resultado == ""

def test_formatar_timedelta_negativo():
    """Testa formatação com timedelta negativo."""
    delta = timedelta(hours=-1, minutes=-30, seconds=-45)
    resultado = formatar_timedelta(delta)
    assert resultado.startswith("-")
    assert "01:30:45" in resultado
