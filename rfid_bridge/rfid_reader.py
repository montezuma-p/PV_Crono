import serial
import threading
import time
import queue

class RFIDReader:
    """Lida com a comunicação com o leitor RFID em uma thread separada."""

    def __init__(self, data_queue, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        """Inicializa o leitor.

        Args:
            data_queue (queue.Queue): Fila para enviar os dados lidos para a thread principal.
            port (str): A porta serial a ser usada (ex: 'COM3' no Windows, '/dev/ttyUSB0' no Linux).
            baudrate (int): A taxa de transmissão em bits por segundo.
            timeout (int): Tempo de espera para leitura da porta serial.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.data_queue = data_queue
        self.serial_connection = None
        self.is_running = False
        self.thread = None
        self.connection_status = "Desconectado"

    def _read_loop(self):
        """Loop principal que roda em uma thread para ler dados da porta serial."""
        while self.is_running:
            if self.serial_connection is None or not self.serial_connection.is_open:
                try:
                    self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                    self.connection_status = "Conectado"
                    print(f"[RFID] Conectado à porta {self.port}")
                except serial.SerialException:
                    self.connection_status = f"Falha ao conectar a {self.port}"
                    # print(f"[RFID] Erro: Não foi possível abrir a porta serial {self.port}. Tentando novamente em 5 segundos...")
                    time.sleep(5)
                    continue

            try:
                # A função readline() com timeout evita o busy-waiting.
                # Ela bloqueará por até 'timeout' segundos esperando por dados.
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    print(f"[RFID] Dado bruto recebido: '{line}'")
                    self.data_queue.put(line) # Coloca o número lido na fila
            except serial.SerialException:
                print("[RFID] Erro: A porta serial foi desconectada.")
                self.connection_status = "Desconectado"
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.close()
                self.serial_connection = None
                time.sleep(2)
            except Exception as e:
                print(f"[RFID] Erro inesperado: {e}")
                time.sleep(2)

    def start(self):
        """Inicia a thread de leitura do RFID."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            print("[RFID] Leitor iniciado.")

    def stop(self):
        """Para a thread de leitura do RFID e fecha a conexão serial."""
        if self.is_running:
            self.is_running = False
            if self.thread and self.thread.is_alive():
                self.thread.join() # Espera a thread terminar
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
            self.connection_status = "Desconectado"
            print("[RFID] Leitor parado.")


class MockRFIDReader:
    """
    A mock version of the RFIDReader for testing purposes.
    It simulates reading tags without requiring a physical device.
    """
    def __init__(self, serial_port, **kwargs):
        """
        Initializes the mock reader. The parameters are for compatibility
        with the real RFIDReader, but are not used here.
        """
        print(f"Mock RFID Reader initialized for port {serial_port}.")
        self._tags_to_read = []
        self._read_count = 0
        self.is_reading = threading.Event()

    def set_mock_data(self, tags):
        """
        Sets the tag data that the mock reader will return.
        :param tags: A list of lists of tuples, where each inner list represents one read cycle.
                     Example: [[('EPC1', 1, -50, time.time())], [('EPC2', 2, -60, time.time())]]
        """
        self._tags_to_read = tags
        self._read_count = 0

    def read_tags(self, timeout=1.0):
        """
        Simulates reading tags. Returns one batch of tags from the pre-set mock data per call.
        """
        self.is_reading.set()
        print(f"Mock reading tags (timeout: {timeout}s)...")
        time.sleep(0.1) # Simulate read delay
        if self._read_count < len(self._tags_to_read):
            tags_to_return = self._tags_to_read[self._read_count]
            # Update timestamp to be current
            tags_with_current_time = [(epc, ant, rssi, time.time()) for epc, ant, rssi, _ in tags_to_return]
            print(f"Mock reader returning: {tags_with_current_time}")
            self._read_count += 1
            self.is_reading.clear()
            return tags_with_current_time
        
        print("No more mock tags to return.")
        self.is_reading.clear()
        return []

    def close(self):
        """
        Simulates closing the connection.
        """
        print("Mock RFID Reader closed.")
        # In a real scenario, you might join a thread here.
        # For this mock, we just print a message.
        pass


if __name__ == '__main__':
    # --- Example for MockRFIDReader ---
    print("--- Running Mock RFID Reader Example ---")
    try:
        mock_reader = MockRFIDReader("mock_port")
        mock_tags_sequence = [
            [('EPC12345', 1, -50, 0)],
            [('EPC67890', 2, -65, 0), ('EPCABCDE', 1, -70, 0)],
            []
        ]
        mock_reader.set_mock_data(mock_tags_sequence)

        print("\nReading mock tags (call 1)...")
        tags = mock_reader.read_tags()
        print(f"Found tags: {tags}")
        assert len(tags) == 1

        print("\nReading mock tags (call 2)...")
        tags = mock_reader.read_tags()
        print(f"Found tags: {tags}")
        assert len(tags) == 2

        print("\nReading mock tags (call 3)...")
        tags = mock_reader.read_tags()
        print(f"Found tags: {tags}")
        assert len(tags) == 0

        print("\nReading mock tags (call 4 - should be empty again)...")
        tags = mock_reader.read_tags()
        print(f"Found tags: {tags}")
        assert len(tags) == 0

        mock_reader.close()
        print("--- Mock RFID Reader Example Finished ---")

    except Exception as e:
        print(f"Failed to run Mock RFID reader example: {e}")


    # --- Example for real RFIDReader ---
    print("\n--- Running Real RFID Reader Example ---")
    # This requires a real reader connected.
    # For testing without hardware, this block will fail.
    try:
        reader = RFIDReader("tmr:///dev/ttyUSB0") 
        print("Reading tags...")
        tags = reader.read_tags(timeout=2)
        if tags:
            for tag in tags:
                print(f"EPC: {tag[0]}, Antenna: {tag[1]}, RSSI: {tag[2]}, Timestamp: {tag[3]}")
        else:
            print("No tags found.")
        reader.close()
    except Exception as e:
        print(f"Failed to run real RFID reader example: {e}")
