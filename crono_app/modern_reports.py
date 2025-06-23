"""
Gerador de Relatórios Modernos para AppCrono
Sistema premium de relatórios PDF com design internacional
"""

from datetime import datetime, date
import os
from typing import List, Dict, Any
from .design_system import COLORS, FONTS, FONT_SIZES, SPACING

class ModernReportGenerator:
    """Gerador de relatórios PDF com design moderno e profissional"""
    
    def __init__(self):
        self.setup_fonts()
    
    def setup_fonts(self):
        """Configura fontes para relatórios"""
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.fonts import addMapping
            
            # Registra fontes modernas se disponíveis
            self.primary_font = "Helvetica"
            self.mono_font = "Courier"
            self.bold_font = "Helvetica-Bold"
            
        except ImportError:
            print("ReportLab não encontrado. Instale com: pip install reportlab")
            self.primary_font = "Helvetica"
            self.mono_font = "Courier" 
            self.bold_font = "Helvetica-Bold"
    
    def generate_results_report(self, evento_data: Dict, resultados: List[Dict], output_path: str = None) -> str:
        """
        Gera relatório premium de resultados da corrida
        
        Args:
            evento_data: Dados do evento (nome, data, local, etc.)
            resultados: Lista de resultados dos atletas
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch, mm
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.lib import colors
            
            # Define arquivo de saída
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"relatorio_resultados_{timestamp}.pdf"
            
            # Configurações da página
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   rightMargin=20*mm, leftMargin=20*mm,
                                   topMargin=25*mm, bottomMargin=25*mm)
            
            # Estilos modernos
            styles = self._create_modern_styles()
            story = []
            
            # Cabeçalho premium
            story.extend(self._create_header(evento_data, styles))
            story.append(Spacer(1, 20))
            
            # Informações do evento
            story.extend(self._create_event_info(evento_data, styles))
            story.append(Spacer(1, 15))
            
            # Estatísticas gerais
            story.extend(self._create_statistics_section(resultados, styles))
            story.append(Spacer(1, 20))
            
            # Tabela de resultados
            story.extend(self._create_results_table(resultados, styles))
            
            # Rodapé
            story.extend(self._create_footer(styles))
            
            # Gera o PDF
            doc.build(story, onFirstPage=self._add_page_decoration, 
                     onLaterPages=self._add_page_decoration)
            
            return output_path
            
        except ImportError as e:
            raise ImportError(f"Dependências do ReportLab não encontradas: {e}")
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {e}")
    
    def _create_modern_styles(self):
        """Cria estilos modernos para o relatório"""
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.lib.colors import HexColor
        
        styles = getSampleStyleSheet()
        
        # Título principal
        styles.add(ParagraphStyle(
            name='ModernTitle',
            parent=styles['Title'],
            fontName=self.bold_font,
            fontSize=24,
            textColor=HexColor(COLORS["primary"]["blue"]),
            alignment=TA_CENTER,
            spaceAfter=10,
            spaceBefore=0
        ))
        
        # Subtítulo
        styles.add(ParagraphStyle(
            name='ModernSubtitle',
            parent=styles['Normal'],
            fontName=self.primary_font,
            fontSize=14,
            textColor=HexColor(COLORS["secondary"]["gray"]),
            alignment=TA_CENTER,
            spaceAfter=15
        ))
        
        # Cabeçalho de seção
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontName=self.bold_font,
            fontSize=16,
            textColor=HexColor(COLORS["primary"]["blue"]),
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=15,
            borderWidth=2,
            borderColor=HexColor(COLORS["primary"]["gold"]),
            borderPadding=5
        ))
        
        # Texto normal moderno
        styles.add(ParagraphStyle(
            name='ModernNormal',
            parent=styles['Normal'],
            fontName=self.primary_font,
            fontSize=11,
            textColor=HexColor("#333333"),
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        # Estatísticas destacadas
        styles.add(ParagraphStyle(
            name='StatHighlight',
            parent=styles['Normal'],
            fontName=self.bold_font,
            fontSize=12,
            textColor=HexColor(COLORS["primary"]["green"]),
            alignment=TA_CENTER,
            spaceAfter=5
        ))
        
        return styles
    
    def _create_header(self, evento_data: Dict, styles) -> List:
        """Cria cabeçalho premium do relatório"""
        from reportlab.platypus import Paragraph, Table, TableStyle
        from reportlab.lib.colors import HexColor
        
        header_elements = []
        
        # Logo conceitual e título
        title_text = f"🏃‍♂️ {evento_data.get('nome', 'EVENTO DE CORRIDA')}"
        header_elements.append(Paragraph(title_text, styles['ModernTitle']))
        
        # Subtítulo com local e data
        subtitle = f"📍 {evento_data.get('local', 'Local não informado')} • 📅 {evento_data.get('data', date.today().strftime('%d/%m/%Y'))}"
        header_elements.append(Paragraph(subtitle, styles['ModernSubtitle']))
        
        # Linha divisória
        header_elements.append(Paragraph("<hr/>", styles['ModernNormal']))
        
        return header_elements
    
    def _create_event_info(self, evento_data: Dict, styles) -> List:
        """Cria seção de informações do evento"""
        from reportlab.platypus import Paragraph, Table, TableStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib import colors
        
        info_elements = []
        info_elements.append(Paragraph("📋 INFORMAÇÕES DO EVENTO", styles['SectionHeader']))
        
        # Tabela de informações
        info_data = [
            ["🚀 Horário de Largada:", evento_data.get('horario_largada', 'Não informado')],
            ["📏 Distância:", evento_data.get('distancia', 'Não informada')],
            ["👥 Total de Atletas:", str(evento_data.get('total_atletas', 0))],
            ["⏱️ Sistema:", "PV Cronometragem PRO v14.0"],
            ["🏆 Categorias:", evento_data.get('categorias', 'Geral')]
        ]
        
        info_table = Table(info_data, colWidths=[120, 300])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor(COLORS["background"]["modal"])),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor(COLORS["primary"]["blue"])),
            ('FONTNAME', (0, 0), (0, -1), self.bold_font),
            ('FONTNAME', (1, 0), (1, -1), self.primary_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor(COLORS["secondary"]["gray"])),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, HexColor("#F8FAFC")])
        ]))
        
        info_elements.append(info_table)
        return info_elements
    
    def _create_statistics_section(self, resultados: List[Dict], styles) -> List:
        """Cria seção de estatísticas da corrida"""
        from reportlab.platypus import Paragraph, Table, TableStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib import colors
        
        stats_elements = []
        stats_elements.append(Paragraph("📊 ESTATÍSTICAS DA CORRIDA", styles['SectionHeader']))
        
        if not resultados:
            stats_elements.append(Paragraph("Nenhum resultado disponível", styles['ModernNormal']))
            return stats_elements
        
        # Calcula estatísticas
        tempos = [r.get('tempo_segundos', 0) for r in resultados if r.get('tempo_segundos', 0) > 0]
        
        if tempos:
            tempo_medio = sum(tempos) / len(tempos)
            tempo_min = min(tempos)
            tempo_max = max(tempos)
            
            # Converte para formato legível
            def format_time(seconds):
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = seconds % 60
                return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
            
            stats_data = [
                ["🥇 Melhor Tempo:", format_time(tempo_min)],
                ["📊 Tempo Médio:", format_time(tempo_medio)],
                ["⏰ Maior Tempo:", format_time(tempo_max)],
                ["👥 Finalizaram:", f"{len(tempos)} atletas"]
            ]
        else:
            stats_data = [
                ["📝 Status:", "Corrida em andamento"],
                ["👥 Inscritos:", f"{len(resultados)} atletas"],
                ["⏱️ Cronometragem:", "Ativa"],
                ["📊 Resultados:", "Aguardando finalizações"]
            ]
        
        stats_table = Table(stats_data, colWidths=[150, 200])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor(COLORS["status"]["info"])),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), self.bold_font),
            ('FONTNAME', (1, 0), (1, -1), self.mono_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 5)
        ]))
        
        stats_elements.append(stats_table)
        return stats_elements
    
    def _create_results_table(self, resultados: List[Dict], styles) -> List:
        """Cria tabela moderna de resultados"""
        from reportlab.platypus import Paragraph, Table, TableStyle
        from reportlab.lib.colors import HexColor
        
        table_elements = []
        table_elements.append(Paragraph("🏆 RESULTADOS OFICIAIS", styles['SectionHeader']))
        
        if not resultados:
            table_elements.append(Paragraph("Nenhum resultado disponível", styles['ModernNormal']))
            return table_elements
        
        # Cabeçalho da tabela
        headers = ["Pos.", "Nº", "Nome", "Categoria", "Tempo"]
        table_data = [headers]
        
        # Ordena resultados por tempo
        resultados_ordenados = sorted(resultados, 
                                    key=lambda x: x.get('tempo_segundos', float('inf')))
        
        # Adiciona dados dos atletas
        for i, resultado in enumerate(resultados_ordenados[:50]):  # Limita a 50 primeiros
            pos = str(i + 1) if resultado.get('tempo_segundos', 0) > 0 else "-"
            numero = str(resultado.get('numero', ''))
            nome = resultado.get('nome', 'Nome não informado')[:25]  # Limita nome
            categoria = resultado.get('categoria', 'Geral')
            
            # Formato do tempo
            tempo_seg = resultado.get('tempo_segundos', 0)
            if tempo_seg > 0:
                hours = int(tempo_seg // 3600)
                minutes = int((tempo_seg % 3600) // 60)
                seconds = tempo_seg % 60
                tempo_str = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
            else:
                tempo_str = "DNS/DNF"
            
            table_data.append([pos, numero, nome, categoria, tempo_str])
        
        # Cria tabela com design moderno
        results_table = Table(table_data, colWidths=[40, 40, 180, 80, 80])
        
        # Estilo da tabela
        table_style = [
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLORS["primary"]["blue"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), self.bold_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), self.primary_font),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Posição
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Número
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Nome
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Categoria
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Tempo
            
            # Bordas e cores alternadas
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor(COLORS["secondary"]["gray"])),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]
        
        # Cores alternadas para as linhas
        for i in range(1, min(len(table_data), 51)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), HexColor("#F8FAFC")))
            
            # Destaque para top 3
            if i <= 3 and table_data[i][0] != "-":
                if i == 1:  # 1º lugar
                    table_style.append(('BACKGROUND', (0, i), (-1, i), HexColor(COLORS["primary"]["gold"])))
                    table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.white))
                elif i == 2:  # 2º lugar  
                    table_style.append(('BACKGROUND', (0, i), (-1, i), HexColor("#C0C0C0")))
                elif i == 3:  # 3º lugar
                    table_style.append(('BACKGROUND', (0, i), (-1, i), HexColor("#CD7F32")))
                    table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.white))
        
        results_table.setStyle(TableStyle(table_style))
        table_elements.append(results_table)
        
        # Nota de rodapé se há mais resultados
        if len(resultados) > 50:
            note = f"* Exibindo primeiros 50 resultados de {len(resultados)} atletas"
            table_elements.append(Paragraph(note, styles['ModernNormal']))
        
        return table_elements
    
    def _create_footer(self, styles) -> List:
        """Cria rodapé do relatório"""
        from reportlab.platypus import Paragraph, Spacer
        
        footer_elements = []
        footer_elements.append(Spacer(1, 30))
        
        # Informações do sistema
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        footer_text = f"""
        <para align="center">
        <font size="8" color="{COLORS['secondary']['gray']}">
        Relatório gerado pelo PV Cronometragem PRO v14.0<br/>
        Sistema Internacional de Cronometragem Esportiva<br/>
        Gerado em {timestamp}
        </font>
        </para>
        """
        footer_elements.append(Paragraph(footer_text, styles['ModernNormal']))
        
        return footer_elements
    
    def _add_page_decoration(self, canvas, doc):
        """Adiciona decoração às páginas do PDF"""
        from reportlab.lib.colors import HexColor
        
        # Linha decorativa no topo
        canvas.setStrokeColor(HexColor(COLORS["primary"]["blue"]))
        canvas.setLineWidth(3)
        canvas.line(doc.leftMargin, doc.height + doc.bottomMargin - 10,
                   doc.width + doc.leftMargin, doc.height + doc.bottomMargin - 10)
        
        # Número da página
        page_num = canvas.getPageNumber()
        canvas.setFont(self.primary_font, 8)
        canvas.setFillColor(HexColor(COLORS["secondary"]["gray"]))
        canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 15,
                              f"Página {page_num}")
