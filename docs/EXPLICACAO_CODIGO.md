# Explicação das Partes do Código – PV Crono

Este documento explica a função de cada parte principal do código do projeto PV Crono, facilitando o entendimento para novos colaboradores e para consulta futura.

## Estrutura Geral
- **crono_app/**: Aplicação principal (UI, lógica de negócio, integração com banco de dados e relatórios)
- **rfid_bridge/**: Módulo de integração com hardware RFID (leitura de tags, comunicação via socket)
- **tests/**: Testes automatizados de todos os módulos
- **docs/**: Documentação do projeto

## crono_app/
- **app.py**: Interface gráfica principal, controle de fluxo da aplicação, integração com módulos de lógica, banco e relatórios.
- **business_logic.py**: Lógica de negócio central (regras de cronometragem, validações, manipulação de dados de atletas e eventos).
- **custom_exceptions.py**: Definição de exceções customizadas para tratamento de erros específicos do domínio.
- **database_manager.py**: Gerenciamento do banco de dados SQLite (CRUD de atletas, eventos, categorias, persistência de estados).
- **design_system.py**: Definição de temas, cores, tipografia e componentes visuais reutilizáveis.
- **modern_reports.py**: Geração de relatórios PDF e exportação de resultados.
- **ui_states.py**: Gerenciamento dos estados da interface (ex: telas, modos, feedback visual).
- **utils.py**: Funções utilitárias e helpers gerais.

## rfid_bridge/
- **bridge.py**: Gerencia a comunicação entre o app principal e o hardware RFID via socket.
- **rfid_reader.py**: Implementa a leitura de tags RFID, simulação e integração com hardware real.

## tests/
- **test_*.py**: Testes unitários e de integração para cada módulo do projeto.
- **conftest.py**: Fixtures e configurações globais para os testes.

## docs/
- Documentação detalhada do projeto, normas, histórico, visão e tarefas.

> Para detalhes de implementação, consulte os próprios arquivos fonte e a documentação técnica.
