# -*- coding: utf-8 -*-
# tests/test_ui_states.py

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, date
from tkinter import messagebox

import crono_app.ui_states as ui_states_module
from crono_app.ui_states import (
    State, PreparacaoState, EmCursoState, FinalizadoState
)
from crono_app.custom_exceptions import AtletaNaoEncontradoError, ErroLogicaCorrida


class TestStateBase:
    """Testes para a classe abstrata State."""
    
    def test_state_is_abstract(self):
        """Verifica que State é uma classe abstrata."""
        with pytest.raises(TypeError):
            State()
    
    def test_state_default_handlers_log_warnings(self):
        """Testa os handlers padrão que devem logar warnings."""
        # Criar uma implementação concreta mínima para teste
        class TestState(State):
            def on_enter(self, app): pass
            def handle_ui_update(self, app): pass
        
        state = TestState()
        mock_app = MagicMock()
        
        # Testar cada handler padrão
        state.handle_importar_atletas(mock_app)
        state.handle_iniciar_prova(mock_app, "10:00:00.000")
        state.handle_registrar_chegada(mock_app, "123")
        state.handle_finalizar_corrida(mock_app)
        state.handle_reiniciar_prova(mock_app)
        
        # Verificar se todos os warnings foram logados
        assert mock_app.logger.warning.call_count == 5
        
        # Verificar as mensagens de warning
        warning_calls = mock_app.logger.warning.call_args_list
        assert "Importar Atletas" in warning_calls[0][0][0]
        assert "Iniciar Prova" in warning_calls[1][0][0]
        assert "Registrar Chegada" in warning_calls[2][0][0]
        assert "Finalizar Corrida" in warning_calls[3][0][0]
        assert "Reiniciar Prova" in warning_calls[4][0][0]


class TestPreparacaoState:
    """Testes para PreparacaoState."""
    
    @pytest.fixture
    def app_mock(self):
        """Mock da aplicação com todos os componentes necessários."""
        app = MagicMock()
        app.THEME_COLORS = {
            "dark_blue": "#1f538d",
            "green": "#2b7a2b",
            "red": "#d12e2e"
        }
        app.data_do_evento = date(2025, 6, 22)
        app.db.obter_todos_atletas_para_tabela.return_value = []
        return app
    
    @pytest.fixture
    def state(self):
        """Instância do PreparacaoState."""
        return PreparacaoState()
    
    def test_on_enter_configura_ui_corretamente(self, state, app_mock):
        """Testa se on_enter configura a UI corretamente."""
        with patch('crono_app.ui_states.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "10:30:45.123456"  # Simula resultado completo
            mock_datetime.now.return_value = mock_now
            
            state.on_enter(app_mock)
            
            # Verificar configurações da UI
            app_mock.label_status_corrida.configure.assert_called_with(
                text="EM PREPARAÇÃO", 
                text_color=app_mock.THEME_COLORS["dark_blue"]
            )
            app_mock.label_cronometro.configure.assert_called_with(
                text="00:00:00.000", 
                text_color=app_mock.THEME_COLORS["dark_blue"]
            )
            
            # Verificar configuração do horário de largada
            mock_now.strftime.assert_called_with('%H:%M:%S.%f')
            app_mock.entry_horario_largada.delete.assert_called_with(0, "end")
            # O código usa [:-3] para cortar os últimos 3 dígitos dos microssegundos
            app_mock.entry_horario_largada.insert.assert_called_with(0, "10:30:45.123")
    
    def test_handle_ui_update_sem_atletas(self, state, app_mock):
        """Testa atualização da UI quando não há atletas."""
        app_mock.db.obter_todos_atletas_para_tabela.return_value = []
        
        state.handle_ui_update(app_mock)
        
        # Verificar estados dos botões sem atletas
        app_mock.btn_importar.configure.assert_called_with(state="normal")
        app_mock.btn_confirmar_largada.configure.assert_called_with(state="disabled")
        app_mock.btn_reiniciar.configure.assert_called_with(state="disabled")
        app_mock.entry_chegada.configure.assert_called_with(state="disabled")
        app_mock.btn_registrar_chegada.configure.assert_called_with(state="disabled")
        app_mock.btn_finalizar_corrida.configure.assert_called_with(state="disabled")
    
    def test_handle_ui_update_com_atletas(self, state, app_mock):
        """Testa atualização da UI quando há atletas."""
        app_mock.db.obter_todos_atletas_para_tabela.return_value = [
            ["1", "João", "M", "25", "Adulto", "10K", ""],
            ["2", "Maria", "F", "30", "Adulto", "10K", ""]
        ]
        
        state.handle_ui_update(app_mock)
        
        # Verificar estados dos botões com atletas
        app_mock.btn_importar.configure.assert_called_with(state="normal")
        app_mock.btn_confirmar_largada.configure.assert_called_with(state="normal")
        app_mock.btn_reiniciar.configure.assert_called_with(state="normal")
    
    def test_handle_importar_atletas(self, state, app_mock):
        """Testa o handler de importação de atletas."""
        state.handle_importar_atletas(app_mock)
        app_mock._executar_importacao_atletas.assert_called_once()
    
    def test_handle_iniciar_prova_sucesso(self, state, app_mock):
        """Testa início de prova com horário válido."""
        horario_str = "10:30:45.123"
        
        with patch('crono_app.ui_states.datetime') as mock_datetime:
            mock_time = MagicMock()
            mock_datetime.strptime.return_value.time.return_value = mock_time
            mock_datetime.combine.return_value.isoformat.return_value = "2025-06-22T10:30:45.123000"
            mock_datetime.combine.return_value.strftime.return_value = "10:30:45"
            
            state.handle_iniciar_prova(app_mock, horario_str)
            
            # Verificar chamadas
            mock_datetime.strptime.assert_called_with(horario_str, '%H:%M:%S.%f')
            mock_datetime.combine.assert_called_with(app_mock.data_do_evento, mock_time)
            app_mock.db.salvar_estado_corrida.assert_called_with('horario_largada', "2025-06-22T10:30:45.123000")
            app_mock.logger.info.assert_called()
            app_mock.transition_to.assert_called_once()
    
    def test_handle_iniciar_prova_formato_invalido(self, state, app_mock):
        """Testa início de prova com formato de horário inválido."""
        horario_invalido = "formato_invalido"
        
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            state.handle_iniciar_prova(app_mock, horario_invalido)
            
            mock_msgbox.showerror.assert_called_with(
                "Erro de Formato", 
                "Formato de hora inválido. Use HH:MM:SS.ms"
            )
            app_mock.transition_to.assert_not_called()
    
    def test_handle_reiniciar_prova_confirmado(self, state, app_mock):
        """Testa reinício de prova quando confirmado."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = True
            
            state.handle_reiniciar_prova(app_mock)
            
            mock_msgbox.askyesno.assert_called_with(
                "Confirmar Reinício", 
                "Tem certeza? TODOS os tempos serão apagados. A lista de atletas será mantida."
            )
            app_mock.db.reiniciar_prova.assert_called_once()
    
    def test_handle_reiniciar_prova_cancelado(self, state, app_mock):
        """Testa reinício de prova quando cancelado."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = False
            
            state.handle_reiniciar_prova(app_mock)
            
            app_mock.db.reiniciar_prova.assert_not_called()


class TestEmCursoState:
    """Testes para EmCursoState."""
    
    @pytest.fixture
    def app_mock(self):
        """Mock da aplicação."""
        app = MagicMock()
        app.THEME_COLORS = {
            "dark_blue": "#1f538d",
            "green": "#2b7a2b",
            "red": "#d12e2e"
        }
        app.chegada_num_var = MagicMock()
        return app
    
    @pytest.fixture
    def state(self):
        """Instância do EmCursoState."""
        return EmCursoState()
    
    def test_on_enter_com_horario_largada(self, state, app_mock):
        """Testa on_enter quando há horário de largada salvo."""
        horario_iso = "2025-06-22T10:30:45.123000"
        app_mock.db.carregar_estado_corrida.return_value = horario_iso
        
        with patch('crono_app.ui_states.datetime') as mock_datetime:
            mock_horario = MagicMock()
            mock_horario.strftime.return_value = "10:30:45.123456"  # Simula resultado completo
            mock_datetime.fromisoformat.return_value = mock_horario
            
            state.on_enter(app_mock)
            
            app_mock.label_status_corrida.configure.assert_called_with(
                text="EM CURSO", 
                text_color=app_mock.THEME_COLORS["green"]
            )
            mock_datetime.fromisoformat.assert_called_with(horario_iso)
            mock_horario.strftime.assert_called_with('%H:%M:%S.%f')
            app_mock.entry_horario_largada.delete.assert_called_with(0, "end")
            # O código usa [:-3] para cortar os últimos 3 dígitos dos microssegundos
            app_mock.entry_horario_largada.insert.assert_called_with(0, "10:30:45.123")
    
    def test_on_enter_sem_horario_largada(self, state, app_mock):
        """Testa on_enter quando não há horário de largada."""
        app_mock.db.carregar_estado_corrida.return_value = None
        
        state.on_enter(app_mock)
        
        app_mock.label_status_corrida.configure.assert_called_with(
            text="EM CURSO", 
            text_color=app_mock.THEME_COLORS["green"]
        )
        app_mock.entry_horario_largada.delete.assert_not_called()
        app_mock.entry_horario_largada.insert.assert_not_called()
    
    def test_handle_ui_update(self, state, app_mock):
        """Testa atualização da UI durante a corrida."""
        state.handle_ui_update(app_mock)
        
        # Verificar estados dos botões durante a corrida
        app_mock.btn_importar.configure.assert_called_with(state="disabled")
        app_mock.btn_confirmar_largada.configure.assert_called_with(state="normal")
        app_mock.btn_reiniciar.configure.assert_called_with(state="normal")
        app_mock.entry_chegada.configure.assert_called_with(state="normal")
        app_mock.btn_registrar_chegada.configure.assert_called_with(state="normal")
        app_mock.btn_finalizar_corrida.configure.assert_called_with(state="normal")
    
    def test_handle_registrar_chegada_sucesso(self, state, app_mock):
        """Testa registro de chegada bem-sucedido."""
        num_atleta_str = "123"
        horario_largada = "2025-06-22T10:00:00"
        
        app_mock.db.obter_atleta_por_id.return_value = {"num": 123, "nome": "João"}
        app_mock.db.carregar_estado_corrida.return_value = horario_largada
        
        with patch('crono_app.ui_states.datetime') as mock_datetime:
            # Mock do horário atual (11:30:45)
            mock_datetime.now.return_value = datetime(2025, 6, 22, 11, 30, 45)
            mock_datetime.fromisoformat.return_value = datetime(2025, 6, 22, 10, 0, 0)
            
            state.handle_registrar_chegada(app_mock, num_atleta_str)
            
            # Verificar chamadas
            app_mock.db.obter_atleta_por_id.assert_called_with(123)
            app_mock.db.carregar_estado_corrida.assert_called_with('horario_largada')
            app_mock.db.atualizar_tempo_atleta.assert_called_once()
            
            # Verificar limpeza da entrada
            app_mock.chegada_num_var.set.assert_called_with("")
            app_mock.entry_chegada.focus.assert_called_once()
    
    def test_handle_registrar_chegada_atleta_nao_encontrado(self, state, app_mock):
        """Testa registro de chegada com atleta inexistente."""
        num_atleta_str = "999"
        app_mock.db.obter_atleta_por_id.return_value = None
        
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            state.handle_registrar_chegada(app_mock, num_atleta_str)
            
            mock_msgbox.showwarning.assert_called_with(
                "Erro de Lógica", 
                "Atleta com número 999 não encontrado."
            )
            app_mock.chegada_num_var.set.assert_called_with("")
            app_mock.entry_chegada.focus.assert_called_once()
    
    def test_handle_registrar_chegada_sem_horario_largada(self, state, app_mock):
        """Testa registro de chegada sem horário de largada definido."""
        num_atleta_str = "123"
        app_mock.db.obter_atleta_por_id.return_value = {"num": 123}
        app_mock.db.carregar_estado_corrida.return_value = None
        
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            state.handle_registrar_chegada(app_mock, num_atleta_str)
            
            mock_msgbox.showwarning.assert_called_with(
                "Erro de Lógica", 
                "Horário de largada não definido."
            )
    
    def test_handle_registrar_chegada_numero_invalido(self, state, app_mock):
        """Testa registro de chegada com número inválido."""
        num_atleta_invalido = "abc"
        
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            state.handle_registrar_chegada(app_mock, num_atleta_invalido)
            
            mock_msgbox.showerror.assert_called_with(
                "Entrada Inválida", 
                "Digite um número de atleta válido."
            )
            app_mock.chegada_num_var.set.assert_called_with("")
            app_mock.entry_chegada.focus.assert_called_once()
    
    def test_handle_registrar_chegada_antes_largada(self, state, app_mock):
        """Testa registro de chegada antes do horário de largada."""
        num_atleta_str = "123"
        horario_largada = "2025-06-22T12:00:00"  # Largada às 12:00
        
        app_mock.db.obter_atleta_por_id.return_value = {"num": 123}
        app_mock.db.carregar_estado_corrida.return_value = horario_largada
        
        with patch('crono_app.ui_states.datetime') as mock_datetime:
            # Horário atual antes da largada (11:00)
            mock_datetime.now.return_value = datetime(2025, 6, 22, 11, 0, 0)
            mock_datetime.fromisoformat.return_value = datetime(2025, 6, 22, 12, 0, 0)
            
            with patch('crono_app.ui_states.messagebox') as mock_msgbox:
                state.handle_registrar_chegada(app_mock, num_atleta_str)
                
                mock_msgbox.showwarning.assert_called_with(
                    "Erro de Lógica", 
                    "Hora de chegada não pode ser anterior à de largada."
                )
    
    def test_handle_finalizar_corrida_confirmado(self, state, app_mock):
        """Testa finalização da corrida quando confirmada."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = True
            
            state.handle_finalizar_corrida(app_mock)
            
            mock_msgbox.askyesno.assert_called_with(
                "Confirmar Finalização", 
                "Deseja finalizar a corrida? A cronometragem será bloqueada."
            )
            app_mock.db.salvar_estado_corrida.assert_called_with('estado_prova', 'FINALIZADO')
            app_mock.logger.warning.assert_called_with("PROVA FINALIZADA. Cronometragem bloqueada.")
            app_mock.transition_to.assert_called_once()
    
    def test_handle_finalizar_corrida_cancelado(self, state, app_mock):
        """Testa finalização da corrida quando cancelada."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = False
            
            state.handle_finalizar_corrida(app_mock)
            
            app_mock.db.salvar_estado_corrida.assert_not_called()
            app_mock.transition_to.assert_not_called()
    
    def test_handle_reiniciar_prova_confirmado(self, state, app_mock):
        """Testa reinício durante a corrida quando confirmado."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = True
            
            state.handle_reiniciar_prova(app_mock)
            
            mock_msgbox.askyesno.assert_called_with(
                "Confirmar Reinício", 
                "A prova está em andamento. Deseja reiniciar? TODOS os tempos serão apagados."
            )
            app_mock.db.reiniciar_prova.assert_called_once()
            app_mock.transition_to.assert_called_once()
    
    def test_handle_reiniciar_prova_cancelado(self, state, app_mock):
        """Testa reinício durante a corrida quando cancelado."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = False
            
            state.handle_reiniciar_prova(app_mock)
            
            app_mock.db.reiniciar_prova.assert_not_called()
            app_mock.transition_to.assert_not_called()


class TestFinalizadoState:
    """Testes para FinalizadoState."""
    
    @pytest.fixture
    def app_mock(self):
        """Mock da aplicação."""
        app = MagicMock()
        app.THEME_COLORS = {
            "dark_blue": "#1f538d",
            "green": "#2b7a2b",
            "red": "#d12e2e"
        }
        return app
    
    @pytest.fixture
    def state(self):
        """Instância do FinalizadoState."""
        return FinalizadoState()
    
    def test_on_enter(self, state, app_mock):
        """Testa on_enter do estado finalizado."""
        state.on_enter(app_mock)
        
        app_mock.label_status_corrida.configure.assert_called_with(
            text="FINALIZADA", 
            text_color=app_mock.THEME_COLORS["red"]
        )
    
    def test_handle_ui_update(self, state, app_mock):
        """Testa atualização da UI no estado finalizado."""
        state.handle_ui_update(app_mock)
        
        # Verificar que tudo está desabilitado exceto reiniciar
        app_mock.btn_importar.configure.assert_called_with(state="disabled")
        app_mock.btn_confirmar_largada.configure.assert_called_with(state="disabled")
        app_mock.btn_reiniciar.configure.assert_called_with(state="normal")
        app_mock.entry_chegada.configure.assert_called_with(state="disabled")
        app_mock.btn_registrar_chegada.configure.assert_called_with(state="disabled")
        app_mock.btn_finalizar_corrida.configure.assert_called_with(state="disabled")
    
    def test_handle_reiniciar_prova_confirmado(self, state, app_mock):
        """Testa reinício no estado finalizado quando confirmado."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = True
            
            state.handle_reiniciar_prova(app_mock)
            
            mock_msgbox.askyesno.assert_called_with(
                "Confirmar Reinício", 
                "A prova está finalizada. Deseja reiniciar para uma nova cronometragem?"
            )
            app_mock.db.reiniciar_prova.assert_called_once()
            app_mock.transition_to.assert_called_once()
    
    def test_handle_reiniciar_prova_cancelado(self, state, app_mock):
        """Testa reinício no estado finalizado quando cancelado."""
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = False
            
            state.handle_reiniciar_prova(app_mock)
            
            app_mock.db.reiniciar_prova.assert_not_called()
            app_mock.transition_to.assert_not_called()


class TestStateTransitions:
    """Testes para transições entre estados."""
    
    def test_preparacao_to_em_curso_transition(self):
        """Testa transição de Preparação para Em Curso."""
        app_mock = MagicMock()
        app_mock.THEME_COLORS = {"dark_blue": "#1f538d"}
        app_mock.data_do_evento = date(2025, 6, 22)
        
        preparacao = PreparacaoState()
        
        with patch('crono_app.ui_states.datetime') as mock_datetime:
            mock_time = MagicMock()
            mock_datetime.strptime.return_value.time.return_value = mock_time
            mock_datetime.combine.return_value.isoformat.return_value = "2025-06-22T10:30:45"
            mock_datetime.combine.return_value.strftime.return_value = "10:30:45"
            
            preparacao.handle_iniciar_prova(app_mock, "10:30:45.000")
            
            # Verificar que transition_to foi chamado com EmCursoState
            app_mock.transition_to.assert_called_once()
            transitioned_state = app_mock.transition_to.call_args[0][0]
            assert isinstance(transitioned_state, EmCursoState)
    
    def test_em_curso_to_finalizado_transition(self):
        """Testa transição de Em Curso para Finalizado."""
        app_mock = MagicMock()
        em_curso = EmCursoState()
        
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = True
            
            em_curso.handle_finalizar_corrida(app_mock)
            
            # Verificar que transition_to foi chamado com FinalizadoState
            app_mock.transition_to.assert_called_once()
            transitioned_state = app_mock.transition_to.call_args[0][0]
            assert isinstance(transitioned_state, FinalizadoState)
    
    def test_any_state_to_preparacao_on_restart(self):
        """Testa que qualquer estado pode retornar para Preparação no reinício."""
        app_mock = MagicMock()
        
        # Testar reinício do estado Em Curso
        em_curso = EmCursoState()
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = True
            
            em_curso.handle_reiniciar_prova(app_mock)
            
            app_mock.transition_to.assert_called_once()
            transitioned_state = app_mock.transition_to.call_args[0][0]
            assert isinstance(transitioned_state, PreparacaoState)
        
        # Reset mock
        app_mock.reset_mock()
        
        # Testar reinício do estado Finalizado
        finalizado = FinalizadoState()
        with patch('crono_app.ui_states.messagebox') as mock_msgbox:
            mock_msgbox.askyesno.return_value = True
            
            finalizado.handle_reiniciar_prova(app_mock)
            
            app_mock.transition_to.assert_called_once()
            transitioned_state = app_mock.transition_to.call_args[0][0]
            assert isinstance(transitioned_state, PreparacaoState)
