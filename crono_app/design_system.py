"""
Sistema de Design Moderno para AppCrono
Cores, tipografia e estilos profissionais baseados em padrões internacionais
"""

# Paleta de Cores Profissional
COLORS = {
    # Cores Primárias
    "primary": {
        "blue": "#1E3A8A",      # Azul corporativo sólido
        "green": "#059669",     # Verde sucesso/confirmação
        "red": "#DC2626",       # Vermelho alertas/crítico
        "gold": "#F59E0B",      # Destaque/prêmios
    },
    
    # Cores Secundárias
    "secondary": {
        "gray": "#64748B",      # Texto secundário
        "purple": "#7C3AED",    # Funcionalidades especiais
        "teal": "#0D9488",      # Dados em tempo real
        "orange": "#EA580C",    # Avisos importantes
    },
    
    # Backgrounds
    "background": {
        "dark": "#0F172A",      # Fundo escuro premium
        "light": "#F8FAFC",     # Fundo claro clean
        "card": "#FFFFFF",      # Cards e componentes
        "modal": "#F1F5F9",     # Modais e overlays
    },
    
    # Estados
    "status": {
        "success": "#059669",
        "warning": "#D97706", 
        "error": "#DC2626",
        "info": "#2563EB",
        "live": "#EF4444",      # Status em tempo real
    },
    
    # Categorias por Gênero
    "categories": {
        "male": "#3B82F6",      # Azul para masculino
        "female": "#EC4899",    # Rosa para feminino
        "mixed": "#8B5CF6",     # Roxo para misto
    }
}

# Tipografia Moderna
FONTS = {
    "primary": ("Inter", "SF Pro Display", "system-ui", "sans-serif"),
    "mono": ("JetBrains Mono", "SF Mono", "Consolas", "monospace"),
    "display": ("Poppins", "Inter", "sans-serif"),
}

# Tamanhos de Fonte (em pixels)
FONT_SIZES = {
    "xs": 12,       # Labels pequenos
    "sm": 14,       # Texto secundário  
    "base": 16,     # Texto principal
    "lg": 18,       # Subtítulos
    "xl": 20,       # Títulos de seção
    "2xl": 24,      # Títulos principais
    "3xl": 30,      # Títulos grandes
    "4xl": 36,      # Cronômetros
    "5xl": 48,      # Display principal
}

# Espaçamentos (em pixels)
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "2xl": 48,
    "3xl": 64,
}

# Bordas e Sombras
BORDERS = {
    "radius": {
        "sm": 6,
        "md": 8, 
        "lg": 12,
        "xl": 16,
        "full": 9999,
    },
    "width": {
        "thin": 1,
        "normal": 2,
        "thick": 4,
    }
}

SHADOWS = {
    "sm": "0 1px 2px rgba(0,0,0,0.05)",
    "md": "0 4px 6px rgba(0,0,0,0.07)", 
    "lg": "0 10px 15px rgba(0,0,0,0.1)",
    "xl": "0 20px 25px rgba(0,0,0,0.1)",
}

# Função para configurar tema personalizado

def get_theme_config(mode="light"):
    """Retorna configuração de tema baseada no modo (apenas light)"""
    return {
        "bg_primary": COLORS["background"]["light"],
        "bg_secondary": COLORS["background"]["card"],
        "text_primary": "#1E293B",
        "text_secondary": COLORS["secondary"]["gray"],
        "accent": COLORS["primary"]["blue"],
        "success": COLORS["status"]["success"],
        "warning": COLORS["status"]["warning"],
        "error": COLORS["status"]["error"]
    }

# Ícones e Elementos Visuais
ICONS = {
    "athletes": {
        "male": "🏃‍♂️",
        "female": "🏃‍♀️", 
        "mixed": "🏃",
    },
    "medals": {
        "gold": "🥇",
        "silver": "🥈", 
        "bronze": "🥉",
    },
    "status": {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
        "live": "🔴",
        "processing": "⏳",
    },
    "actions": {
        "play": "▶️",
        "pause": "⏸️",
        "stop": "⏹️",
        "settings": "⚙️",
        "refresh": "🔄",
        "save": "💾",
        "print": "🖨️",
        "export": "📤",
    }
}

# Animações e Transições
ANIMATIONS = {
    "duration": {
        "fast": 150,        # ms
        "normal": 300,      # ms  
        "slow": 500,        # ms
    },
    "easing": {
        "ease_in": "ease-in",
        "ease_out": "ease-out", 
        "ease_in_out": "ease-in-out",
        "bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
    }
}

# Configurações de Layout
LAYOUT = {
    "container_max": "100vw",  # Largura máxima ajustada para ocupar toda a tela
    "sidebar_width": "20vw",  # Sidebar proporcional ao tamanho da tela
    "header_height": "10vh",  # Header proporcional ao tamanho da tela
    "card_min_height": "15vh",  # Altura mínima dos cards ajustada
}

# Z-index para layering
Z_INDEX = {
    "dropdown": 1000,
    "sticky": 1020,
    "fixed": 1030,
    "modal_backdrop": 1040,
    "modal": 1050,
    "popover": 1060,
    "tooltip": 1070,
}

def get_color(category: str, name: str) -> str:
    """Obtém uma cor do sistema de design"""
    return COLORS.get(category, {}).get(name, "#000000")

def get_font_size(size: str) -> int:
    """Obtém um tamanho de fonte"""
    return FONT_SIZES.get(size, 16)

def get_spacing(size: str) -> int:
    """Obtém um valor de espaçamento"""
    return SPACING.get(size, 16)

# Temas para diferentes modos
THEMES = {
    "light": {
        "bg_primary": COLORS["background"]["light"],
        "bg_secondary": COLORS["background"]["card"],
        "text_primary": "#1F2937",
        "text_secondary": COLORS["secondary"]["gray"],
        "border": "#E5E7EB",
    }
}

# Função para calcular tamanhos responsivos

def get_responsive_size(base_size: int, screen_dimension: str) -> str:
    """Retorna tamanho proporcional baseado na dimensão da tela."""
    return f"calc({base_size}px + {screen_dimension} * 0.01)"
