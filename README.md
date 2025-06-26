# PV Cronometragem (PV Crono v0.14-alpha)

**Software de cronometragem profissional para eventos esportivos de grande porte**

> ⚠️ **ATENÇÃO:** Este projeto está em desenvolvimento ativo (versão ALPHA). Não utilize em produção! Feedbacks e contribuições são bem-vindos.

---

## 🌟 Destaques do Projeto

- **Uso Prático:** Desenvolvido para gerenciar eventos esportivos reais, com suporte a milhares de participantes.
- **Objetivo Educacional:** Criado como um estudo de caso para aprendizado em Python, arquitetura de software e integração de tecnologias modernas.
- **Parceria com IA:** Desenvolvido em colaboração com IA (Codex 2.0), explorando novas fronteiras de produtividade e inovação.
- **Documentação Centralizada:** Integração de memória persistente com a pasta `docs/` para histórico e evolução do projeto.
- **Portfólio Profissional:** Estruturado para demonstrar habilidades técnicas e conquistar oportunidades no mercado de trabalho.

---

## 🏃‍♂️ Visão Geral

O PV Crono v0.14-alpha é a primeira peça de um futuro ecossistema tecnológico completo para eventos esportivos. Ele combina uma interface moderna, arquitetura robusta e funcionalidades avançadas para oferecer uma solução confiável e escalável.

### 🎉 Novidades da v0.14-alpha
- **Cobertura de testes excepcional:** 71% geral, 100% sucesso em 209 testes
- **Interface modernizada** com design system consistente
- **Arquitetura robusta** com tratamento avançado de exceções
- **Relatórios aprimorados** com exportação PDF otimizada

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
- Sistema operacional: Windows, Linux ou macOS
- **Para WSL:** X11 server (VcXsrv, Xming ou WSLg) para interface gráfica

---

## 🛠️ Instalação

### Instalação Padrão (Linux/Mac/Windows)

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
# Ativar venv (sempre necessário)
source venv/bin/activate

# Executar PV Crono v0.14-alpha
python -m crono_app.app
```

### Bridge RFID
```bash
# Em terminal separado, com venv ativa
python -m rfid_bridge.bridge
```

---

## 🧪 Testes

O PV Crono v0.14-alpha possui uma suíte de testes robusta com **71% de cobertura geral**.

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

> ⚠️ **AVISO IMPORTANTE:**
> A interface de gerenciamento de categorias (CRUD via modal) foi adicionada na versão atual, mas ainda NÃO está coberta por testes automatizados (pytest). Use com cautela e reporte qualquer problema.

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

---

