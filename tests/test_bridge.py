import pytest
from unittest.mock import Mock, patch, MagicMock
import socket
import threading


class TestRFIDBridgeAppInit:
    """Testa a inicialização da aplicação RFIDBridgeApp."""

    def test_app_initialization(self, app):
        """Testa a inicialização da UI e dos componentes."""
        # Verifica se os componentes foram criados
        assert hasattr(app, 'serial_port_entry')
        assert hasattr(app, 'ip_entry')
        assert hasattr(app, 'port_entry')
        assert hasattr(app, 'toggle_button')
        assert hasattr(app, 'status_label')
        assert hasattr(app, 'log_textbox')
        assert hasattr(app, 'antenna_counters')
        
        # Verifica estado inicial
        assert app.server is None
        assert app.server_thread is None
        assert app.reader_thread is None
        assert app.is_running is False
        assert app.rfid_reader is None
        assert app.clients == []


class TestRFIDBridgeAppLogging:
    """Testa a funcionalidade de logging da aplicação."""

    def test_log_message(self, app):
        """Testa se as mensagens são logadas corretamente na UI."""
        log_textbox = app.log_textbox
        test_message = "Teste de mensagem de log"
        
        app.log(test_message)
        
        # Verifica se o textbox foi configurado para receber texto
        log_textbox.configure.assert_called()
        log_textbox.insert.assert_called()
        log_textbox.see.assert_called_with("end")


class TestServerToggle:
    """Testa a funcionalidade de toggle do servidor."""

    @patch('rfid_bridge.bridge.RFIDBridgeApp.start_server')
    def test_toggle_server_starts_when_not_running(self, mock_start_server, app):
        """Testa se toggle_server inicia o servidor quando ele não está rodando."""
        app.is_running = False
        app.toggle_server()
        mock_start_server.assert_called_once()

    @patch('rfid_bridge.bridge.RFIDBridgeApp.stop_server')
    def test_toggle_server_stops_when_running(self, mock_stop_server, app):
        """Testa se toggle_server para o servidor quando ele está rodando."""
        app.is_running = True
        app.toggle_server()
        mock_stop_server.assert_called_once()


class TestServerStart:
    """Testa a funcionalidade de início do servidor."""

    @patch('rfid_bridge.bridge.RFIDReader')
    @patch('socket.socket')
    def test_start_server_success(self, mock_socket, mock_rfid_reader, app):
        """Testa o início do servidor com sucesso."""
        app.serial_port_entry.get.return_value = "/dev/ttyUSB0"
        app.ip_entry.get.return_value = "0.0.0.0"
        app.port_entry.get.return_value = "9999"
        
        app.start_server()
        
        # Verifica se o leitor RFID foi criado e iniciado
        mock_rfid_reader.assert_called_once_with("/dev/ttyUSB0")
        app.rfid_reader.start.assert_called_once()
        
        # Verifica se o socket foi criado e configurado
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        app.server.bind.assert_called_once_with(("0.0.0.0", 9999))
        app.server.listen.assert_called_once_with(5)
        
        # Verifica se o estado foi atualizado
        assert app.is_running is True

    def test_start_server_no_serial_port(self, app):
        """Testa a falha ao iniciar o servidor sem porta serial selecionada."""
        app.serial_port_entry.get.return_value = ""
        app.ip_entry.get.return_value = "0.0.0.0"
        app.port_entry.get.return_value = "9999"
        
        app.start_server()
        
        # Verifica se o estado permanece falso
        assert app.is_running is False

    @patch('socket.socket')
    def test_start_server_socket_error(self, mock_socket, app):
        """Testa a falha ao iniciar o servidor devido a um erro de socket."""
        app.serial_port_entry.get.return_value = "/dev/ttyUSB0"
        app.ip_entry.get.return_value = "0.0.0.0"
        app.port_entry.get.return_value = "9999"
        
        # Simula erro no socket
        mock_socket.side_effect = Exception("Erro de socket")
        
        app.start_server()
        
        # Verifica se o estado permanece falso
        assert app.is_running is False


class TestServerStop:
    """Testa a funcionalidade de parada do servidor."""

    def test_stop_server_when_running(self, app):
        """Testa a parada do servidor quando ele está rodando."""
        # Simula um servidor em execução
        app.is_running = True
        app.rfid_reader = MagicMock()
        app.server = MagicMock()
        app.clients = [MagicMock(), MagicMock()]
        
        app.stop_server()
        
        # Verifica se o leitor foi parado
        app.rfid_reader.stop.assert_called_once()
        
        # Verifica se o socket foi fechado
        app.server.close.assert_called_once()
        
        # Verifica se os clientes foram fechados
        for client in app.clients:
            client.close.assert_called_once()
        
        # Verifica se o estado foi atualizado
        assert app.is_running is False


class TestAppClosing:
    """Testa a funcionalidade de fechamento da aplicação."""

    @patch('rfid_bridge.bridge.RFIDBridgeApp.stop_server')
    def test_on_closing_stops_server(self, mock_stop_server, app):
        """Testa se on_closing para o servidor antes de fechar."""
        app.is_running = True
        app.on_closing()
        mock_stop_server.assert_called_once()

    def test_on_closing_destroys_window_if_server_not_running(self, app):
        """Testa se on_closing destrói a janela quando o servidor não está rodando."""
        app.is_running = False
        app.on_closing()
        app.destroy.assert_called_once()


class TestHelperMethods:
    """Testa métodos auxiliares da aplicação."""

    def test_update_antenna_count(self, app):
        """Testa a atualização do contador de antenas."""
        # Mock do contador da antena 1
        app.antenna_counters[1] = MagicMock()
        app.antenna_counters[1].cget.return_value = "5"
        
        app.update_antenna_count(1)
        
        # Verifica se o contador foi atualizado
        app.antenna_counters[1].configure.assert_called_with(text="6")

    def test_broadcast_message(self, app):
        """Testa o envio de mensagem para todos os clientes."""
        # Cria clientes mock
        client1 = MagicMock()
        client2 = MagicMock()
        app.clients = [client1, client2]
        
        test_message = "test_message"
        app.broadcast(test_message)
        
        # Verifica se a mensagem foi enviada para todos os clientes
        client1.sendall.assert_called_once_with(test_message.encode('utf-8'))
        client2.sendall.assert_called_once_with(test_message.encode('utf-8'))

    def test_broadcast_removes_disconnected_client(self, app):
        """Testa se clientes desconectados são removidos da lista."""
        # Cria cliente que vai falhar
        client_fail = MagicMock()
        client_fail.sendall.side_effect = socket.error("Connection lost")
        client_ok = MagicMock()
        
        app.clients = [client_fail, client_ok]
        
        test_message = "test_message"
        app.broadcast(test_message)
        
        # Verifica se o cliente com falha foi removido
        assert client_fail not in app.clients
        assert client_ok in app.clients
        client_fail.close.assert_called_once()
