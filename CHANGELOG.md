# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

## [0.1.0] - 2026-05-06

### Added
- ✅ Sistema inicial de reconhecimento facial com FastAPI
- ✅ Página de câmera com captura em tempo real
- ✅ Página de telão com exibição em grande escala
- ✅ Comunicação WebSocket para tempo real
- ✅ Síntese de fala em português (Web Speech API)
- ✅ Sistema de debounce para evitar anúncios repetidos
- ✅ Interface responsiva para desktop e mobile
- ✅ Histórico de alunos reconhecidos
- ✅ Suporte a Docker e docker-compose
- ✅ Documentação completa (README, INSTALL, CONTRIBUTING)
- ✅ Script de teste de configuração

### Features
- Reconhecimento facial usando face_recognition library
- Captura de frames via câmera do navegador
- WebSocket para comunicação em tempo real
- Tolerância configurável de reconhecimento
- Interface moderna e intuitiva
- Suporte multi-idioma (foco em português)

### Technical Details
- FastAPI backend
- Uvicorn ASGI server
- face_recognition + OpenCV
- Python 3.8+
- HTML5 + CSS3 + Vanilla JavaScript
- WebSocket para real-time updates

---

## Versões Futuras Planejadas

### v0.2.0
- [ ] Dashboard de administração
- [ ] Banco de dados para registrar attendance
- [ ] Autenticação para acesso às páginas
- [ ] Configuração via interface web
- [ ] Suporte para múltiplos eventos/turmas

### v0.3.0
- [ ] API REST para gerenciar alunos
- [ ] Export de relatórios (CSV, PDF)
- [ ] Notificações push
- [ ] Cache de imagens para melhor performance
- [ ] Análise de frequência

### v1.0.0
- [ ] Suporte a reconhecimento de expressões
- [ ] Integração com sistemas de gestão escolar
- [ ] Mobile app nativa
- [ ] Machine learning customizado
- [ ] Suporte a múltiplas câmeras

---

## Como Reportar Bugs

Se encontrar um bug, por favor:

1. Verifique se já foi reportado
2. Inclua:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Screenshots se aplicável
   - Informações do sistema (OS, navegador, versão Python)

## Como Sugerir Features

Sugestões são bem-vindas! Por favor:

1. Use um título descritivo
2. Forneça descrição detalhada
3. Liste exemplos de uso
4. Explique por que seria útil

---

## Notas de Versão

### v0.1.0 - Lançamento Inicial
Este é o lançamento inicial do sistema de reconhecimento facial para formatura SENAI.

**O que está incluído:**
- Sistema completo de reconhecimento facial
- Interface de câmera
- Interface de telão com áudio
- Documentação extensiva
- Suporte Docker

**Requisitos do Sistema:**
- Python 3.8+
- Navegador moderno (Chrome, Firefox, Safari, Edge)
- Webcam integrada ou USB
- Conexão com a mesma rede para múltiplos dispositivos

**Instalação:**
Veja [INSTALL.md](INSTALL.md) para instruções detalhadas.

**Conhecidas Limitações:**
- Requer boa iluminação para melhor reconhecimento
- Melhor performance com até 100 alunos cadastrados
- Web Speech API pode não suportar todos os idiomas em todos os navegadores

---

## Contribuições

Obrigado a todos que contribuíram para este projeto!

Para contribuir, veja [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Última atualização:** 2026-05-06
