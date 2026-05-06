# Estrutura de Fotos dos Alunos

O sistema agora suporta múltiplas fotos por aluno para melhorar a precisão do reconhecimento facial.

## Organização das Pastas

Você pode organizar as fotos de duas formas:

### Opção 1: Usando Subpastas (Recomendado)

Crie uma pasta para cada aluno dentro de `alunos_cadastrados/`:

```
alunos_cadastrados/
├── João Silva/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   ├── foto3.jpg
│   └── foto4.jpg
├── Maria Santos/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── foto3.jpg
├── Pedro Oliveira/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   ├── foto3.jpg
│   ├── foto4.jpg
│   └── foto5.jpg
└── Ana Costa/
    ├── foto1.jpg
    └── foto2.jpg
```

O nome da pasta **DEVE** ser exatamente o nome do aluno que será exibido no telão.

### Opção 2: Imagens Diretas na Pasta

Se preferir, você pode colocar as imagens diretamente em `alunos_cadastrados/`:

```
alunos_cadastrados/
├── João Silva.jpg
├── Maria Santos.jpg
├── Pedro Oliveira.png
└── Ana Costa.jpeg
```

O nome do arquivo (sem extensão) será usado como o nome do aluno.

## Formatos Suportados

- `.jpg`
- `.jpeg`
- `.png`

## Dicas para Melhores Resultados

### Quantidade de Fotos

- **Mínimo:** 1 foto por aluno
- **Recomendado:** 3-5 fotos por aluno
- **Ideal:** 5-10 fotos em diferentes ângulos e condições de iluminação

### Qualidade das Fotos

- Luz clara e bem distribuída
- Rosto ocupa cerca de 30-50% da imagem
- Rosto frontal ou com ângulo leve
- Sem óculos de sol ou chapéus
- Sem movimentação (foto nítida)

### Ângulos Diferentes

Para cada aluno, tente tirar fotos em:

1. Frontal direto
2. Ligeiramente para a esquerda (20-30 graus)
3. Ligeiramente para a direita (20-30 graus)
4. Com iluminação de frente
5. Com iluminação lateral

### Evite

- Fotos muito pequenas do rosto
- Fotos com muita sombra no rosto
- Fotos de lado ou de costas
- Fotos borradas ou com pouca qualidade
- Imagens muito antigas (mudanças de aparência)

## Recarregar Fotos

As fotos são carregadas quando o servidor inicia. Se adicionar ou modificar fotos:

1. Pare o servidor (Ctrl+C)
2. Adicione/modifique as fotos
3. Inicie o servidor novamente (`python main.py`)

As fotos serão recarregadas automaticamente.

## Exemplo Prático

```bash
# Criar pastas para os alunos
mkdir "alunos_cadastrados/João Silva"
mkdir "alunos_cadastrados/Maria Santos"
mkdir "alunos_cadastrados/Pedro Oliveira"

# Copiar fotos (exemplo)
cp fotos/joao_1.jpg "alunos_cadastrados/João Silva/foto1.jpg"
cp fotos/joao_2.jpg "alunos_cadastrados/João Silva/foto2.jpg"
cp fotos/joao_3.jpg "alunos_cadastrados/João Silva/foto3.jpg"

cp fotos/maria_1.jpg "alunos_cadastrados/Maria Santos/foto1.jpg"
cp fotos/maria_2.jpg "alunos_cadastrados/Maria Santos/foto2.jpg"
```

## Duvidas Frequentes

### P: Qual é o nome exato que devo usar?
R: O nome da pasta ou arquivo (sem extensão) será exibido exatamente como digitado no telão. Use o nome completo do aluno.

### P: Preciso de muitas fotos?
R: Não obrigatoriamente. 1 foto funciona, mas 3-5 fotos melhoram bastante a precisão.

### P: Posso misturar as duas formas?
R: O sistema detectará automaticamente. Se houver subpastas, ele usará aquelas. Se não, usará as imagens diretas.

### P: Como adicionao novas fotos sem reiniciar?
R: No momento, é necessário reiniciar o servidor. No futuro, teremos um endpoint para recarregar.

### P: Que tamanho as imagens devem ter?
R: Qualquer tamanho funciona, mas recomenda-se imagens de 640x480 ou maiores.

## Performance

- 10 alunos x 5 fotos cada = ~50 comparações por frame
- Tempo de carregamento: ~2-5 segundos
- Tempo de reconhecimento: ~100-200ms por frame

Se tiver muitos alunos (100+), considere reduzir o número de fotos por aluno para manter performance.
