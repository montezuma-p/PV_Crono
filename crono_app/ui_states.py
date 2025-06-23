# -*- coding: utf-8 -*-
# ui_states.py

from abc import ABC, abstractmethod
from tkinter import messagebox
from datetime import datetime
from .custom_exceptions import AtletaNaoEncontradoError, ErroLogicaCorrida

# Importar os outros estados
class EmCursoState: pass
class FinalizadoState: pass
class PreparacaoState: pass

class State(ABC):
    """
    Classe base abstrata para o Padrão State. Define a interface
    comum para todos os estados concretos.
    """
    @abstractmethod
    def on_enter(self, app): pass

    @abstractmethod
    def handle_ui_update(self, app): pass

    def handle_importar_atletas(self, app):
        app.logger.warning(f"Ação 'Importar Atletas' não permitida no estado {self.__class__.__name__}.")

    def handle_iniciar_prova(self, app, horario_str: str):
        app.logger.warning(f"Ação 'Iniciar Prova' não permitida no estado {self.__class__.__name__}.")

    def handle_registrar_chegada(self, app, num_atleta_str: str):
        app.logger.warning(f"Ação 'Registrar Chegada' não permitida no estado {self.__class__.__name__}.")

    def handle_finalizar_corrida(self, app):
        app.logger.warning(f"Ação 'Finalizar Corrida' não permitida no estado {self.__class__.__name__}.")

    def handle_reiniciar_prova(self, app):
        app.logger.warning(f"Ação 'Reiniciar Prova' não permitida no estado {self.__class__.__name__}.")

class PreparacaoState(State):
    """Estado inicial da aplicação, antes da largada."""
    def on_enter(self, app):
        app.label_status_corrida.configure(text="EM PREPARAÇÃO", text_color=app.THEME_COLORS["dark_blue"])
        app.label_cronometro.configure(text="00:00:00.000", text_color=app.THEME_COLORS["dark_blue"])
        app.entry_horario_largada.delete(0, "end")
        app.entry_horario_largada.insert(0, datetime.now().strftime('%H:%M:%S.%f')[:-3])

    def handle_ui_update(self, app):
        # CORREÇÃO 2: Verificar se existe QUALQUER atleta, não apenas o de nº 1
        has_atletas = len(app.db.obter_todos_atletas_para_tabela('Nº', False)) > 0
        app.btn_importar.configure(state="normal")
        app.btn_confirmar_largada.configure(state="normal" if has_atletas else "disabled")
        app.btn_reiniciar.configure(state="normal" if has_atletas else "disabled")
        app.entry_chegada.configure(state="disabled")
        app.btn_registrar_chegada.configure(state="disabled")
        app.btn_finalizar_corrida.configure(state="disabled")

    def handle_importar_atletas(self, app):
        app._executar_importacao_atletas()

    def handle_iniciar_prova(self, app, horario_str: str):
        try:
            horario_obj = datetime.strptime(horario_str, '%H:%M:%S.%f').time()
            novo_horario = datetime.combine(app.data_do_evento, horario_obj)
            app.db.salvar_estado_corrida('horario_largada', novo_horario.isoformat())
            app.logger.info(f"Prova iniciada. Horário de largada: {novo_horario.strftime('%H:%M:%S')}.")
            app.transition_to(EmCursoState())
        except ValueError:
            messagebox.showerror("Erro de Formato", "Formato de hora inválido. Use HH:MM:SS.ms")

    def handle_reiniciar_prova(self, app):
        if messagebox.askyesno("Confirmar Reinício", "Tem certeza? TODOS os tempos serão apagados. A lista de atletas será mantida."):
            app.db.reiniciar_prova()

class EmCursoState(State):
    """Estado da aplicação durante a corrida."""
    def on_enter(self, app):
        app.label_status_corrida.configure(text="EM CURSO", text_color=app.THEME_COLORS["green"])
        horario_largada_str = app.db.carregar_estado_corrida('horario_largada')
        if horario_largada_str:
            horario_largada = datetime.fromisoformat(horario_largada_str)
            app.entry_horario_largada.delete(0, "end")
            app.entry_horario_largada.insert(0, horario_largada.strftime('%H:%M:%S.%f')[:-3])

    def handle_ui_update(self, app):
        app.btn_importar.configure(state="disabled")
        app.btn_confirmar_largada.configure(state="normal") # Permitir reajuste
        app.btn_reiniciar.configure(state="normal")
        app.entry_chegada.configure(state="normal")
        app.btn_registrar_chegada.configure(state="normal")
        app.btn_finalizar_corrida.configure(state="normal")

    def handle_registrar_chegada(self, app, num_atleta_str: str):
        try:
            num_atleta = int(num_atleta_str)
            if app.db.obter_atleta_por_id(num_atleta) is None:
                raise AtletaNaoEncontradoError(f"Atleta com número {num_atleta} não encontrado.")
            
            horario_largada_str = app.db.carregar_estado_corrida('horario_largada')
            if not horario_largada_str:
                raise ErroLogicaCorrida("Horário de largada não definido.")
            
            horario_largada = datetime.fromisoformat(horario_largada_str)
            timestamp_chegada = datetime.now()
            if timestamp_chegada < horario_largada:
                raise ErroLogicaCorrida("Hora de chegada não pode ser anterior à de largada.")
            
            tempo_liquido = timestamp_chegada - horario_largada
            app.db.atualizar_tempo_atleta(num_atleta, timestamp_chegada.isoformat(), tempo_liquido.total_seconds())
        except (ValueError, TypeError):
            messagebox.showerror("Entrada Inválida", "Digite um número de atleta válido.")
        except (AtletaNaoEncontradoError, ErroLogicaCorrida) as e:
            messagebox.showwarning("Erro de Lógica", str(e))
        finally:
            app.chegada_num_var.set("")
            app.entry_chegada.focus()

    def handle_finalizar_corrida(self, app):
        if messagebox.askyesno("Confirmar Finalização", "Deseja finalizar a corrida? A cronometragem será bloqueada."):
            app.db.salvar_estado_corrida('estado_prova', 'FINALIZADO')
            app.logger.warning("PROVA FINALIZADA. Cronometragem bloqueada.")
            app.transition_to(FinalizadoState())

    def handle_reiniciar_prova(self, app):
        if messagebox.askyesno("Confirmar Reinício", "A prova está em andamento. Deseja reiniciar? TODOS os tempos serão apagados."):
            app.db.reiniciar_prova()
            app.transition_to(PreparacaoState())

class FinalizadoState(State):
    """Estado da aplicação após a corrida ter sido finalizada."""
    def on_enter(self, app):
        app.label_status_corrida.configure(text="FINALIZADA", text_color=app.THEME_COLORS["red"])

    def handle_ui_update(self, app):
        app.btn_importar.configure(state="disabled")
        app.btn_confirmar_largada.configure(state="disabled")
        app.btn_reiniciar.configure(state="normal")
        app.entry_chegada.configure(state="disabled")
        app.btn_registrar_chegada.configure(state="disabled")
        app.btn_finalizar_corrida.configure(state="disabled")

    def handle_reiniciar_prova(self, app):
        if messagebox.askyesno("Confirmar Reinício", "A prova está finalizada. Deseja reiniciar para uma nova cronometragem?"):
            app.db.reiniciar_prova()
            app.transition_to(PreparacaoState())