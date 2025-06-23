import customtkinter as ctk
import tkinter as tk
import socket
import threading
import time
from .rfid_reader import RFIDReader, MockRFIDReader

class RFIDBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RFID Bridge")
        self.geometry("400x450") # Increased height for logs

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Adjusted row for log

        # --- Server and Reader State ---
        self.server = None
        self.server_thread = None
        self.reader_thread = None
        self.is_running = False
        self.clients = []
        # Use MockRFIDReader for development without hardware
        # self.rfid_reader = MockRFIDReader()
        self.rfid_reader = None # To be initialized

        # --- Connection Frame ---
        self.connection_frame = ctk.CTkFrame(self)
        self.connection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.connection_frame.grid_columnconfigure(1, weight=1)

        self.serial_port_label = ctk.CTkLabel(self.connection_frame, text="Porta Serial:")
        self.serial_port_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.serial_port_entry = ctk.CTkEntry(self.connection_frame, placeholder_text="/dev/ttyUSB0")
        self.serial_port_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.ip_label = ctk.CTkLabel(self.connection_frame, text="IP do Servidor:")
        self.ip_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ip_entry = ctk.CTkEntry(self.connection_frame, placeholder_text="0.0.0.0")
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.ip_entry.insert(0, "0.0.0.0")


        self.port_label = ctk.CTkLabel(self.connection_frame, text="Porta:")
        self.port_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.port_entry = ctk.CTkEntry(self.connection_frame, placeholder_text="9999")
        self.port_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.port_entry.insert(0, "9999")

        self.toggle_button = ctk.CTkButton(self, text="Iniciar Servidor", command=self.toggle_server)
        self.toggle_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # --- Status Frame ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.status_frame, text="Status: Desconectado", text_color="red")
        self.status_label.grid(row=0, column=0, padx=5, pady=5)

        # --- Antennas Frame ---
        self.antennas_frame = ctk.CTkFrame(self)
        self.antennas_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.antennas_frame.grid_columnconfigure(1, weight=1) # Ensure counter column expands
        ctk.CTkLabel(self.antennas_frame, text="Leituras por Antena").grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.antenna_labels = {}
        self.antenna_counters = {}
        for i in range(1, 5): # Assuming 4 antennas
            label = ctk.CTkLabel(self.antennas_frame, text=f"Antena {i}:")
            label.grid(row=i, column=0, padx=10, pady=2, sticky="w")
            self.antenna_labels[i] = label

            counter = ctk.CTkLabel(self.antennas_frame, text="0")
            counter.grid(row=i, column=1, padx=10, pady=2, sticky="e")
            self.antenna_counters[i] = counter

        # --- Log Frame ---
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_textbox = ctk.CTkTextbox(self.log_frame, state="disabled")
        self.log_textbox.grid(row=0, column=0, sticky="nsew")


    def log(self, message):
        """Appends a message to the log textbox."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")


    def toggle_server(self):
        if not self.is_running:
            self.start_server()
        else:
            self.stop_server()

    def start_server(self):
        serial_port = self.serial_port_entry.get()
        ip = self.ip_entry.get()

        if not serial_port:
            self.log("Erro: A porta serial deve ser especificada.")
            return

        try:
            port = int(self.port_entry.get())
        except (ValueError, TypeError):
            self.log("Erro: A porta do servidor deve ser um número válido.")
            return

        try:
            # Use MockRFIDReader if serial_port is 'mock' for testing purposes
            if serial_port.lower() == 'mock':
                self.rfid_reader = MockRFIDReader()
                self.log("Leitor RFID iniciado (Mock).")
            else:
                self.rfid_reader = RFIDReader(serial_port)
                self.log(f"Iniciando o leitor RFID na porta {serial_port}...")
            
            self.rfid_reader.start()

            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((ip, port))
            self.server.listen(5)
            self.log(f"Servidor escutando em {ip}:{port}")

            self.is_running = True

            self.server_thread = threading.Thread(target=self.listen_for_clients, daemon=True)
            self.server_thread.start()

            self.reader_thread = threading.Thread(target=self.listen_for_reads, daemon=True)
            self.reader_thread.start()

            self.toggle_button.configure(text="Parar Servidor")
            self.status_label.configure(text="Status: Rodando", text_color="green")
            self.serial_port_entry.configure(state="disabled")
            self.ip_entry.configure(state="disabled")
            self.port_entry.configure(state="disabled")

        except Exception as e:
            self.log(f"Erro ao iniciar: {e}")
            if self.rfid_reader:
                self.rfid_reader.stop()


    def stop_server(self):
        self.log("Parando o servidor...")
        self.is_running = False

        if self.rfid_reader:
            self.rfid_reader.stop()
            self.log("Leitor RFID parado.")

        for client in self.clients:
            client.close()
        self.clients.clear()

        if self.server:
            self.server.close()
            self.log("Soquete do servidor fechado.")

        # Threads são daemon, então não precisamos de join()

        self.toggle_button.configure(text="Iniciar Servidor")
        self.status_label.configure(text="Status: Desconectado", text_color="red")
        self.serial_port_entry.configure(state="normal")
        self.ip_entry.configure(state="normal")
        self.port_entry.configure(state="normal")
        self.log("Servidor parado.")

    def listen_for_clients(self):
        try:
            while self.is_running:
                self.server.settimeout(1.0) # Timeout para permitir a verificação de self.is_running
                try:
                    client_socket, addr = self.server.accept()
                    self.clients.append(client_socket)
                    self.log(f"Cliente conectado: {addr}")
                except socket.timeout:
                    continue
        except Exception as e:
            if self.is_running: # Evita log de erro ao fechar normalmente
                self.log(f"Erro no listener de clientes: {e}")

    def handle_client(self, client_socket):
        # Apenas mantém a conexão. A transmissão é feita pelo listen_for_reads
        while self.is_running:
            try:
                # Pequeno sleep para não sobrecarregar o processador
                time.sleep(1)
            except Exception:
                break
        self.log("Cliente desconectado.")
        self.clients.remove(client_socket)
        client_socket.close()

    def listen_for_reads(self):
        while self.is_running:
            try:
                tag_read = self.rfid_reader.get_read()
                if tag_read:
                    tag_id, antenna = tag_read
                    message = f"{tag_id},{antenna}"
                    self.log(f"Lido: {message}")
                    self.broadcast(message + '\n')
                    self.update_antenna_count(antenna)
                time.sleep(0.1) # Evita uso excessivo da CPU
            except Exception as e:
                self.log(f"Erro ao ler tag: {e}")
                break

    def broadcast(self, message):
        for client in self.clients[:]: # Itera sobre uma cópia
            try:
                client.sendall(message.encode('utf-8'))
            except (socket.error, BrokenPipeError):
                self.log("Cliente se desconectou, removendo.")
                self.clients.remove(client)
                client.close()

    def update_antenna_count(self, antenna):
        current_count = int(self.antenna_counters[antenna].cget("text"))
        self.antenna_counters[antenna].configure(text=str(current_count + 1))

    def on_closing(self):
        if self.is_running:
            self.stop_server()
        self.destroy()

if __name__ == "__main__":
    app = RFIDBridgeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
