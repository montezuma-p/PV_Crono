"""
Testes para o sistema de design moderno do AppCrono v14.0
"""

import pytest
from crono_app.design_system import COLORS, FONTS, FONT_SIZES, SPACING, BORDERS, get_theme_config


class TestDesignSystem:
    """Testa o sistema de design moderno."""

    def test_colors_structure(self):
        """Testa se a estrutura de cores está correta."""
        # Testa cores primárias
        assert "primary" in COLORS
        assert "blue" in COLORS["primary"]
        assert "green" in COLORS["primary"]
        assert "red" in COLORS["primary"]
        assert "gold" in COLORS["primary"]
        
        # Testa cores secundárias
        assert "secondary" in COLORS
        assert "gray" in COLORS["secondary"]
        assert "purple" in COLORS["secondary"]
        
        # Testa backgrounds
        assert "background" in COLORS
        assert "dark" in COLORS["background"]
        assert "light" in COLORS["background"]
        
        # Testa status
        assert "status" in COLORS
        assert "success" in COLORS["status"]
        assert "error" in COLORS["status"]

    def test_color_values_format(self):
        """Testa se as cores estão no formato hexadecimal correto."""
        # Testa algumas cores específicas
        assert COLORS["primary"]["blue"].startswith("#")
        assert len(COLORS["primary"]["blue"]) == 7
        assert COLORS["status"]["success"].startswith("#")
        assert len(COLORS["background"]["dark"]) == 7

    def test_fonts_structure(self):
        """Testa se a estrutura de fontes está correta."""
        assert "primary" in FONTS
        assert "mono" in FONTS
        assert "display" in FONTS
        
        # Testa se são tuplas de fontes
        assert isinstance(FONTS["primary"], tuple)
        assert isinstance(FONTS["mono"], tuple)
        assert isinstance(FONTS["display"], tuple)

    def test_font_sizes(self):
        """Testa se os tamanhos de fonte estão definidos."""
        required_sizes = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]
        
        for size in required_sizes:
            assert size in FONT_SIZES
            assert isinstance(FONT_SIZES[size], int)
            assert FONT_SIZES[size] > 0

    def test_spacing_values(self):
        """Testa se os espaçamentos estão definidos."""
        required_spacings = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl"]
        
        for spacing in required_spacings:
            assert spacing in SPACING
            assert isinstance(SPACING[spacing], int)
            assert SPACING[spacing] > 0

    def test_borders_structure(self):
        """Testa se a estrutura de bordas está correta."""
        assert "radius" in BORDERS
        assert "width" in BORDERS
        
        # Testa radius
        assert "sm" in BORDERS["radius"]
        assert "md" in BORDERS["radius"]
        assert "lg" in BORDERS["radius"]
        
        # Testa width
        assert "thin" in BORDERS["width"]
        assert "normal" in BORDERS["width"]
        assert "thick" in BORDERS["width"]

    def test_get_theme_config_dark(self):
        """Testa a configuração do tema escuro."""
        theme = get_theme_config("dark")
        
        required_keys = [
            "bg_primary", "bg_secondary", "text_primary", 
            "text_secondary", "accent", "success", "warning", "error"
        ]
        
        for key in required_keys:
            assert key in theme
            assert isinstance(theme[key], str)
            assert theme[key].startswith("#")

    def test_get_theme_config_light(self):
        """Testa a configuração do tema claro."""
        theme = get_theme_config("light")
        
        required_keys = [
            "bg_primary", "bg_secondary", "text_primary", 
            "text_secondary", "accent", "success", "warning", "error"
        ]
        
        for key in required_keys:
            assert key in theme
            assert isinstance(theme[key], str)
            assert theme[key].startswith("#")

    def test_theme_differences(self):
        """Testa se os temas dark e light são diferentes."""
        dark_theme = get_theme_config("dark")
        light_theme = get_theme_config("light")
        
        # Deve haver diferenças entre os temas
        assert dark_theme["bg_primary"] != light_theme["bg_primary"]
        assert dark_theme["text_primary"] != light_theme["text_primary"]

    def test_color_consistency(self):
        """Testa se as cores são consistentes entre diferentes contextos."""
        dark_theme = get_theme_config("dark")
        
        # Cores de status devem ser as mesmas
        assert dark_theme["success"] == COLORS["status"]["success"]
        assert dark_theme["error"] == COLORS["status"]["error"]

    def test_font_size_progression(self):
        """Testa se os tamanhos de fonte estão em progressão lógica."""
        sizes = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]
        
        for i in range(len(sizes) - 1):
            current_size = FONT_SIZES[sizes[i]]
            next_size = FONT_SIZES[sizes[i + 1]]
            assert current_size < next_size, f"{sizes[i]} deve ser menor que {sizes[i + 1]}"

    def test_spacing_progression(self):
        """Testa se os espaçamentos estão em progressão lógica."""
        spacings = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl"]
        
        for i in range(len(spacings) - 1):
            current_spacing = SPACING[spacings[i]]
            next_spacing = SPACING[spacings[i + 1]]
            assert current_spacing < next_spacing, f"{spacings[i]} deve ser menor que {spacings[i + 1]}"


class TestDesignSystemIntegration:
    """Testa a integração do design system com outros componentes."""

    def test_import_from_app(self):
        """Testa se o design system pode ser importado no app principal."""
        try:
            from crono_app.app import AppCrono
            from crono_app.design_system import get_theme_config
            
            # Testa se pode criar um tema
            theme = get_theme_config("dark")
            assert theme is not None
            
        except ImportError as e:
            pytest.fail(f"Falha ao importar design system no app: {e}")

    def test_modern_reports_integration(self):
        """Testa se o design system integra com modern_reports."""
        try:
            from crono_app.modern_reports import ModernReportGenerator
            from crono_app.design_system import COLORS, FONTS
            
            # Deve conseguir acessar as cores no gerador
            assert COLORS["primary"]["blue"] is not None
            assert FONTS["primary"] is not None
            
        except ImportError as e:
            pytest.fail(f"Falha ao integrar design system com relatórios: {e}")
