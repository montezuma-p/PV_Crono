# PV Cronometragem (PV Crono)

**Software de cronometragem profissional para eventos esportivos de grande porte**

> ⚠️ **ATENÇÃO:** Este projeto está em desenvolvimento ativo (versão ALPHA). Não utilize em produção! Feedbacks e contribuições são bem-vindos.

---

## 🌟 Destaques do Projeto

- **Uso Prático:** Gerencia eventos esportivos reais, com suporte a milhares de participantes.
- **Objetivo Educacional:** Estudo de caso para aprendizado em Python, arquitetura de software e integração de tecnologias modernas.
- **Parceria com IA:** Desenvolvido em colaboração com IA (Codex 2.0).
- **Documentação Centralizada:** Toda a evolução registrada na pasta `docs/`.
- **Portfólio Profissional:** Demonstra habilidades técnicas e organização de projeto.

---

## 🏃‍♂️ Visão Geral e Roadmap

O PV Crono é a base de um futuro ecossistema completo para eventos esportivos. O projeto está em transição para uma stack de interface premium (Qt, Flutter ou similar) e segue um roadmap sequencial:

### Roadmap Atual
1. **Fundação e Arquitetura**
   - Definir stack de interface alvo (Qt, Flutter, etc)
   - Revisar e modularizar arquitetura
   - Code Signing para distribuição
2. **Prototipagem e Migração de Interface**
   - Prototipar tela principal na nova stack
   - Migração incremental dos módulos de UI
   - Melhorias de UI/UX baseadas em feedback
   - Atualizar documentação e normas técnicas
3. **Core de Cronometragem e Precisão**
   - Implementar feature de precisão (sincronização de tempo, testes de latência)
   - CRUD de Categorias avançado
   - Configurações de Evento personalizáveis
4. **Funcionalidades Avançadas**
   - Resultados em tempo real
   - Internacionalização (i18n)
   - API REST para integração
   - Plataforma Web complementar
   - Dashboard analítico

> Veja o arquivo [`TASKS.md`](./docs/TASKS.md) para o roadmap detalhado e atualizado.

---

## 🚀 Funcionalidades

- ✅ Gestão completa de atletas
- ✅ Cronometragem em tempo real
- ✅ Integração com leitores RFID
- ✅ Geração de relatórios PDF
- ✅ Interface com CustomTkinter
- ✅ Base de dados SQLite robusta

---

## 📋 Pré-requisitos

- Python 3.12+
- Windows, Linux ou macOS
- **Para WSL:** X11 server (VcXsrv, Xming ou WSLg) para interface gráfica

---

## 🛠️ Instalação

1. Clone o repositório:
   ```bash
   git clone <repository-url>
   cd PV_Crono
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

---

## 🎯 Execução

### Aplicação Principal
```bash
source venv/bin/activate
python -m crono_app.app
```

### Bridge RFID
```bash
python -m rfid_bridge.bridge
```

---

## 🧪 Testes e Qualidade

O projeto possui uma suíte de testes robusta (71% de cobertura geral). Em breve, contará com testes automáticos (CI/CD) via GitHub Actions.

```bash
source venv/bin/activate
pytest
pytest --cov=crono_app --cov=rfid_bridge --cov-report=term-missing
```

---

## 📁 Estrutura do Projeto

```
PV_Crono/
├── crono_app/           # Aplicação principal
├── rfid_bridge/         # Bridge RFID
├── tests/               # Testes automatizados
├── docs/                # Documentação
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

---

## 📚 Documentação e Colaboração

- [Visão e status do projeto](./docs/PROJECT_OVERVIEW.md)
- [Roadmap detalhado](./docs/TASKS.md)
- [Histórico e aprendizados](./docs/DIARIO_DE_BORDO.md)
- [Guia de colaboração](./docs/GUIA_DE_COLABORACAO.md)
- [Explicação do código](./docs/EXPLICACAO_CODIGO.md)

**Como contribuir:**
- Leia o `GUIA_DE_COLABORACAO.md`.
- Sugira melhorias, reporte bugs ou envie Pull Requests.
- Feedbacks e dúvidas são bem-vindos!

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

