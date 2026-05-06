# 🤝 Guia de Contribuição

Obrigado por querer contribuir! Aqui estão algumas diretrizes para manter o projeto bem organizado.

## Como Contribuir

### 1. Fork o repositório
```bash
git clone https://github.com/seu-usuario/reconhecimento_facial_formatura_senai.git
cd reconhecimento_facial_formatura_senai
```

### 2. Crie uma branch para sua feature
```bash
git checkout -b feature/sua-feature-aqui
```

### 3. Faça suas mudanças
- Siga o estilo de código existente
- Adicione testes se aplicável
- Atualize a documentação conforme necessário

### 4. Commit com mensagens descritivas
```bash
git commit -m "Adiciona descrição clara da mudança"
```

### 5. Push e crie um Pull Request
```bash
git push origin feature/sua-feature-aqui
```

## Diretrizes de Código

### Python
- Use snake_case para nomes de variáveis e funções
- Use UPPER_CASE para constantes
- Máximo 100 caracteres por linha
- Adicione type hints quando possível

```python
def recognize_face(image_data: bytes) -> str | None:
    """Identifica um rosto em uma imagem."""
    pass
```

### JavaScript/HTML/CSS
- Use camelCase para nomes de variáveis e funções
- Use kebab-case para classes CSS
- Máximo 100 caracteres por linha
- Documente funções complexas

```javascript
function displayStudent(nome) {
    // Implementação
}
```

## Tipos de Contribuição

### 🐛 Bug Fixes
- Descreva o problema claramente
- Forneça passos para reproduzir
- Inclua screenshots se relevante

### ✨ Novas Features
- Discuta a feature em uma issue primeiro
- Mantenha compatibilidade com código existente
- Adicione testes

### 📚 Documentação
- Melhore README ou guias existentes
- Corrija typos
- Adicione exemplos

### 🎨 Melhorias de UI/UX
- Explique a melhoria visual
- Forneça before/after screenshots
- Considere responsividade

## Checklist antes de submeter PR

- [ ] Código segue as diretrizes de estilo
- [ ] Testou as mudanças localmente
- [ ] Atualizou documentação relevante
- [ ] Não há conflitos com main branch
- [ ] Commits têm mensagens descritivas
- [ ] Sem arquivos de configuração pessoal (venv, .env, etc)

## Processo de Review

1. Seu PR será revisado
2. Podem haver solicitações de mudanças
3. Após aprovação, será feito merge

## Questões?

Abra uma issue no repositório para:
- Reportar bugs
- Sugerir features
- Fazer perguntas sobre o projeto

---

**Obrigado por contribuir! 🎉**
