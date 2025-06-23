import sys
from unittest.mock import MagicMock
import pytest

# This code runs when conftest is imported by pytest, before test collection.

class MockWidget(MagicMock):
    """A versatile mock for any customtkinter widget."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add mocks for common widget methods
        self.grid = MagicMock()
        self.pack = MagicMock()
        self.place = MagicMock()
        self.configure = MagicMock()
        self.cget = MagicMock(return_value="some_value")
        self.bind = MagicMock()
        self.insert = MagicMock()
        self.see = MagicMock()
        self.get = MagicMock(return_value="")
        self.delete = MagicMock()

    def __call__(self, *args, **kwargs):
        # When a widget class is instantiated, return a new mock instance.
        return MockWidget()

class MockCTk:
    """
    A mock for the main CTk window class. It does NOT inherit from MagicMock
    to prevent the application class from becoming a mock itself.
    """
    _instantiation_mock = MagicMock()  # Track instantiations
    
    def __init__(self, *args, **kwargs):
        # Track that the class was instantiated
        self._instantiation_mock(*args, **kwargs)
        
        # Instead, it contains a MagicMock to track calls to its methods.
        self._mock = MagicMock()
        self.title = self._mock.title
        self.geometry = self._mock.geometry
        self.protocol = self._mock.protocol
        self.mainloop = self._mock.mainloop
        self.destroy = self._mock.destroy
        self.grid_rowconfigure = self._mock.grid_rowconfigure
        self.grid_columnconfigure = self._mock.grid_columnconfigure
        self.after = self._mock.after
    
    @classmethod
    def assert_called_once(cls):
        """Permite verificar se CTk foi instanciado uma vez."""
        cls._instantiation_mock.assert_called_once()
    
    @classmethod
    def reset_mock(cls):
        """Reseta o mock de instanciação."""
        cls._instantiation_mock.reset_mock()

# Create mock module replacements
mock_ctk_module = MagicMock()
mock_serial_module = MagicMock()

# Configure serial mock to have SerialException as a real exception class
class MockSerialException(Exception):
    pass

mock_serial_module.SerialException = MockSerialException
mock_serial_module.Serial = MagicMock()

# Patch sys.modules at import time
sys.modules['customtkinter'] = mock_ctk_module
sys.modules['serial'] = mock_serial_module
sys.modules['serial.tools'] = mock_serial_module.tools
sys.modules['serial.tools.list_ports'] = mock_serial_module.tools.list_ports

@pytest.fixture(autouse=True)
def reset_all_mocks():
    """
    A fixture to automatically reset all mocks before each test, ensuring
    test isolation.
    """
    mock_ctk_module.reset_mock()
    mock_serial_module.reset_mock()
    
    # Reset CTk instantiation mock
    MockCTk.reset_mock()
    
    # Re-initialize mocks that are functions/classes to reset their internal state
    mock_ctk_module.CTk = MockCTk
    mock_ctk_module.CTkFrame = MockWidget()
    mock_ctk_module.CTkLabel = MockWidget()
    mock_ctk_module.CTkButton = MockWidget()
    mock_ctk_module.CTkEntry = MockWidget()
    mock_ctk_module.CTkOptionMenu = MockWidget()
    mock_ctk_module.CTkTextbox = MockWidget()

    # Reset serial comports return value
    mock_serial_module.tools.list_ports.comports.return_value = [MagicMock(device="/dev/ttyUSB0")]

@pytest.fixture
def app():
    """
    Provides a fresh instance of the application for each test.
    The import is done inside the fixture to ensure mocks are in place.
    """
    # Add project root to path to allow importing rfid_bridge
    sys.path.insert(0, '/home/montezuma/AppCrono')
    from rfid_bridge.bridge import RFIDBridgeApp
    app_instance = RFIDBridgeApp()
    return app_instance
