# -*- coding: utf-8 -*-
# Sistema de Cronometragem PRO v14.0 - Arquitetura Cliente-Servidor com Design Premium
import logging
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import customtkinter as ctk
import queue
from datetime import datetime, date, timedelta
import socket
from socket import timeout
import threading
import time

# IMPORTAÇÕES MODULARES
from .database_manager import DatabaseManager
from .business_logic import GerenciadorDeCorrida, Atleta
from .ui_states import PreparacaoState, EmCursoState, FinalizadoState, State
from .custom_exceptions import AtletaNaoEncontradoError, ChegadaJaRegistradaError, VoltaInvalidaError, CabecalhoInvalidoError
from .utils import formatar_timedelta
from .design_system import COLORS, FONTS, FONT_SIZES, SPACING, BORDERS, get_theme_config

class TextLogHandler(logging.Handler):
    """Handler customizado para redirecionar logs para um widget de texto do CTk."""
    def __init__(self, text_widget: ctk.CTkTextbox):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record: logging.LogRecord):
        # Usa 'after' para garantir que a atualização da UI ocorra no thread principal
        self.text_widget.after(0, self._append_log, self.format(record))

    def _append_log(self, msg: str):
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")


class AppCrono(ctk.CTk):
    """Sistema de Cronometragem Profissional com Design Premium"""
    
    def __init__(self):
        super().__init__()

        # Configurações do tema moderno
        self.theme = get_theme_config("dark")
        
        # Configurações Iniciais
        self._configurar_logger()
        self._configurar_janela()
        self._configurar_estilo_tabela()

        # Inicialização dos componentes de negócio
        self.db = DatabaseManager("race_data.db")
        self.db.attach(self)
        self.gerenciador = GerenciadorDeCorrida(self.db, self.logger)
        
        # --- NOVO: Componentes para a conexão com a Ponte RFID ---
        self.rfid_queue = queue.Queue()
        self.bridge_socket = None
        self.is_bridge_connected = False
        self.bridge_listener_thread = None
        
        self.data_do_evento = date.today()
        self.table_headers = ["Nº", "Nome", "Sexo", "Idade", "Categoria", "Modalidade", "Tempo Bruto"]
        self.table_column_ids = ["num", "nome", "sexo", "idade", "categoria", "modalidade", "tempo_bruto"]
        self.dados_tabela = [self.table_headers]
        self._coluna_ordenacao = ("Nº", False)

        # Construção da UI moderna
        self.current_state: State | None = None
        self._criar_interface()
        self.after(100, self._inicializacao_pos_ui)
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _configurar_logger(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _configurar_janela(self):
        """Configura a janela principal com design moderno"""
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.title("PV Cronometragem PRO v14.0 - Sistema Internacional")
        self.geometry("1400x900")  # Aumenta para comportar melhor layout
        # self.minsize(1200, 800)  # CustomTkinter não suporta minsize
        
        # Configura o fundo com cor do design system
        try:
            self.configure(fg_color=self.theme["bg_primary"])
        except (AttributeError, KeyError):
            # Fallback se não conseguir configurar
            pass

    def _configurar_estilo_tabela(self):
        """Configura o estilo moderno do ttk.Treeview com design system."""
        try:
            style = ttk.Style()
            
            # Cores do design system
            bg_color = self.theme["bg_secondary"]
            text_color = self.theme["text_primary"] 
            header_bg = COLORS["primary"]["blue"]
            selected_bg = COLORS["primary"]["green"]
            
            style.theme_use("default")
            style.configure("Treeview",
                            background=bg_color,
                            foreground=text_color,
                            fieldbackground=bg_color,
                            borderwidth=0,
                            rowheight=28)  # Altura maior para melhor legibilidade
            style.map('Treeview', background=[('selected', selected_bg)])
            
            style.configure("Treeview.Heading",
                            background=header_bg,
                            foreground="#FFFFFF",
                            font=(FONTS["primary"][0], FONT_SIZES["sm"], 'bold'),
                            relief="flat",
                            borderwidth=1)
            style.map("Treeview.Heading", 
                     background=[('active', COLORS["secondary"]["teal"])])
            style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
            
        except Exception as e:
            self.logger.warning(f"Não foi possível aplicar o estilo customizado ao Treeview: {e}")

    def _criar_interface(self):
        """Cria interface moderna com design system premium"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header com logo e ações principais
        self._criar_header().grid(row=0, column=0, padx=SPACING["lg"], pady=SPACING["md"], sticky="ew")

        # Frame principal com layout moderno
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=SPACING["lg"], pady=(0, SPACING["lg"]), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # TabView principal com estilo moderno
        self.tab_view = ctk.CTkTabview(main_frame, 
                                      corner_radius=BORDERS["radius"]["lg"],
                                      border_width=0)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["md"]))
        
        # Abas com ícones conceituais
        self.tab_view.add("⏱️ Cronometragem")
        self.tab_view.add("📝 Consulta / Edição") 
        self.tab_view.add("🏆 Resultados")
        self.tab_view.add("📊 Logs do Evento")
        
        self._popular_aba_cronometragem(self.tab_view.tab("⏱️ Cronometragem"))
        self._popular_aba_consulta(self.tab_view.tab("📝 Consulta / Edição"))
        self._popular_aba_resultados(self.tab_view.tab("🏆 Resultados"))
        self._popular_aba_logs(self.tab_view.tab("📊 Logs do Evento"))

        # Sidebar de controles modernizada
        self._criar_sidebar_controles(main_frame).grid(row=0, column=1, sticky="ns")

    def _criar_header(self):
        """Cria header moderno com branding e ações principais"""
        header_frame = ctk.CTkFrame(self, 
                                   fg_color=self.theme["bg_secondary"],
                                   corner_radius=BORDERS["radius"]["lg"])
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo/Título
        title_label = ctk.CTkLabel(header_frame, 
                                  text="🏃‍♂️ PV CRONOMETRAGEM PRO",
                                  font=(FONTS["display"][0], FONT_SIZES["2xl"], "bold"),
                                  text_color=self.theme["text_primary"])
        title_label.grid(row=0, column=0, padx=SPACING["lg"], pady=SPACING["md"], sticky="w")
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(header_frame,
                                     text="Sistema Internacional de Cronometragem Esportiva",
                                     font=(FONTS["primary"][0], FONT_SIZES["sm"]),
                                     text_color=self.theme["text_secondary"])
        subtitle_label.grid(row=1, column=0, padx=SPACING["lg"], pady=(0, SPACING["md"]), sticky="w")
        
        # Botões de ação principais
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, rowspan=2, padx=SPACING["lg"], pady=SPACING["md"], sticky="e")
        
        self.btn_importar = ctk.CTkButton(actions_frame, 
                                         text="📥 Importar Atletas",
                                         command=self._ui_importar_atletas,
                                         fg_color=self.theme["accent"],
                                         hover_color=COLORS["secondary"]["teal"],
                                         corner_radius=BORDERS["radius"]["md"],
                                         font=(FONTS["primary"][0], FONT_SIZES["sm"], "bold"))
        self.btn_importar.pack(side="left", padx=(0, SPACING["sm"]))
        
        self.btn_reiniciar = ctk.CTkButton(actions_frame, 
                                          text="🔄 Reiniciar Prova",
                                          command=self._ui_reiniciar_prova,
                                          fg_color=self.theme["error"],
                                          hover_color=COLORS["status"]["warning"],
                                          corner_radius=BORDERS["radius"]["md"],
                                          font=(FONTS["primary"][0], FONT_SIZES["sm"], "bold"))
        self.btn_reiniciar.pack(side="left")
        
        return header_frame

    def _criar_sidebar_controles(self, parent):
        """Cria sidebar moderna com controles de cronometragem"""
        sidebar = ctk.CTkFrame(parent,
                              fg_color=self.theme["bg_secondary"],
                              corner_radius=BORDERS["radius"]["lg"])
        sidebar.grid_columnconfigure(0, weight=1)
        
        # --- Frame de Conexão com a Ponte RFID ---
        self._criar_bridge_connection_frame(sidebar).grid(row=0, column=0, 
                                                          padx=SPACING["md"], 
                                                          pady=SPACING["md"], 
                                                          sticky="ew")
        
        # --- Status da Corrida ---
        status_frame = ctk.CTkFrame(sidebar, 
                                   fg_color=self.theme["bg_primary"],
                                   corner_radius=BORDERS["radius"]["md"])
        status_frame.grid(row=1, column=0, padx=SPACING["md"], pady=SPACING["sm"], sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Título da seção
        status_title = ctk.CTkLabel(status_frame, 
                                   text="📊 STATUS DO EVENTO",
                                   font=(FONTS["primary"][0], FONT_SIZES["lg"], "bold"),
                                   text_color=self.theme["text_primary"])
        status_title.grid(row=0, column=0, columnspan=2, pady=(SPACING["md"], SPACING["sm"]), sticky="w")
        
        # Status da corrida
        ctk.CTkLabel(status_frame, 
                    text="Corrida:",
                    font=(FONTS["primary"][0], FONT_SIZES["sm"], "bold"),
                    text_color=self.theme["text_secondary"]).grid(row=1, column=0, padx=SPACING["md"], pady=SPACING["xs"], sticky="e")
        
        self.label_status_corrida = ctk.CTkLabel(status_frame, 
                                               text="INICIANDO...",
                                               font=(FONTS["mono"][0], FONT_SIZES["sm"], "bold"),
                                               text_color=COLORS["status"]["warning"])
        self.label_status_corrida.grid(row=1, column=1, padx=SPACING["md"], sticky="w")
        
        # Status RFID
        ctk.CTkLabel(status_frame,
                    text="RFID:",
                    font=(FONTS["primary"][0], FONT_SIZES["sm"], "bold"),
                    text_color=self.theme["text_secondary"]).grid(row=2, column=0, padx=SPACING["md"], pady=(SPACING["xs"], SPACING["md"]), sticky="e")
        
        self.label_status_rfid = ctk.CTkLabel(status_frame,
                                            text="Desconectado",
                                            font=(FONTS["mono"][0], FONT_SIZES["sm"], "bold"),
                                            text_color=self.theme["error"])
        self.label_status_rfid.grid(row=2, column=1, padx=SPACING["md"], pady=(SPACING["xs"], SPACING["md"]), sticky="w")

        # --- Cronômetro Central ---
        crono_frame = ctk.CTkFrame(sidebar,
                                  fg_color=COLORS["background"]["dark"],
                                  corner_radius=BORDERS["radius"]["lg"],
                                  border_width=2,
                                  border_color=self.theme["accent"])
        crono_frame.grid(row=2, column=0, padx=SPACING["md"], pady=SPACING["md"], sticky="ew")
        crono_frame.grid_columnconfigure(0, weight=1)
        
        # Label do cronômetro com estilo premium
        self.label_cronometro = ctk.CTkLabel(crono_frame,
                                           text="00:00:00.000",
                                           font=(FONTS["mono"][0], FONT_SIZES["4xl"], "bold"),
                                           text_color=COLORS["primary"]["gold"])
        self.label_cronometro.grid(row=0, column=0, pady=SPACING["xl"])
        
        # --- Controles de Largada ---
        self._criar_controles_largada(sidebar).grid(row=3, column=0, 
                                                   padx=SPACING["md"], 
                                                   pady=SPACING["sm"], 
                                                   sticky="ew")
        
        # --- Controles de Chegada ---
        self._criar_controles_chegada(sidebar).grid(row=4, column=0,
                                                   padx=SPACING["md"],
                                                   pady=SPACING["sm"],
                                                   sticky="ew")
        
        # --- Botão Finalizar ---
        self.btn_finalizar_corrida = ctk.CTkButton(sidebar,
                                                  text="🏁 FINALIZAR CORRIDA",
                                                  command=self._ui_finalizar_corrida,
                                                  fg_color=self.theme["error"],
                                                  hover_color=COLORS["status"]["warning"],
                                                  corner_radius=BORDERS["radius"]["md"],
                                                  font=(FONTS["primary"][0], FONT_SIZES["lg"], "bold"),
                                                  height=50)
        self.btn_finalizar_corrida.grid(row=5, column=0, 
                                       padx=SPACING["md"], 
                                       pady=SPACING["lg"], 
                                       sticky="ew")
        
        return sidebar

    def _criar_controles_largada(self, parent):
        """Cria seção moderna de controles de largada"""
        controles_frame = ctk.CTkFrame(parent,
                                      fg_color=self.theme["bg_primary"],
                                      corner_radius=BORDERS["radius"]["md"])
        controles_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(controles_frame,
                                  text="🚀 LARGADA",
                                  font=(FONTS["primary"][0], FONT_SIZES["lg"], "bold"),
                                  text_color=self.theme["text_primary"])
        title_label.pack(pady=(SPACING["md"], SPACING["sm"]))
        
        # Input de horário
        time_label = ctk.CTkLabel(controles_frame,
                                 text="Horário (HH:MM:SS.ms)",
                                 font=(FONTS["primary"][0], FONT_SIZES["sm"]),
                                 text_color=self.theme["text_secondary"])
        time_label.pack()
        
        self.entry_horario_largada = ctk.CTkEntry(controles_frame,
                                                 justify="center",
                                                 font=(FONTS["mono"][0], FONT_SIZES["base"]),
                                                 corner_radius=BORDERS["radius"]["sm"],
                                                 border_width=2)
        self.entry_horario_largada.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Botão iniciar
        self.btn_confirmar_largada = ctk.CTkButton(controles_frame,
                                                  text="▶️ INICIAR PROVA",
                                                  command=self._ui_iniciar_prova,
                                                  fg_color=self.theme["success"],
                                                  hover_color=COLORS["secondary"]["teal"],
                                                  corner_radius=BORDERS["radius"]["md"],
                                                  font=(FONTS["primary"][0], FONT_SIZES["base"], "bold"),
                                                  height=40)
        self.btn_confirmar_largada.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]))
        
        return controles_frame

    def _criar_controles_chegada(self, parent):
        """Cria seção moderna de controles de chegada"""
        chegada_frame = ctk.CTkFrame(parent,
                                    fg_color=self.theme["bg_primary"],
                                    corner_radius=BORDERS["radius"]["md"])
        chegada_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(chegada_frame,
                                  text="🏃‍♂️ CHEGADA",
                                  font=(FONTS["primary"][0], FONT_SIZES["lg"], "bold"),
                                  text_color=self.theme["text_primary"])
        title_label.pack(pady=(SPACING["md"], SPACING["sm"]))
        
        # Input de número do atleta
        num_label = ctk.CTkLabel(chegada_frame,
                                text="Número do Atleta",
                                font=(FONTS["primary"][0], FONT_SIZES["sm"]),
                                text_color=self.theme["text_secondary"])
        num_label.pack()
        
        self.chegada_num_var = tk.StringVar()
        self.entry_chegada = ctk.CTkEntry(chegada_frame,
                                         textvariable=self.chegada_num_var,
                                         justify="center",
                                         font=(FONTS["mono"][0], FONT_SIZES["lg"]),
                                         corner_radius=BORDERS["radius"]["sm"],
                                         border_width=2,
                                         height=40)
        self.entry_chegada.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        self.entry_chegada.bind("<Return>", self._ui_registrar_chegada)
        
        # Botão registrar
        self.btn_registrar_chegada = ctk.CTkButton(chegada_frame,
                                                  text="⏰ REGISTRAR",
                                                  command=self._ui_registrar_chegada,
                                                  fg_color=COLORS["primary"]["gold"],
                                                  hover_color=COLORS["secondary"]["orange"],
                                                  corner_radius=BORDERS["radius"]["md"],
                                                  font=(FONTS["primary"][0], FONT_SIZES["base"], "bold"),
                                                  height=40)
        self.btn_registrar_chegada.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]))
        
        return chegada_frame

    def _criar_bridge_connection_frame(self, parent):
        """Cria frame moderno para conexão com ponte RFID"""
        bridge_frame = ctk.CTkFrame(parent,
                                   fg_color=COLORS["secondary"]["purple"],
                                   corner_radius=BORDERS["radius"]["md"])
        bridge_frame.grid_columnconfigure(1, weight=1)

        # Título da seção
        title_label = ctk.CTkLabel(bridge_frame,
                                  text="📡 PONTE RFID",
                                  font=(FONTS["primary"][0], FONT_SIZES["lg"], "bold"),
                                  text_color="#FFFFFF")
        title_label.grid(row=0, column=0, columnspan=2, pady=(SPACING["md"], SPACING["sm"]), sticky="w")

        # IP da ponte
        ctk.CTkLabel(bridge_frame,
                    text="IP:",
                    font=(FONTS["primary"][0], FONT_SIZES["sm"], "bold"),
                    text_color="#FFFFFF").grid(row=1, column=0, padx=SPACING["md"], pady=SPACING["xs"], sticky="w")
        
        self.bridge_ip_entry = ctk.CTkEntry(bridge_frame,
                                           placeholder_text="127.0.0.1",
                                           font=(FONTS["mono"][0], FONT_SIZES["sm"]),
                                           corner_radius=BORDERS["radius"]["sm"])
        self.bridge_ip_entry.grid(row=1, column=1, padx=(SPACING["xs"], SPACING["md"]), pady=SPACING["xs"], sticky="ew")
        self.bridge_ip_entry.insert(0, "127.0.0.1")

        # Porta
        ctk.CTkLabel(bridge_frame,
                    text="Porta:",
                    font=(FONTS["primary"][0], FONT_SIZES["sm"], "bold"),
                    text_color="#FFFFFF").grid(row=2, column=0, padx=SPACING["md"], pady=SPACING["xs"], sticky="w")
        
        self.bridge_port_entry = ctk.CTkEntry(bridge_frame,
                                             placeholder_text="9999",
                                             font=(FONTS["mono"][0], FONT_SIZES["sm"]),
                                             corner_radius=BORDERS["radius"]["sm"])
        self.bridge_port_entry.grid(row=2, column=1, padx=(SPACING["xs"], SPACING["md"]), pady=SPACING["xs"], sticky="ew")
        self.bridge_port_entry.insert(0, "9999")

        # Botão de conexão
        self.bridge_connect_button = ctk.CTkButton(bridge_frame,
                                                  text="🔗 Conectar à Ponte",
                                                  command=self.toggle_bridge_connection,
                                                  fg_color="#FFFFFF",
                                                  text_color=COLORS["secondary"]["purple"],
                                                  hover_color=COLORS["background"]["modal"],
                                                  corner_radius=BORDERS["radius"]["md"],
                                                  font=(FONTS["primary"][0], FONT_SIZES["sm"], "bold"))
        self.bridge_connect_button.grid(row=3, column=0, columnspan=2, 
                                       padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]), sticky="ew")
        
        return bridge_frame

    def toggle_bridge_connection(self):
        if not self.is_bridge_connected:
            self.start_bridge_connection()
        else:
            self.stop_bridge_connection()

    def start_bridge_connection(self):
        ip = self.bridge_ip_entry.get()
        port_str = self.bridge_port_entry.get()
        if not ip or not port_str:
            messagebox.showerror("Erro de Conexão", "O IP e a Porta da ponte devem ser preenchidos.")
            return
        
        try:
            port = int(port_str)
            self.bridge_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.bridge_socket.connect((ip, port))
            self.bridge_socket.settimeout(1.0)

            self.is_bridge_connected = True
            self.logger.info(f"Conectado à ponte RFID em {ip}:{port}")

            self.bridge_listener_thread = threading.Thread(target=self.listen_for_bridge_data, daemon=True)
            self.bridge_listener_thread.start()

            self.bridge_connect_button.configure(text="🔌 Desconectar", 
                                                 fg_color=COLORS["status"]["warning"],
                                                 text_color="#FFFFFF")
            self.label_status_rfid.configure(text="🟢 Conectado", 
                                            text_color=self.theme["success"])
            self.bridge_ip_entry.configure(state="disabled")
            self.bridge_port_entry.configure(state="disabled")

        except Exception as e:
            self.logger.error(f"Falha ao conectar à ponte RFID: {e}")
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar à ponte RFID.\nVerifique se a ponte está rodando e o IP/Porta estão corretos.\n\nErro: {e}")
            self.is_bridge_connected = False
            if self.bridge_socket:
                self.bridge_socket.close()

    def stop_bridge_connection(self):
        self.is_bridge_connected = False
        if self.bridge_socket:
            try:
                self.bridge_socket.close()
            except Exception as e:
                self.logger.warning(f"Erro ao fechar o soquete da ponte: {e}")
        
        # A thread listener vai parar sozinha pois is_bridge_connected é False
        self.logger.info("Desconectado da ponte RFID.")
        self.bridge_connect_button.configure(text="🔗 Conectar à Ponte", 
                                             fg_color="#FFFFFF",
                                             text_color=COLORS["secondary"]["purple"])
        self.label_status_rfid.configure(text="🔴 Desconectado", 
                                        text_color=self.theme["error"])
        self.bridge_ip_entry.configure(state="normal")
        self.bridge_port_entry.configure(state="normal")

    def listen_for_bridge_data(self):
        buffer = ""
        while self.is_bridge_connected:
            try:
                data = self.bridge_socket.recv(1024).decode('utf-8')
                if not data:
                    # Conexão fechada pelo servidor
                    self.logger.warning("A ponte RFID encerrou a conexão.")
                    self.after(0, self.stop_bridge_connection)
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.rfid_queue.put(line)

            except socket.timeout:
                continue # Apenas para permitir que o loop verifique is_bridge_connected
            except Exception as e:
                if self.is_bridge_connected:
                    self.logger.error(f"Erro recebendo dados da ponte: {e}")
                break
        self.logger.info("Thread de escuta da ponte finalizada.")

    def _popular_aba_cronometragem(self, parent):
        """Substitui CTkTable por um ttk.Treeview, que é mais robusto e eficiente."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # O container agora segura a tabela e a scrollbar
        self.tabela_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.tabela_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.tabela_container.grid_rowconfigure(0, weight=1)
        self.tabela_container.grid_columnconfigure(0, weight=1)

        # Criação do Treeview
        self.tabela_atletas = ttk.Treeview(self.tabela_container, columns=self.table_column_ids, show="headings")

        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(self.tabela_container, orient="vertical", command=self.tabela_atletas.yview)
        self.tabela_atletas.configure(yscrollcommand=scrollbar.set)

        # Configuração das colunas e cabeçalhos
        for col_id, col_text in zip(self.table_column_ids, self.table_headers):
            # O comando no heading agora cuida da ordenação
            self.tabela_atletas.heading(col_id, text=col_text, command=lambda c=col_text: self._ordenar_tabela(c))
            # Define larguras de coluna para melhor visualização
            if col_id == "nome":
                self.tabela_atletas.column(col_id, width=250, minwidth=150)
            elif col_id == "num":
                 self.tabela_atletas.column(col_id, width=50, anchor="center")
            else:
                self.tabela_atletas.column(col_id, width=80, anchor="center")

        self.tabela_atletas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")


    def _popular_aba_consulta(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(parent)
        frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(frame, text="Buscar Atleta (Nº):").grid(row=0, column=0, sticky="e")
        busca_var = tk.StringVar()
        entry_busca = ctk.CTkEntry(frame, textvariable=busca_var, width=80)
        entry_busca.grid(row=0, column=1, padx=5)
        btn_buscar = ctk.CTkButton(frame, text="Buscar", width=60)
        btn_buscar.grid(row=0, column=2, padx=5)

        # Campos de edição
        labels = ["Nome", "Sexo (M/F)", "Data Nascimento (dd/mm/aaaa)", "Categoria", "Modalidade"]
        edit_vars = [tk.StringVar() for _ in labels]
        for i, label in enumerate(labels):
            ctk.CTkLabel(frame, text=label + ":").grid(row=i+1, column=0, sticky="e")
            ctk.CTkEntry(frame, textvariable=edit_vars[i], width=200).grid(row=i+1, column=1, columnspan=2, sticky="w", pady=2)

        btn_salvar = ctk.CTkButton(frame, text="Salvar Alterações", fg_color=self.theme["success"])
        btn_salvar.grid(row=len(labels)+1, column=0, columnspan=3, pady=10)

        resultado_label = ctk.CTkLabel(frame, text="")
        resultado_label.grid(row=len(labels)+2, column=0, columnspan=3)

        def buscar():
            try:
                num = int(busca_var.get())
                atleta = self.db.obter_atleta_por_id(num)
                if not atleta:
                    resultado_label.configure(text="Atleta não encontrado.", text_color=self.THEME_COLORS["red"])
                    for v in edit_vars: v.set("")
                    return
                edit_vars[0].set(atleta["nome"])
                edit_vars[1].set(atleta["sexo"])
                edit_vars[2].set(atleta["data_nascimento"])
                edit_vars[3].set(atleta["categoria"])
                edit_vars[4].set(atleta["modalidade"])
                resultado_label.configure(text="Atleta encontrado. Você pode editar os dados abaixo.", text_color=self.THEME_COLORS["green"])
            except (ValueError, TypeError):
                resultado_label.configure(text="Número de busca inválido.", text_color=self.THEME_COLORS["red"])
                for v in edit_vars: v.set("")

        def salvar():
            try:
                num_str = busca_var.get()
                if not num_str:
                    resultado_label.configure(text="Busque um atleta primeiro para poder salvar.", text_color=self.THEME_COLORS["yellow"])
                    return

                num = int(num_str)
                nome, sexo, data_nasc, categoria, modalidade = [v.get().strip() for v in edit_vars]
                
                # Validação dos campos
                if not all([nome, sexo, data_nasc, categoria, modalidade]):
                    resultado_label.configure(text="Todos os campos devem ser preenchidos.", text_color=self.THEME_COLORS["red"])
                    return
                if sexo.upper() not in ('M', 'F'):
                    resultado_label.configure(text="Sexo deve ser 'M' ou 'F'.", text_color=self.THEME_COLORS["red"])
                    return
                # Adicionar validação de data se necessário (por enquanto, confiamos no formato)

                with self.db._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE atletas SET nome=?, sexo=?, data_nascimento=?, categoria=?, modalidade=? WHERE num=?",
                        (nome, sexo.upper(), data_nasc, categoria.upper(), modalidade, num)
                    )
                    conn.commit()
                
                self.logger.info(f"Dados do atleta #{num} atualizados pelo formulário de edição.")
                resultado_label.configure(text=f"Atleta #{num} atualizado com sucesso!", text_color=self.THEME_COLORS["green"])
                # CORREÇÃO: Chama o método centralizado para atualizar a tabela.
                self._ordenar_tabela(self._coluna_ordenacao[0], manter_direcao=True)

                # Limpa os campos para a próxima operação
                busca_var.set("")
                for v in edit_vars: v.set("")

            except ValueError:
                resultado_label.configure(text="Número do atleta na busca é inválido.", text_color=self.THEME_COLORS["red"])
            except Exception as e:
                self.logger.error(f"Erro ao salvar dados do atleta #{busca_var.get()}: {e}")
                resultado_label.configure(text=f"Erro ao salvar: {e}", text_color=self.THEME_COLORS["red"])

        btn_buscar.configure(command=buscar)
        btn_salvar.configure(command=salvar)

    def _popular_aba_resultados(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # Imports necessários para esta aba
        import tkinter as tk
        from collections import OrderedDict
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from customtkinter import CTkScrollableFrame
        from datetime import timedelta

        # --- WIDGETS ---
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Frame para os filtros
        filtro_frame = ctk.CTkFrame(container)
        filtro_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ctk.CTkLabel(filtro_frame, text="Sexo:").pack(side="left", padx=(10, 2))
        sexo_var = tk.StringVar(value="Ambos")
        ctk.CTkOptionMenu(filtro_frame, variable=sexo_var, values=["Ambos", "Masculino", "Feminino"]).pack(side="left", padx=2)

        ctk.CTkLabel(filtro_frame, text="Categoria:").pack(side="left", padx=(10, 2))
        categoria_var = tk.StringVar(value="Todas")
        categorias = ["Todas", "GERAL", "PCD"]
        ctk.CTkOptionMenu(filtro_frame, variable=categoria_var, values=categorias).pack(side="left", padx=2)

        ctk.CTkLabel(filtro_frame, text="Faixa Etária:").pack(side="left", padx=(10, 2))
        faixa_var = tk.StringVar(value="Todas")
        faixas = ["Todas", "Até 19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70+"]
        ctk.CTkOptionMenu(filtro_frame, variable=faixa_var, values=faixas).pack(side="left", padx=2)

        # Frame para os botões, alinhado à direita
        button_frame = ctk.CTkFrame(filtro_frame, fg_color="transparent")
        button_frame.pack(side="right", padx=(10, 5))
        btn_filtrar = ctk.CTkButton(button_frame, text="Atualizar Relatório", width=150)
        btn_filtrar.pack(side="left", padx=5)
        btn_pdf = ctk.CTkButton(button_frame, text="🏆 Gerar PDF Premium", width=180)
        btn_pdf.pack(side="left", padx=5)

        # Frame rolável para exibir os pódios
        scroll_frame = CTkScrollableFrame(container, label_text="Relatório de Pódios da Prova")
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        # --- LÓGICA ---
        self.dados_relatorio_agrupado = OrderedDict()

        def _get_faixa_etaria_label(idade: int) -> str:
            if idade <= 19: return "Até 19"
            if idade >= 70: return "70+"
            faixa_min = (idade // 5) * 5
            faixa_max = faixa_min + 4
            return f"{faixa_min}-{faixa_max}"

        def _gerar_dados_relatorio():
            self.logger.info("Gerando e agrupando dados para o relatório de resultados...")
            self.dados_relatorio_agrupado.clear()

            atletas_com_tempo = [r for r in self.db.obter_todos_atletas_para_tabela("Tempo Líquido", False) if r["tempo_liquido"] is not None]
            if not atletas_com_tempo:
                self.logger.warning("Nenhum atleta com tempo finalizado para gerar relatório.")
                return

            # Estruturas para agrupar atletas
            geral_masc, geral_fem = [], []
            pcd_masc, pcd_fem = [], []
            faixas_geral_m, faixas_geral_f = {}, {}
            faixas_pcd_m, faixas_pcd_f = {}, {}

            for row in atletas_com_tempo:
                try:
                    idade = Atleta._calcular_idade(row["data_nascimento"], self.data_do_evento)
                    faixa_label = _get_faixa_etaria_label(idade)
                    atleta_info = (row, idade)

                    is_pcd = row['categoria'].upper() == 'PCD'
                    is_male = row['sexo'] == 'M'

                    if is_pcd:
                        if is_male:
                            pcd_masc.append(atleta_info)
                            faixas_pcd_m.setdefault(faixa_label, []).append(atleta_info)
                        else:
                            pcd_fem.append(atleta_info)
                            faixas_pcd_f.setdefault(faixa_label, []).append(atleta_info)
                    else: # GERAL
                        if is_male:
                            geral_masc.append(atleta_info)
                            faixas_geral_m.setdefault(faixa_label, []).append(atleta_info)
                        else:
                            geral_fem.append(atleta_info)
                            faixas_geral_f.setdefault(faixa_label, []).append(atleta_info)
                except Exception as e:
                    self.logger.warning(f"Atleta #{row['num']} ignorado nos resultados devido a erro: {e}")

            # Monta a estrutura de dados final (OrderedDict para manter a ordem)
            self.dados_relatorio_agrupado["Pódio Geral Masculino (Top 5)"] = geral_masc[:5]
            self.dados_relatorio_agrupado["Pódio Geral Feminino (Top 5)"] = geral_fem[:5]
            if pcd_masc: self.dados_relatorio_agrupado["Pódio PCD Masculino (Geral)"] = pcd_masc
            if pcd_fem: self.dados_relatorio_agrupado["Pódio PCD Feminino (Geral)"] = pcd_fem

            ids_podio_geral = {a[0]['num'] for a in geral_masc[:5]} | {a[0]['num'] for a in geral_fem[:5]}

            for faixa, atletas in sorted(faixas_geral_m.items()):
                atletas_faixa = [a for a in atletas if a[0]['num'] not in ids_podio_geral]
                if atletas_faixa: self.dados_relatorio_agrupado[f"GERAL Masculino {faixa}"] = atletas_faixa[:3]
            
            for faixa, atletas in sorted(faixas_geral_f.items()):
                atletas_faixa = [a for a in atletas if a[0]['num'] not in ids_podio_geral]
                if atletas_faixa: self.dados_relatorio_agrupado[f"GERAL Feminino {faixa}"] = atletas_faixa[:3]

            for faixa, atletas in sorted(faixas_pcd_m.items()):
                if atletas: self.dados_relatorio_agrupado[f"PCD Masculino {faixa}"] = atletas[:3]
            for faixa, atletas in sorted(faixas_pcd_f.items()):
                if atletas: self.dados_relatorio_agrupado[f"PCD Feminino {faixa}"] = atletas[:3]
            
            self.logger.info("Dados do relatório gerados com sucesso.")

        def _atualizar_exibicao_relatorio():
            self.logger.info("Atualizando exibição do relatório de pódios...")
            for widget in scroll_frame.winfo_children(): widget.destroy()

            sexo_f = sexo_var.get()
            cat_f = categoria_var.get().upper()
            faixa_f = faixa_var.get()

            grupos_a_exibir = OrderedDict()
            for titulo, atletas in self.dados_relatorio_agrupado.items():
                if not atletas: continue
                
                # Lógica de filtragem
                if sexo_f == "Masculino" and "Feminino" in titulo: continue
                if sexo_f == "Feminino" and "Masculino" in titulo: continue
                if cat_f != "TODAS" and cat_f not in titulo: continue
                if faixa_f != "Todas":
                    if "Geral)" in titulo: continue # Oculta pódios gerais se faixa etária específica for selecionada
                    if faixa_f not in titulo: continue
                
                grupos_a_exibir[titulo] = atletas

            if not grupos_a_exibir:
                ctk.CTkLabel(scroll_frame, text="Nenhum pódio encontrado para os filtros selecionados.", font=("Roboto", 16)).pack(pady=20)
                return

            for titulo, atletas in grupos_a_exibir.items():
                frame_podio = ctk.CTkFrame(scroll_frame)
                frame_podio.pack(fill="x", expand=True, pady=5, padx=5)
                
                label_titulo = ctk.CTkLabel(frame_podio, text=titulo, font=("Roboto", 16, "bold"), anchor="w")
                label_titulo.pack(fill="x", padx=10, pady=(5, 5))

                # NOVO: Usa ttk.Treeview para os pódios, eliminando CTkTable
                podio_container = ctk.CTkFrame(frame_podio, fg_color="transparent")
                podio_container.pack(expand=True, fill="x", padx=10, pady=(0, 10))
                podio_container.grid_columnconfigure(0, weight=1)

                col_ids = ("pos", "num", "nome", "idade", "tempo_bruto")
                col_headings = ("Pos.", "Nº", "Nome", "Idade", "Tempo Bruto")

                # A altura da tabela é definida pelo número de atletas para ser compacta
                tree = ttk.Treeview(podio_container, columns=col_ids, show="headings", height=len(atletas))

                for cid, chead in zip(col_ids, col_headings):
                    tree.heading(cid, text=chead)
                    # Define larguras de coluna para melhor visualização
                    if cid == "nome":
                        tree.column(cid, width=250, minwidth=150)
                    elif cid == "pos" or cid == "num":
                        tree.column(cid, width=40, anchor="center")
                    else:
                        tree.column(cid, width=80, anchor="center")

                # Preenche a tabela com os dados
                for i, (row, idade) in enumerate(atletas, 1):
                    tempo = formatar_timedelta(timedelta(seconds=row["tempo_liquido"]))
                    tree.insert("", "end", values=(i, row["num"], row["nome"], idade, tempo))

                tree.grid(row=0, column=0, sticky="ew")
            
            self.logger.info(f"{len(grupos_a_exibir)} grupos de pódio exibidos.")

        def _executar_atualizacao_completa():
            _gerar_dados_relatorio()
            _atualizar_exibicao_relatorio()

        def gerar_pdf():
            """Gera relatório PDF moderno usando o sistema premium"""
            try:
                from .modern_reports import ModernReportGenerator
                
                sexo_f = sexo_var.get()
                cat_f = categoria_var.get()
                faixa_f = faixa_var.get()

                # Re-filtra os dados para garantir que o PDF corresponda à UI
                grupos_para_pdf = OrderedDict()
                for titulo, atletas in self.dados_relatorio_agrupado.items():
                    if not atletas: continue
                    if sexo_f == "Masculino" and "Feminino" in titulo: continue
                    if sexo_f == "Feminino" and "Masculino" in titulo: continue
                    if cat_f.upper() != "TODAS" and cat_f.upper() not in titulo: continue
                    if faixa_f != "Todas":
                        if "Geral)" in titulo: continue
                        if faixa_f not in titulo: continue
                    grupos_para_pdf[titulo] = atletas

                if not grupos_para_pdf:
                    messagebox.showinfo("PDF", "Nenhum resultado para exportar com os filtros atuais.")
                    return

                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf", 
                    filetypes=[("PDF files", "*.pdf")], 
                    title="Salvar Relatório Premium em PDF"
                )
                if not file_path: 
                    return

                # Prepara dados do evento
                evento_data = {
                    'nome': getattr(self.gerenciador_corrida, 'nome_evento', 'Corrida AppCrono'),
                    'local': getattr(self.gerenciador_corrida, 'local_evento', 'Local não informado'),
                    'data': date.today().strftime('%d/%m/%Y'),
                    'distancia': getattr(self.gerenciador_corrida, 'distancia', 'Distância variada'),
                    'categorias': ', '.join(grupos_para_pdf.keys()) if grupos_para_pdf else 'Geral',
                    'total_atletas': sum(len(atletas) for atletas in grupos_para_pdf.values()),
                    'filtros': f"Sexo: {sexo_f} | Categoria: {cat_f} | Faixa: {faixa_f}"
                }

                # Converte dados para formato do relatório moderno
                resultados_modernos = []
                for titulo, atletas in grupos_para_pdf.items():
                    for i, (row, idade) in enumerate(atletas, 1):
                        resultado = {
                            'posicao': i,
                            'numero': str(row["num"]),
                            'nome': row["nome"],
                            'categoria': titulo.split('(')[0].strip() if '(' in titulo else 'Geral',
                            'idade': idade,
                            'tempo_segundos': row["tempo_liquido"],
                            'tempo_formatado': formatar_timedelta(timedelta(seconds=row["tempo_liquido"])),
                            'sexo': 'M' if 'Masculino' in titulo else 'F' if 'Feminino' in titulo else 'Misto'
                        }
                        resultados_modernos.append(resultado)

                # Gera relatório premium
                generator = ModernReportGenerator()
                arquivo_gerado = generator.generate_results_report(
                    evento_data=evento_data,
                    resultados=resultados_modernos,
                    output_path=file_path
                )

                messagebox.showinfo(
                    "PDF Premium Gerado! 🏆", 
                    f"Relatório premium salvo com sucesso!\n\n📁 {arquivo_gerado}\n\n✨ Design internacional aplicado com paleta moderna e tipografia profissional."
                )
                
            except ImportError as e:
                self.logger.error(f"Módulo de relatórios modernos não encontrado: {e}")
                messagebox.showerror("Erro de Importação", 
                    "Sistema de relatórios premium não disponível.\nVerifique se o ReportLab está instalado.")
            except Exception as e:
                self.logger.error(f"Erro ao gerar PDF premium: {e}")
                messagebox.showerror("Erro de PDF", f"Não foi possível gerar o relatório premium:\n{e}")

        btn_filtrar.configure(command=_atualizar_exibicao_relatorio)
        btn_pdf.configure(command=gerar_pdf)
        
        # Carrega os resultados iniciais ao construir a UI
        self.after(200, _executar_atualizacao_completa)

    def _popular_aba_logs(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        self.log_text_widget = ctk.CTkTextbox(parent, wrap="word", state="disabled")
        self.log_text_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        log_handler = TextLogHandler(self.log_text_widget)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        self.logger.addHandler(log_handler)

    def _inicializacao_pos_ui(self):
        """Executa tarefas de inicialização que dependem da UI já estar criada."""
        # Configura o handler de log para o widget de texto
        log_handler = TextLogHandler(self.log_text_widget)
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        log_handler.setFormatter(log_formatter)
        self.logger.addHandler(log_handler)

        self.logger.info("Interface Gráfica Carregada.")
        self.logger.info("Bem-vindo ao PV Cronometragem!")

        try:
            self.db.init_db()
            self.logger.info("Banco de dados inicializado com sucesso.")
        except Exception as e:
            self.logger.critical(f"Falha CRÍTICA ao inicializar o banco de dados: {e}")
            messagebox.showerror("Erro Crítico", f"Não foi possível iniciar o banco de dados: {e}")
            self.destroy()
            return

        self.current_state = PreparacaoState(self)
        self._ordenar_tabela(self._coluna_ordenacao[0], manter_direcao=True)
        self._processar_fila_rfid() # Inicia o processamento da fila

    def _on_closing(self):
        """Garante que tudo seja finalizado corretamente."""
        if self.is_bridge_connected:
            self.stop_bridge_connection()
        self.destroy()

    def _processar_fila_rfid(self):
        """Processa continuamente a fila de leituras RFID."""
        try:
            while not self.rfid_queue.empty():
                leitura = self.rfid_queue.get_nowait()
                self.logger.debug(f"Processando da fila: {leitura}")
                # Formato esperado: "TAG_ID,ANTENA"
                partes = leitura.strip().split(',')
                if len(partes) == 2:
                    tag_id, antena_str = partes
                    self._ui_registrar_chegada_rfid(tag_id, int(antena_str))
                else:
                    self.logger.warning(f"Leitura RFID em formato inesperado ignorada: {leitura}")

        except queue.Empty:
            pass # Normal, a fila estava vazia
        finally:
            # Reagenda a si mesmo para rodar novamente, criando um loop
            self.after(100, self._processar_fila_rfid)

    def _ui_registrar_chegada_rfid(self, tag_id: str, antena: int):
        """Lógica para registrar uma chegada vinda do leitor RFID."""
        if not isinstance(self.current_state, EmCursoState):
            self.logger.warning(f"Leitura RFID da tag {tag_id} ignorada (a corrida não está em curso).")
            return
        try:
            # A lógica de negócio agora pode usar a informação da antena se necessário
            atleta = self.gerenciador.registrar_chegada_por_rfid(tag_id)
            self.logger.info(f"[RFID Antena {antena}] Chegada registrada para o atleta #{atleta.num} ({atleta.nome}) com a tag {tag_id}.")
            # Opcional: Limpar o campo de entrada manual se a chegada for por RFID
            self.chegada_num_var.set("")
        except AtletaNaoEncontradoError:
            self.logger.error(f"[RFID Antena {antena}] Tag RFID \"{tag_id}\" lida, mas nenhum atleta corresponde a ela.")
        except ChegadaJaRegistradaError as e:
            self.logger.warning(f"[RFID Antena {antena}] {e}")
        except Exception as e:
            self.logger.critical(f"[RFID Antena {antena}] Erro inesperado ao processar tag {tag_id}: {e}")

    # OBSERVER PATTERN: Este é o método chamado pelo 'Subject' (DatabaseManager).
    def update(self, subject=None):
        if isinstance(subject, DatabaseManager):
            self.logger.info("Recebida notificação de atualização. Agendando atualização da UI.")
            # CORREÇÃO: Usa self.after() para agendar a atualização da UI no loop principal do Tkinter.
            # Isso evita conflitos e garante que a UI seja redesenhada de forma segura e eficiente,
            # resolvendo o bug onde a tabela não atualizava após a importação.
            # A chamada agora é para _ordenar_tabela, que centraliza a lógica.
            self.after(50, lambda: self._ordenar_tabela(self._coluna_ordenacao[0], manter_direcao=True))
            self.after(100, lambda: self.current_state.handle_ui_update(self)) # Reavalia o estado dos botões

    def _atualizar_relogios(self):
        if isinstance(self.current_state, EmCursoState):
            horario_largada_str = self.db.carregar_estado_corrida('horario_largada')
            if isinstance(horario_largada_str, str) and horario_largada_str:
                decorrido = datetime.now() - datetime.fromisoformat(horario_largada_str)
                self.label_cronometro.configure(text=formatar_timedelta(decorrido))
        self.after(100, self._atualizar_relogios)

    def _ui_importar_atletas(self): self.current_state.handle_importar_atletas(self)
    def _ui_iniciar_prova(self): self.current_state.handle_iniciar_prova(self, self.entry_horario_largada.get())
    def _ui_registrar_chegada(self, event=None): self.current_state.handle_registrar_chegada(self, self.chegada_num_var.get())
    def _ui_finalizar_corrida(self): self.current_state.handle_finalizar_corrida(self)
    def _ui_reiniciar_prova(self): self.current_state.handle_reiniciar_prova(self)
    
    # O método _ui_clique_tabela foi removido pois o comando de ordenação
    # agora está diretamente no cabeçalho do Treeview.

    def _executar_importacao_atletas(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not caminho: return
        try:
            sucesso, erros = self.gerenciador.carregar_atletas_csv(caminho, self.data_do_evento)
            msg_final = f"Sucesso: {sucesso} atletas carregados.\nErros: {len(erros)} linhas ignoradas."
            if erros:
                msg_final += "\n\nConsulte a aba 'Logs do Evento' para detalhes."
                # CORREÇÃO: Adiciona a ação que faltava dentro do loop, que é logar o erro.
                for erro in erros:
                    self.logger.warning(f"Erro na importação de linha do CSV: {erro}")

            messagebox.showinfo("Importação Concluída", msg_final)
            # A atualização da tabela agora é tratada de forma confiável pelo padrão Observer (método update)
        except CabecalhoInvalidoError as e:
            messagebox.showerror("Erro de Cabeçalho", f"O cabeçalho do arquivo CSV está inválido:\n{e}")
            self.logger.error(f"Erro de cabeçalho na importação de CSV: {e}")
        except Exception as e:
            messagebox.showerror("Erro Crítico na Importação", f"Não foi possível processar o arquivo:\n{e}")
            self.logger.critical(f"Falha total ao carregar CSV: {e}")

    def _ordenar_tabela(self, coluna: str, manter_direcao=False):
        """
        Busca os dados do banco, formata-os e atualiza a tabela na UI.
        Este método é o ponto central para todas as atualizações da tabela de atletas.
        """
        self.logger.debug(f"Ordenando tabela pela coluna '{coluna}', manter_direcao={manter_direcao}")
        coluna_atual, reverso_atual = self._coluna_ordenacao

        # Determina a nova direção da ordenação
        if manter_direcao:
            reverso = reverso_atual
        else:
            reverso = not reverso_atual if coluna_atual == coluna else False
        
        self._coluna_ordenacao = (coluna, reverso)

        # Mapeia o nome da coluna da UI para o nome da coluna do DB
        map_coluna_db = {
            "Nº": "num",
            "Nome": "nome",
            "Sexo": "sexo",
            "Idade": "data_nascimento", # A ordenação por idade é feita no código após a busca
            "Categoria": "categoria",
            "Modalidade": "modalidade",
            "Tempo Bruto": "tempo_liquido"
        }
        coluna_db = map_coluna_db.get(coluna, "num")

        try:
            # 1. Busca os dados brutos do banco de dados
            dados_brutos = self.db.obter_todos_atletas_para_tabela(coluna_db, reverso)

            # 2. Processa os dados para exibição
            self.dados_tabela = [self.table_headers]
            for r in dados_brutos:
                try:
                    idade = Atleta._calcular_idade(r['data_nascimento'], self.data_do_evento)
                    tempo_bruto_str = formatar_timedelta(timedelta(seconds=r['tempo_liquido'])) if r['tempo_liquido'] is not None else "00:00:00.000"
                    self.dados_tabela.append([
                        r['num'], r['nome'], r['sexo'], idade, r['categoria'], r['modalidade'], tempo_bruto_str
                    ])
                except Exception as e:
                    self.logger.warning(f"Erro ao processar atleta #{r.get('num', 'N/A')} para a tabela: {e}")
            
            # Ordenação especial por idade, que não pode ser feita diretamente no SQL
            if coluna == "Idade":
                # Pega o índice da coluna "Idade"
                idx_idade = self.table_headers.index("Idade")
                # Separa o cabeçalho dos dados, ordena os dados pela idade, e junta novamente
                header = self.dados_tabela[0]
                data_rows = self.dados_tabela[1:]
                data_rows.sort(key=lambda row: row[idx_idade], reverse=reverso)
                self.dados_tabela = [header] + data_rows

            # 3. Atualiza o widget da tabela na UI
            # CORREÇÃO DEFINITIVA: A tabela (Treeview) agora é atualizada de forma eficiente,
            # limpando as linhas existentes e inserindo as novas, sem destruir o widget.
            # Isso elimina o "flickering" (pisca-pisca).
            if hasattr(self, 'tabela_atletas') and self.tabela_atletas.winfo_exists():
                # 1. Limpa todas as linhas antigas da tabela
                for i in self.tabela_atletas.get_children():
                    self.tabela_atletas.delete(i)
                
                # 2. Insere as novas linhas (pulando o cabeçalho da nossa lista de dados)
                for row_data in self.dados_tabela[1:]:
                    self.tabela_atletas.insert("", "end", values=row_data)

                self.logger.info(f"Tabela (Treeview) atualizada com {len(self.dados_tabela) - 1} registros.")
            else:
                self.logger.warning("O widget da tabela (Treeview) não existe, não foi possível atualizar.")

        except Exception as e:
            self.logger.error(f"Falha crítica ao ordenar e atualizar a tabela: {e}", exc_info=True)
            messagebox.showerror("Erro de Tabela", f"Não foi possível atualizar a tabela de atletas:\n{e}")

# PONTO DE ENTRADA DA APLICAÇÃO
if __name__ == "__main__":
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    
    try:
        app = AppCrono()
        app.mainloop()
    except Exception as e:
        logging.critical("Erro fatal ao iniciar a aplicação.", exc_info=True)

