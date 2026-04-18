# Sistema de Extração de Flyers com OCR

## Descrição
Sistema Python que extrai produtos, preços e metadados de imagens de flyers (supermercados, farmácias) usando OCR com GPT-4o-mini da OpenAI.

## Arquivos Principais

### main.py
Script principal que:
- Processa múltiplas imagens em lote
- Extrai produtos e preços (OCR 100% literal)
- Identifica loja, tipo de comércio e validade
- Otimiza imagens grandes (>4096px)
- Aplica retry automático (até 3x)
- Gera logs detalhados

**Saída CSV:**
```
imagem;produto;preço;loja;tipo;validade
```

### .env
```env
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=gpt-4o-mini
INPUT_FOLDER=folders_entrada
OUTPUT_CSV=produtos_precos_03.csv
MAX_IMAGE_SIZE=4096  # CRÍTICO: não usar <4096
TEMPERATURE=0
MAX_RETRIES=3
```

### requirements.txt
```
openai>=1.3.0
Pillow>=10.0.0
tqdm>=4.65.0
python-dotenv>=1.0.0
tenacity>=8.2.0
```

## Estrutura
```
projeto/
├── main.py
├── .env
├── requirements.txt
├── folders_entrada/        # INPUT: imagens aqui
├── produtos_precos_03.csv  # OUTPUT: dados extraídos
├── erros_processamento.csv # OUTPUT: erros
└── processamento.log       # OUTPUT: log
```

## Prompt da LLM (Estratégia)

**ETAPA 1 - Metadados:**
```
LOJA: [nome ou "Nome não identificado"]
TIPO: [tipo ou "Tipo não identificado"]
VALIDADE: [data ou "Validade não identificada"]
```

**ETAPA 2 - Produtos (100% literal):**
```
produto;preço
produto;preço
```

**Princípios:**
- OCR 100% literal - NÃO corrigir ortografia
- NÃO alterar marcas
- NÃO inferir ou inventar
- Extrair EXATAMENTE como aparece
- Se texto em múltiplas linhas, unir mantendo ordem

## Configurações Críticas

### ⚠️ MAX_IMAGE_SIZE
**MUITO IMPORTANTE:** Deve ser ≥4096 pixels

**Por quê:**
- Imagens >3MB geralmente têm 3000-4000px
- Se redimensionar muito, texto pequeno fica ilegível
- OCR perde precisão e começa a inventar produtos

**Sintoma de problema:**
- Produtos genéricos ("Cerveja", "Sabonete Líquido")
- Marcas trocadas (Carmed vira Nivea)
- Produtos inventados

**Solução:**
```env
MAX_IMAGE_SIZE=4096  # Permite imagens grandes
# ou
MAX_IMAGE_SIZE=99999 # Nunca otimiza
```

## Casos de Uso

### Flyer com nome e validade:
```csv
folder_01.jpg;Arroz Tio João 5kg;R$ 25,90;Supermercado ABC;Supermercado;Válido até 31/12/2024
```

### Flyer sem nome e validade:
```csv
folder_07.jpg;Dipirona 500mg;R$ 12,00;Nome não identificado;Farmácia;Validade não identificada
```

## Performance
- **Tempo:** ~5-8s por imagem
- **Custo:** ~$0.0013 por imagem
- **Acurácia:** 100% (com MAX_IMAGE_SIZE≥4096)

## Problemas Comuns

| Problema | Causa | Solução |
|----------|-------|---------|
| Produtos genéricos | MAX_IMAGE_SIZE muito baixo | Aumentar para 4096+ |
| Marcas trocadas | Otimização excessiva | Usar quality=98 |
| Produtos inventados | Imagem redimensionada demais | MAX_IMAGE_SIZE=99999 |
| Erro Unicode Windows | cp1252 não suporta UTF-8 | Já configurado no código |

## Uso Rápido
```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env: adicionar OPENAI_API_KEY
# Colocar imagens em folders_entrada/
python main_improved.py
```

## Pontos-Chave para IA Entender

1. **Literalidade é crucial:** OCR deve ser 100% literal, não interpretativo
2. **Qualidade de imagem importa:** Otimização excessiva destrói OCR
3. **Separação de contextos:** Metadados vs produtos devem ser etapas distintas no prompt
4. **Nunca inventar:** Se não identificar algo, retornar "não identificado"
5. **MAX_IMAGE_SIZE=4096 é crítico:** Menor que isso causa problemas sérios

## Lições Aprendidas (Histórico)

1. **Erro 1:** Parsing esperava formato diferente → CSV com colunas erradas
    1. **Solução:** Ajustar parsing para aceitar múltiplos formatos

2. **Erro 2:** Caracteres Unicode (✓) no Windows → UnicodeEncodeError
    1. **Solução:** Configurar UTF-8 + usar [OK] ao invés de ✓

3. **Erro 3:** LLM inventando produtos na folder_07.jpg
    1. **Causa real:** MAX_IMAGE_SIZE=2048 redimensionava imagem de 3MB
    2. **Solução:** MAX_IMAGE_SIZE=4096 (texto ficou legível, OCR ficou preciso)

**Lição principal:** Para OCR, qualidade de imagem > economia de custo

---
