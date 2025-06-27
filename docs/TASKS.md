# Roadmap – PV Crono

Este arquivo apresenta o roadmap sequencial do projeto. Ao concluir uma tarefa, marque como concluída (~~riscada~~) e mova o registro detalhado para o `DIARIO_DE_BORDO.md`.

## 1. Fundação e Arquitetura
- [ ] Revisar e modularizar arquitetura para facilitar integração futura
- [ ] Code Signing para distribuição

## 2. Prototipagem e Migração de Interface
- [ ] Prototipar tela principal na nova stack
- [ ] Planejar migração incremental dos módulos de UI
- [ ] Melhorias de UI/UX baseadas em feedback
- [ ] Atualizar documentação e normas técnicas para refletir a nova visão

### Checklist de Migração para Flutter Desktop
- [ ] ~~Instalar Flutter SDK e configurar ambiente desktop no WSL (com X11)~~
    - Em 27/06/2025, o Flutter SDK foi instalado e testado com sucesso no WSL/Linux, validando o potencial visual e responsivo do Flutter Desktop. O setup no Windows será realizado posteriormente.
- [ ] Rodar app de exemplo Flutter Desktop em ambos ambientes para validar setup
- [ ] ~~Criar repositório/projeto inicial Flutter Desktop~~ <!-- O repositório público já existe para este workspace. Decisão: manter monorepo (backend Python + frontend Flutter juntos). -->
- [ ] Prototipar tela principal do PV Crono em Flutter
- [ ] ~~Definir stack de interface alvo (Qt, Flutter, etc)~~ <!-- Decisão: Flutter Desktop concluída e registrada. Veja detalhes no Diário de Bordo. -->
- [ ] Integrar módulos de lógica já existentes (Python) via API/local bridge
- [ ] Testar performance e responsividade em diferentes sistemas (Linux/WSL e Windows)
- [ ] Documentar aprendizados e desafios no Diário de Bordo

## 3. Core de Cronometragem e Precisão
- [ ] Implementar feature de precisão (sincronização de tempo, testes de latência)
- [ ] CRUD de Categorias avançado
- [ ] Configurações de Evento personalizáveis

## 4. Funcionalidades Avançadas
- [ ] Adicionar feature de resultados em tempo real
- [ ] Internacionalização (i18n) - PT/EN/ES
- [ ] API REST para integração
- [ ] Plataforma Web complementar (Módulo 2)
- [ ] Dashboard analítico

## 5. Expansão e Integração
- [ ] Sistema de inscrição online
- [ ] Portal de resultados web
- [ ] Live tracking em tempo real
- [ ] App mobile dedicado
- [ ] Analytics avançados e relatórios interativos
- [ ] Multi-tenancy e white-label
- [ ] Cloud deployment e escalabilidade
