# PV Cronometragem (AppCrono v0.14-alpha)

**Software de cronometragem profissional para eventos esportivos de grande porte**

> ⚠️ **ATENÇÃO:** Este projeto está em desenvolvimento ativo (versão ALPHA). Não utilize em produção! Feedbacks e contribuições são bem-vindos.

## 🏃‍♂️ Visão Geral

O AppCrono v0.14-alpha é a primeira peça de um futuro ecossistema tecnológico completo para eventos esportivos. Desenvolvido em parceria por Montezuma (especialista em cronometragem) e IA Codex 2.0, oferece uma solução robusta, escalável e confiável para gerenciar eventos com dezenas de milhares de participantes.

### 🎉 Novidades da v0.14-alpha
- **Cobertura de testes excepcional**: 71% geral, 100% sucesso em 209 testes
- **Interface modernizada** com design system consistente
- **Arquitetura robusta** com tratamento avançado de exceções
- **Relatórios aprimorados** com exportação PDF otimizada

## 🏗️ Arquitetura

O sistema é dividido em duas aplicações especializadas:

- **`crono_app`**: Aplicação desktop principal para controle da cronometragem
- **`rfid_bridge`**: Bridge dedicada para leitura de tags RFID

## 🚀 Funcionalidades

- ✅ Gestão completa de atletas
- ✅ Cronometragem em tempo real
- ✅ Integração com leitores RFID
- ✅ Geração de relatórios PDF
- ✅ Interface moderna com CustomTkinter
- ✅ Base de dados SQLite robusta
- ✅ Arquitetura preparada para alta escala

## 📋 Pré-requisitos

- Python 3.12+
- Sistema operacional: Windows, Linux ou macOS
- **Para WSL**: X11 server (VcXsrv, Xming ou WSLg) para interface gráfica

## 🛠️ Instalação

### Instalação Padrão (Linux/Mac/Windows)

1. Clone o repositório:
```bash
git clone <repository-url>
cd AppCrono
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### 🐧 Instalação WSL (Ubuntu)

**Pré-requisitos WSL:**
```bash
# Instalar X11 apps
sudo apt update
sudo apt install x11-apps

# Configurar DISPLAY
export DISPLAY=:0.0
```

**Configuração:**
```bash
cd /home/[seu-usuario]/AppCrono
source venv/bin/activate
pip install -r requirements.txt
```

**Validar ambiente:**
```bash
# Testar X11
xclock &
sleep 2 && pkill xclock

# Testar imports
python -c "import tkinter; import customtkinter; print('GUI OK')"
python -c "import crono_app; print('AppCrono OK')"
```

## 🎯 Execução

### Aplicação Principal
```bash
# Ativar venv (sempre necessário)
source venv/bin/activate

# Executar AppCrono v0.14-alpha
python -m crono_app.app
```

### Bridge RFID
```bash
# Em terminal separado, com venv ativa
python -m rfid_bridge.bridge
```

### 🐧 WSL - Troubleshooting Interface Gráfica

Se a interface não aparecer no WSL:

1. **Verificar X11:**
   ```bash
   echo $DISPLAY  # deve retornar :0.0 ou similar
   xclock &       # teste rápido
   ```

2. **Instalar X server no Windows:**
   - VcXsrv (gratuito)
   - X410 (Microsoft Store)
   - WSLg (Windows 11 22H2+)

3. **Configurar firewall Windows** para permitir X11

## 🧪 Testes

O AppCrono v0.14-alpha possui uma suíte de testes excepcional com **71% de cobertura geral**.

### Executar Testes
```bash
# Ativar venv
source venv/bin/activate

# Todos os testes
pytest

# Com relatório de cobertura
pytest --cov=crono_app --cov=rfid_bridge --cov-report=term-missing

# Teste específico
pytest tests/test_app.py -v
```

### 📊 Estatísticas de Testes (v0.14-alpha)
- **209 testes** implementados
- **100% taxa de sucesso**
- **71% cobertura geral** do código
- **8 de 9 módulos** com cobertura > 60%

## 📁 Estrutura do Projeto

```
AppCrono/
├── crono_app/           # Aplicação principal
├── rfid_bridge/         # Bridge RFID
├── tests/               # Testes automatizados
├── docs/                # Documentação
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

## 🎯 Roadmap

### ✅ Conquistados na v0.14-alpha
- [x] Cobertura excepcional de testes (71%)
- [x] Design system modernizado
- [x] Arquitetura robusta com tratamento de exceções
- [x] Relatórios PDF aprimorados
- [x] Interface CustomTkinter otimizada

### 🚧 Próximos Passos (v0.15)
- [ ] Internacionalização (i18n) - PT/EN/ES
- [ ] CRUD de Categorias avançado
- [ ] Configurações de Evento personalizáveis
- [ ] Code Signing para distribuição
- [ ] Melhorias de UI/UX baseadas em feedback

### 🌟 Futuro (Módulo 2)
- [ ] Plataforma Web complementar
- [ ] API REST para integração
- [ ] Dashboard analítico

## 👥 Colaboração

Para contribuir com o projeto, consulte:
- [`docs/GUIA_DE_COLABORACAO.md`](docs/GUIA_DE_COLABORACAO.md)
- [`docs/TASKS.md`](docs/TASKS.md)

## 📄 Licença

Projeto proprietário desenvolvido por PV Cronometragem.

---

**Construindo o futuro da cronometragem esportiva** 🏆
