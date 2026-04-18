# Arquitetura Completa: Plataforma Web de Extração de Flyers + Sistema de Agentes

## Visão Geral

Sistema evolutivo em 3 fases:
1. **Fase 1 (MVP):** Plataforma web - upload manual de imagens
2. **Fase 2 (Expansão):** Sistema de agentes - coleta automatizada
3. **Fase 3 (Futuro):** Analytics e APIs públicas

---

## FASE 1: Plataforma Web (MVP)

### 1.1 Arquitetura de Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  React/Next.js ou Vue.js                               │ │
│  │  - Interface de upload (drag & drop)                   │ │
│  │  - Preview de imagens                                  │ │
│  │  - Visualização de resultados                          │ │
│  │  - Download de CSV                                     │ │
│  │  - Histórico de processamentos                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS/REST API
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY / LOAD BALANCER              │
│                    (Nginx ou AWS ALB)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (API)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI ou Flask (Python)                             │ │
│  │                                                          │ │
│  │  Endpoints:                                             │ │
│  │  - POST /api/upload        (recebe imagem)             │ │
│  │  - GET  /api/status/{id}   (consulta processamento)    │ │
│  │  - GET  /api/result/{id}   (baixa CSV)                 │ │
│  │  - GET  /api/history       (histórico do usuário)      │ │
│  │  - DELETE /api/result/{id} (remove processamento)      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   STORAGE    │    │    QUEUE     │    │   DATABASE   │
│  (S3/Blob)   │    │  (Redis/     │    │ (PostgreSQL) │
│              │    │   RabbitMQ)  │    │              │
│  - Imagens   │    │  - Jobs      │    │  - Usuários  │
│  - CSVs      │    │  - Status    │    │  - Flyers    │
│  - Logs      │    │              │    │  - Produtos  │
└──────────────┘    └──────────────┘    └──────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   WORKER POOL                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Worker 1  │  │  Worker 2  │  │  Worker N  │           │
│  │            │  │            │  │            │           │
│  │  Celery/   │  │  Celery/   │  │  Celery/   │           │
│  │  RQ Worker │  │  RQ Worker │  │  RQ Worker │           │
│  │            │  │            │  │            │           │
│  │  Executa   │  │  Executa   │  │  Executa   │           │
│  │  main_     │  │  main_     │  │  main_     │           │
│  │  improved  │  │  improved  │  │  improved  │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                   ┌──────────────┐
                   │  OpenAI API  │
                   │  GPT-4o-mini │
                   └──────────────┘
```

### 1.2 Stack Tecnológica (Fase 1)

#### Frontend
**Opção A - Next.js (Recomendado)**
- Framework: Next.js 14+ (React)
- Linguagem: TypeScript
- UI Components: shadcn/ui ou Material-UI
- Upload: react-dropzone
- Estado: Zustand ou React Query
- Gráficos (futuro): Recharts ou Chart.js

**Opção B - Vue.js**
- Framework: Nuxt.js 3
- Linguagem: TypeScript
- UI Components: Vuetify ou PrimeVue

#### Backend
**FastAPI (Recomendado para este projeto)**
```
Vantagens:
- Python nativo (reutiliza main_improved.py)
- Async/await nativo
- Validação automática (Pydantic)
- Documentação automática (Swagger)
- Performance alta
- WebSocket suporte (para updates em tempo real)
```

**Alternativa: Flask**
```
Vantagens:
- Mais simples
- Menos curva de aprendizado
- Ecossistema maduro
```

#### Fila de Processamento
**Celery + Redis (Recomendado)**
```
Celery: Sistema de fila de tarefas
Redis: Broker de mensagens + Cache
```

**Alternativa: RQ (Redis Queue)**
```
Mais simples que Celery
Suficiente para MVP
```

#### Banco de Dados
**PostgreSQL (Recomendado)**
```
Relacional, robusto, JSON support
ORM: SQLAlchemy ou Prisma
```

**Alternativa para MVP: SQLite**
```
Zero configuração
Suficiente para testes
```

#### Storage
**Desenvolvimento: Sistema de arquivos local**
**Produção: AWS S3 ou Azure Blob Storage**

#### Monitoramento
- Logs: Python logging + Sentry (erros)
- Métricas: Prometheus + Grafana (opcional para MVP)

### 1.3 Modelo de Dados (Fase 1)

```sql
-- Usuários (autenticação simples ou OAuth)
TABLE users {
  id: UUID PRIMARY KEY
  email: VARCHAR(255) UNIQUE
  password_hash: VARCHAR(255)
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
  is_active: BOOLEAN DEFAULT TRUE
  plan: ENUM('free', 'basic', 'pro') DEFAULT 'free'
}

-- Processamentos de flyers
TABLE flyer_jobs {
  id: UUID PRIMARY KEY
  user_id: UUID FOREIGN KEY → users.id
  filename_original: VARCHAR(255)
  file_path_s3: VARCHAR(512)
  file_size_bytes: BIGINT
  status: ENUM('pending', 'processing', 'completed', 'failed')
  
  -- Resultados
  products_count: INTEGER
  loja_identificada: VARCHAR(255)
  tipo_comercio: VARCHAR(100)
  validade: VARCHAR(100)
  
  -- Arquivos gerados
  csv_path_s3: VARCHAR(512)
  
  -- Metadados
  created_at: TIMESTAMP
  started_at: TIMESTAMP
  completed_at: TIMESTAMP
  error_message: TEXT
  processing_time_seconds: FLOAT
  
  -- Custos
  api_calls: INTEGER
  estimated_cost_usd: DECIMAL(10,6)
  
  INDEXES:
    - user_id, created_at (histórico)
    - status (monitoramento)
}

-- Produtos extraídos
TABLE products {
  id: UUID PRIMARY KEY
  flyer_job_id: UUID FOREIGN KEY → flyer_jobs.id
  
  produto_nome: TEXT
  preco: VARCHAR(50)
  loja: VARCHAR(255)
  tipo_comercio: VARCHAR(100)
  validade: VARCHAR(100)
  
  -- Para análises futuras
  categoria_inferida: VARCHAR(100) -- ex: "higiene", "alimento"
  marca_extraida: VARCHAR(100)
  quantidade_extraida: VARCHAR(50)
  
  created_at: TIMESTAMP
  
  INDEXES:
    - flyer_job_id (consulta rápida)
    - produto_nome (busca) -- usar full-text search
    - preco (filtros)
}

-- Log de operações
TABLE operation_logs {
  id: UUID PRIMARY KEY
  flyer_job_id: UUID FOREIGN KEY → flyer_jobs.id
  level: ENUM('info', 'warning', 'error')
  message: TEXT
  metadata: JSONB -- informações extras flexíveis
  created_at: TIMESTAMP
  
  INDEXES:
    - flyer_job_id, created_at
}
```

### 1.4 Fluxo de Processamento (Fase 1)

```
┌──────────────────────────────────────────────────────────────┐
│ 1. UPLOAD                                                    │
└──────────────────────────────────────────────────────────────┘
   Usuário faz upload → Frontend → API Backend
                                        ↓
                        Valida arquivo (tipo, tamanho)
                                        ↓
                        Salva em S3/Storage temporário
                                        ↓
                        Cria registro em flyer_jobs (status='pending')
                                        ↓
                        Enfileira job na Redis Queue
                                        ↓
                        Retorna job_id para frontend

┌──────────────────────────────────────────────────────────────┐
│ 2. PROCESSAMENTO ASSÍNCRONO                                  │
└──────────────────────────────────────────────────────────────┘
   Worker pega job da fila
                ↓
   Atualiza status para 'processing'
                ↓
   Baixa imagem do S3
                ↓
   Executa main_improved.py (adaptado)
      - otimizar_imagem()
      - imagem_para_base64()
      - extrair_informacoes_flyer()
      - parsear_resposta_llm()
                ↓
   Salva resultados em products table
                ↓
   Gera CSV e salva em S3
                ↓
   Atualiza flyer_jobs:
      - status='completed'
      - products_count
      - csv_path_s3
      - processing_time_seconds
                ↓
   Notifica frontend via WebSocket (opcional)

┌──────────────────────────────────────────────────────────────┐
│ 3. CONSULTA DE RESULTADOS                                    │
└──────────────────────────────────────────────────────────────┘
   Frontend polling GET /api/status/{job_id}
      ou
   WebSocket recebe notificação
                ↓
   status='completed' → Frontend permite download
                ↓
   GET /api/result/{job_id} → Download do CSV
```

### 1.5 Endpoints da API (Fase 1)

```python
# Autenticação
POST   /api/auth/register          # Criar conta
POST   /api/auth/login             # Login (retorna JWT)
POST   /api/auth/logout            # Logout
GET    /api/auth/me                # Info do usuário logado

# Upload e Processamento
POST   /api/flyers/upload          # Upload de imagem(s)
  Body: multipart/form-data
  Response: { job_id, status }

GET    /api/flyers/{job_id}/status # Status do processamento
  Response: { 
    status: 'pending'|'processing'|'completed'|'failed',
    progress_percent: int,
    products_count: int,
    estimated_time_remaining: int
  }

GET    /api/flyers/{job_id}/result # Download CSV
  Response: text/csv

GET    /api/flyers/{job_id}/preview # Preview dos produtos (JSON)
  Response: [{ produto, preco, loja, ... }]

DELETE /api/flyers/{job_id}        # Deletar processamento

# Histórico
GET    /api/flyers/history         # Lista processamentos do usuário
  Query params: 
    - page, limit (paginação)
    - status (filtro)
    - sort_by, order
  Response: {
    items: [{ job_id, filename, status, created_at, ... }],
    total: int,
    page: int,
    pages: int
  }

# Estatísticas (para dashboard)
GET    /api/stats/summary           # Resumo do usuário
  Response: {
    total_flyers_processed: int,
    total_products_extracted: int,
    total_cost_usd: float,
    last_30_days: { ... }
  }

# Admin (futuro)
GET    /api/admin/users            # Listar usuários
GET    /api/admin/jobs             # Todos os jobs
GET    /api/admin/stats            # Estatísticas globais
```

### 1.6 Componentes da Interface (Fase 1)

```
┌─────────────────────────────────────────────────────────────┐
│                    TELA: Dashboard                           │
├─────────────────────────────────────────────────────────────┤
│  [Header com logo, usuário, sair]                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Upload Area (Drag & Drop)                             │ │
│  │                                                          │ │
│  │     [📁] Arraste imagens aqui                          │ │
│  │          ou clique para selecionar                      │ │
│  │                                                          │ │
│  │     Formatos: JPG, PNG | Máximo: 10MB                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Processamentos Recentes                               │ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ 📄 folder_07.jpg          [Processando... 45%]  │  │ │
│  │  │    23 produtos encontrados  ⏱ 5s restantes       │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ 📄 folder_06.jpg          [✓ Concluído]         │  │ │
│  │  │    18 produtos | Supermercado ABC               │  │ │
│  │  │    [👁 Visualizar] [⬇ Baixar CSV] [🗑 Deletar] │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                          │ │
│  │  [Ver histórico completo →]                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Estatísticas do Mês                                   │ │
│  │                                                          │ │
│  │  📊 42 flyers processados                              │ │
│  │  🛒 847 produtos extraídos                             │ │
│  │  💰 $0.54 em custos de API                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              TELA: Visualização de Resultados                │
├─────────────────────────────────────────────────────────────┤
│  [← Voltar]    folder_06.jpg                                │
│                                                              │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │                  │  │  Informações                    │  │
│  │   [Preview da]  │  │                                 │  │
│  │   [imagem]      │  │  Loja: Supermercado ABC        │  │
│  │                  │  │  Tipo: Supermercado            │  │
│  │                  │  │  Validade: 31/12/2024          │  │
│  │                  │  │  Produtos: 18                   │  │
│  │                  │  │  Processado em: 8.3s           │  │
│  │                  │  │                                 │  │
│  └──────────────────┘  │  [⬇ Baixar CSV]                │  │
│                         │  [📋 Copiar para clipboard]    │  │
│                         └────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Produtos Extraídos                                    │ │
│  │                                                          │ │
│  │  [🔍 Buscar produtos...]                    [Filtros▼] │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │ Produto                         | Preço        │    │ │
│  │  ├────────────────────────────────────────────────┤    │ │
│  │  │ Arroz Tio João 5kg             | R$ 25,90     │    │ │
│  │  │ Feijão Preto 1kg               | R$ 8,50      │    │ │
│  │  │ Óleo de Soja 900ml             | R$ 7,99      │    │ │
│  │  │ ...                             | ...          │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  │                                                          │ │
│  │  Mostrando 18 de 18 produtos                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.7 Segurança (Fase 1)

```
┌─────────────────────────────────────────────────────────────┐
│ AUTENTICAÇÃO E AUTORIZAÇÃO                                  │
└─────────────────────────────────────────────────────────────┘

1. Autenticação
   - JWT (JSON Web Tokens)
   - Refresh tokens para sessões longas
   - OAuth2 (opcional): Google, GitHub
   
2. Autorização
   - RBAC (Role-Based Access Control)
   - Roles: user, admin
   - Usuário só acessa seus próprios flyers

3. Validações
   - Rate limiting: 10 uploads/minuto por usuário
   - Tamanho máximo: 10MB por imagem
   - Formatos permitidos: JPG, JPEG, PNG apenas
   - Validação de content-type real (não só extensão)

4. Proteção de Dados
   - HTTPS obrigatório
   - Senhas: bcrypt com salt
   - Dados sensíveis: criptografados em repouso
   - CORS configurado corretamente
   - CSP (Content Security Policy)

5. API Security
   - API key para OpenAI: variável de ambiente
   - Secrets manager (AWS Secrets Manager, Vault)
   - Validação de inputs (Pydantic)
   - Sanitização de filenames

6. Isolamento
   - Workers rodam com privilégios mínimos
   - Imagens processadas em ambiente isolado
   - Limite de memória/CPU por worker
```

### 1.8 Escalabilidade (Fase 1)

```
┌─────────────────────────────────────────────────────────────┐
│ ESTRATÉGIAS DE ESCALABILIDADE                               │
└─────────────────────────────────────────────────────────────┘

HORIZONTAL (adicionar mais máquinas)
├── Frontend: Servir estático via CDN (Cloudflare, AWS CloudFront)
├── Backend API: Load balancer + múltiplas instâncias
├── Workers: Pool elástico (escala baseado em tamanho da fila)
└── Database: Read replicas para consultas

VERTICAL (máquinas mais potentes)
└── Workers: mais CPU/memória para processar imagens grandes

CACHING
├── Redis: Cache de status de jobs (evita consultas ao DB)
├── CDN: Assets estáticos do frontend
└── Resultados: Cache de CSVs já gerados

OTIMIZAÇÕES
├── Batch processing: processar múltiplas imagens em paralelo
├── Connection pooling: reutilizar conexões com DB e Redis
├── Lazy loading: carregar imagens sob demanda
└── Pagination: limitar resultados de histórico

LIMITES INICIAIS (MVP)
├── Usuários simultâneos: ~100
├── Uploads simultâneos: ~50
├── Workers: 3-5 instâncias
└── Armazenamento: 100GB para começar
```

---

## FASE 2: Sistema de Agentes (Automação)

### 2.1 Arquitetura Expandida

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (mesmo da Fase 1)                │
│                    + Dashboard de Agentes                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND API                             │
│                    (expandido)                               │
│                                                              │
│  Novos endpoints:                                           │
│  - GET/POST /api/agents (gerenciar agentes)                │
│  - GET /api/sources (sites monitorados)                    │
│  - GET /api/scraping-logs (logs de coleta)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   ORQUESTRADOR DE AGENTES                    │
│                   (Airflow ou Prefect)                       │
│                                                              │
│  DAGs/Workflows:                                            │
│  - Coletar flyers diariamente                              │
│  - Processar novos flyers                                  │
│  - Limpar dados antigos                                    │
│  - Enviar notificações                                     │
└─────────────────────────────────────────────────────────────┘
                    ↓               ↓               ↓
        ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
        │   AGENTE 1    │  │   AGENTE 2    │  │   AGENTE N    │
        │  Scrapy/      │  │  Playwright/  │  │  Selenium     │
        │  Beautiful    │  │  Puppeteer    │  │               │
        │  Soup         │  │               │  │               │
        │               │  │               │  │               │
        │  Coleta de:   │  │  Coleta de:   │  │  Coleta de:   │
        │  - Site A     │  │  - Site B     │  │  - Site C     │
        │  - Site D     │  │  - Site E     │  │  - Site F     │
        └───────────────┘  └───────────────┘  └───────────────┘
                    ↓               ↓               ↓
┌─────────────────────────────────────────────────────────────┐
│                     FILA DE SCRAPING                         │
│                     (RabbitMQ ou AWS SQS)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  WORKER POOL (expandido)                     │
│                  Processa imagens coletadas                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (expandido)                      │
│  Novas tabelas:                                             │
│  - sources (sites monitorados)                              │
│  - scraping_logs (histórico de coletas)                    │
│  - price_history (histórico de preços para análises)       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes dos Agentes

```
┌─────────────────────────────────────────────────────────────┐
│ AGENTE: Componentes                                          │
└─────────────────────────────────────────────────────────────┘

1. DESCOBERTA DE FLYERS
   ├── Monitorar URLs conhecidas
   ├── Detectar novos flyers (hash de imagem)
   ├── Identificar padrões de URLs
   └── Lidar com anti-bot (delays, user agents, proxies)

2. DOWNLOAD DE IMAGENS
   ├── Baixar imagens de alta resolução
   ├── Validar integridade (não corrompidas)
   ├── Armazenar metadata (URL original, data de coleta)
   └── Deduplicação (evitar processar o mesmo flyer 2x)

3. PROCESSAMENTO
   ├── Enfileirar na mesma fila dos uploads manuais
   ├── Prioridade: manual > automático
   └── Reprocessamento automático em caso de falha

4. VALIDAÇÃO E QUALIDADE
   ├── Verificar se extração fez sentido
   ├── Detectar flyers inválidos (imagens genéricas)
   ├── Alertar se loja não identificada (pode precisar ajuste)
   └── Comparar com histórico (detectar anomalias de preço)

5. NOTIFICAÇÕES
   ├── Webhook quando novo flyer processado
   ├── Email/push quando oferta relevante
   └── Alertas de falhas para admin
```

### 2.3 Tipos de Agentes

```
┌─────────────────────────────────────────────────────────────┐
│ TIPO 1: Agente de Site Estático (Scrapy/BeautifulSoup)      │
└─────────────────────────────────────────────────────────────┘
Uso: Sites com HTML simples, sem JavaScript pesado

Estratégia:
1. HTTP GET na URL
2. Parse HTML com BeautifulSoup/lxml
3. Encontrar tags <img> ou <a> com links de PDF
4. Baixar imagens/PDFs
5. Salvar metadata

Exemplo de sites:
- Sites de supermercados com páginas estáticas de ofertas
- Blogs de ofertas que hospedam flyers

┌─────────────────────────────────────────────────────────────┐
│ TIPO 2: Agente de Site Dinâmico (Playwright/Selenium)       │
└─────────────────────────────────────────────────────────────┘
Uso: Sites com JavaScript, SPAs, carregamento assíncrono

Estratégia:
1. Iniciar navegador headless
2. Navegar até URL
3. Esperar JavaScript carregar
4. Interagir com elementos (scroll, cliques)
5. Capturar imagens ou links
6. Fechar navegador

Exemplo de sites:
- Sites modernos com React/Vue
- Apps de supermercado com galeria de flyers
- Sites que carregam imagens lazy

┌─────────────────────────────────────────────────────────────┐
│ TIPO 3: Agente de API (requests + JSON)                     │
└─────────────────────────────────────────────────────────────┘
Uso: Sites que expõem APIs públicas

Estratégia:
1. Fazer request para API
2. Parsear JSON
3. Extrair URLs de imagens
4. Baixar imagens

Exemplo de sites:
- Alguns supermercados têm APIs de ofertas
- Agregadores de ofertas

┌─────────────────────────────────────────────────────────────┐
│ TIPO 4: Agente de RSS/Feed                                  │
└─────────────────────────────────────────────────────────────┘
Uso: Sites que publicam feeds RSS/Atom

Estratégia:
1. Parse feed RSS
2. Detectar novos itens
3. Extrair imagens de posts
4. Baixar

Exemplo de sites:
- Blogs de ofertas
- Sites de notícias de varejo
```

### 2.4 Modelo de Dados Expandido (Fase 2)

```sql
-- Sites/lojas monitoradas
TABLE sources {
  id: UUID PRIMARY KEY
  nome_loja: VARCHAR(255)
  url_base: VARCHAR(512)
  tipo_site: ENUM('estatico', 'dinamico', 'api', 'rss')
  agente_tipo: VARCHAR(50) -- 'scrapy', 'playwright', etc
  
  -- Configurações do agente
  config: JSONB -- { 
    "selector": "div.flyer img",
    "wait_for": ".gallery-loaded",
    "pagination": true,
    ...
  }
  
  -- Schedule
  schedule_cron: VARCHAR(50) -- "0 9 * * *" (todo dia 9h)
  is_active: BOOLEAN DEFAULT TRUE
  
  -- Estado
  last_scraped_at: TIMESTAMP
  last_success_at: TIMESTAMP
  consecutive_failures: INTEGER DEFAULT 0
  
  -- Metadados
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
  created_by_user_id: UUID -- admin que configurou
  
  INDEXES:
    - is_active, schedule_cron (scheduler)
}

-- Logs de execução dos agentes
TABLE scraping_logs {
  id: UUID PRIMARY KEY
  source_id: UUID FOREIGN KEY → sources.id
  
  started_at: TIMESTAMP
  completed_at: TIMESTAMP
  status: ENUM('running', 'success', 'partial', 'failed')
  
  -- Resultados
  flyers_found: INTEGER
  flyers_downloaded: INTEGER
  flyers_processed: INTEGER
  
  -- Erros
  error_message: TEXT
  error_trace: TEXT
  
  -- Performance
  duration_seconds: FLOAT
  
  created_at: TIMESTAMP
  
  INDEXES:
    - source_id, created_at
    - status
}

-- Rastreamento de flyers para deduplicação
TABLE flyer_tracking {
  id: UUID PRIMARY KEY
  source_id: UUID FOREIGN KEY → sources.id
  
  -- Identificação única
  url_original: VARCHAR(512)
  image_hash: VARCHAR(64) -- SHA256 da imagem
  
  -- Estado
  first_seen_at: TIMESTAMP
  last_seen_at: TIMESTAMP
  download_count: INTEGER DEFAULT 1
  
  -- Relação com processamento
  flyer_job_id: UUID FOREIGN KEY → flyer_jobs.id
  
  INDEXES:
    - image_hash (deduplicação)
    - url_original (busca)
    - source_id, first_seen_at
}

-- Histórico de preços (para análises futuras)
TABLE price_history {
  id: UUID PRIMARY KEY
  produto_id: UUID FOREIGN KEY → products.id
  
  preco_valor: DECIMAL(10,2) -- preço normalizado
  preco_texto: VARCHAR(50) -- preço como aparece
  
  data_validade: DATE -- quando a oferta expira
  
  created_at: TIMESTAMP
  
  INDEXES:
    - produto_id, created_at
}
```

### 2.5 Orquestração com Airflow

```
┌─────────────────────────────────────────────────────────────┐
│ AIRFLOW: DAGs (Workflows)                                    │
└─────────────────────────────────────────────────────────────┘

DAG 1: scrape_all_sources_daily
├── Schedule: Diariamente às 9h
├── Tasks:
│   1. list_active_sources
│   2. scrape_source_1 (parallel)
│   3. scrape_source_2 (parallel)
│   4. scrape_source_N (parallel)
│   5. check_failures
│   └── send_failure_alerts (conditional)

DAG 2: process_scraped_flyers
├── Schedule: A cada 1 hora
├── Tasks:
│   1. list_pending_flyers
│   2. enqueue_processing_jobs
│   3. monitor_processing_queue
│   └── update_scraping_logs

DAG 3: cleanup_old_data
├── Schedule: Semanalmente
├── Tasks:
│   1. delete_old_flyers (>90 dias)
│   2. archive_old_products (mover para data warehouse)
│   3. vacuum_database
│   └── report_storage_usage

DAG 4: health_check
├── Schedule: A cada 15 minutos
├── Tasks:
│   1. check_database_connection
│   2. check_redis_connection
│   3. check_worker_pool_status
│   4. check_openai_api_status
│   └── send_alerts_if_down

DAG 5: generate_reports
├── Schedule: Diariamente à meia-noite
├── Tasks:
│   1. calculate_daily_stats
│   2. detect_price_changes
│   3. generate_trending_products
│   └── send_daily_summary_email
```

### 2.6 Anti-Bot e Boas Práticas

```
┌─────────────────────────────────────────────────────────────┐
│ ESTRATÉGIAS ANTI-DETECÇÃO                                   │
└─────────────────────────────────────────────────────────────┘

1. RATE LIMITING INTELIGENTE
   ├── Delays randômicos entre requests (3-10s)
   ├── Respeitar robots.txt
   ├── Máximo de requests/minuto por site
   └── Backoff exponencial em caso de erro 429

2. USER AGENTS ROTATIVOS
   ├── Lista de user agents reais (Chrome, Firefox, Safari)
   ├── Rotação a cada request
   └── Headers completos (Accept, Accept-Language, etc)

3. PROXIES (se necessário)
   ├── Pool de IPs rotativos
   ├── Proxies residenciais para sites mais restritivos
   └── Verificação de saúde dos proxies

4. COMPORTAMENTO HUMANO (para Playwright/Selenium)
   ├── Movimentação de mouse aleatória
   ├── Scroll suave
   ├── Tempos de espera realistas
   └── Interações naturais com elementos

5. COOKIES E SESSÕES
   ├── Manter cookies entre requests
   ├── Simular sessões realistas
   └── Clear cookies periodicamente

6. RESPEITO E ÉTICA
   ├── Fazer scraping apenas de dados públicos
   ├── Não sobrecarregar servidores
   ├── Respeitar ToS dos sites (Terms of Service)
   └── Identificar-se nos User-Agent se possível
      Ex: "MyFlyerBot/1.0 (+https://meusiteecontato)"
```

### 2.7 Endpoints Adicionais (Fase 2)

```python
# Gerenciamento de Fontes (Sources)
GET    /api/sources                # Listar sites monitorados
POST   /api/sources                # Adicionar novo site
GET    /api/sources/{id}           # Detalhes de um site
PUT    /api/sources/{id}           # Editar configurações
DELETE /api/sources/{id}           # Remover site
POST   /api/sources/{id}/test      # Testar agente

# Logs de Scraping
GET    /api/scraping-logs          # Histórico de execuções
GET    /api/scraping-logs/{id}     # Detalhes de execução

# Monitoramento de Agentes
GET    /api/agents/status          # Status de todos os agentes
POST   /api/agents/{id}/trigger    # Forçar execução manual
POST   /api/agents/{id}/pause      # Pausar agente
POST   /api/agents/{id}/resume     # Retomar agente

# Análises (para futuro)
GET    /api/analytics/price-trends           # Tendências de preço
GET    /api/analytics/popular-products       # Produtos mais ofertados
GET    /api/analytics/stores-comparison      # Comparação entre lojas
```

---

## FASE 3: Expansões Futuras

### 3.1 Features Avançadas

```
┌─────────────────────────────────────────────────────────────┐
│ ANALYTICS E INSIGHTS                                         │
└─────────────────────────────────────────────────────────────┘

1. Comparação de Preços
   - Mesmo produto em várias lojas
   - Histórico de preços (gráficos)
   - Alertas de melhor preço

2. Recomendações
   - "Produtos semelhantes mais baratos"
   - "Melhores ofertas da semana"
   - Lista de compras otimizada

3. Tendências
   - Produtos em alta
   - Sazonalidade de preços
   - Previsão de ofertas futuras

┌─────────────────────────────────────────────────────────────┐
│ INTEGRAÇÕES                                                  │
└─────────────────────────────────────────────────────────────┘

1. API Pública
   - Endpoints para desenvolvedores externos
   - Rate limiting por API key
   - Documentação Swagger/OpenAPI
   - SDKs em Python, JavaScript

2. Webhooks
   - Notificar aplicações externas
   - Eventos: novo flyer, novo produto, mudança de preço

3. Mobile App
   - React Native ou Flutter
   - Notificações push de ofertas
   - Escaneamento de código de barras

┌─────────────────────────────────────────────────────────────┐
│ MACHINE LEARNING                                             │
└─────────────────────────────────────────────────────────────┘

1. Classificação Automática
   - Categorizar produtos (alimentos, higiene, etc)
   - Detectar marcas automaticamente
   - Normalizar nomes de produtos

2. Detecção de Anomalias
   - Preços suspeitos
   - Produtos inválidos extraídos
   - Fraudes em flyers

3. OCR Melhorado
   - Fine-tuning de modelo próprio
   - Reduzir dependência da OpenAI
   - Processar offline

┌─────────────────────────────────────────────────────────────┐
│ MONETIZAÇÃO                                                  │
└─────────────────────────────────────────────────────────────┘

1. Planos
   - Free: 10 flyers/mês
   - Basic: 100 flyers/mês - $9.90/mês
   - Pro: Ilimitado + API - $29.90/mês
   - Enterprise: On-premise + SLA - Custom

2. Marketplace de Dados
   - Vender acesso a dados agregados
   - APIs para comparadores de preços
   - Insights para varejistas

3. Afiliados
   - Links para produtos
   - Comissão por conversão
```

### 3.2 Infraestrutura em Produção

```
┌─────────────────────────────────────────────────────────────┐
│ DEPLOYMENT: Opções                                           │
└─────────────────────────────────────────────────────────────┘

OPÇÃO A: Cloud Serverless (Recomendado para MVP)
├── Frontend: Vercel ou Netlify
├── Backend: AWS Lambda + API Gateway
├── Workers: AWS Lambda (event-driven)
├── Storage: AWS S3
├── Database: AWS RDS (PostgreSQL) ou Aurora Serverless
├── Queue: AWS SQS
├── Cache: AWS ElastiCache (Redis)
└── Custo inicial: ~$50-100/mês

OPÇÃO B: Kubernetes (Recomendado para escala)
├── Frontend: Pods + Ingress
├── Backend: Deployment com auto-scaling
├── Workers: Job/CronJob
├── Managed Services: RDS, S3, etc
└── Custo inicial: ~$200-500/mês

OPÇÃO C: VPS Tradicional (Recomendado para começar)
├── 1 VPS para API + Frontend (4GB RAM)
├── 1 VPS para Workers (8GB RAM)
├── 1 VPS para PostgreSQL (4GB RAM)
├── Redis no mesmo VPS da API
└── Custo inicial: ~$60-120/mês

┌─────────────────────────────────────────────────────────────┐
│ CI/CD Pipeline                                               │
└─────────────────────────────────────────────────────────────┘

GitHub Actions ou GitLab CI:
1. Commit → Branch
2. Testes automatizados
3. Lint e code quality
4. Build Docker images
5. Deploy para staging
6. Testes de integração
7. Deploy para produção (com aprovação manual)
```

---

## RESUMO DA ARQUITETURA

### Fase 1 (MVP - 2-3 meses)
```
✅ Funcionalidades:
   - Upload manual de flyers
   - Processamento com GPT-4o-mini
   - Download de CSV
   - Histórico de processamentos
   - Dashboard básico

🛠 Stack:
   - Frontend: Next.js + TypeScript
   - Backend: FastAPI + Python
   - Queue: Celery + Redis
   - Database: PostgreSQL
   - Storage: S3 ou local

📊 Capacidade:
   - ~100 usuários simultâneos
   - ~500 flyers/dia
   - Custo: ~$100-200/mês
```

### Fase 2 (Agentes - 3-4 meses após MVP)
```
✅ Funcionalidades adicionais:
   - Agentes de scraping automático
   - Monitoramento de sites
   - Deduplicação inteligente
   - Orquestração com Airflow
   - Alertas e notificações

🛠 Stack adicional:
   - Scrapy/Playwright para scraping
   - Airflow para orquestração
   - RabbitMQ ou SQS para filas
   - Proxies para anti-bot

📊 Capacidade expandida:
   - ~50 sites monitorados
   - ~2000 flyers/dia coletados
   - Custo: ~$500-1000/mês
```

### Fase 3 (Expansão - contínuo)
```
✅ Futuro:
   - Analytics avançados
   - API pública
   - Machine Learning
   - Mobile app
   - Monetização

💰 Potencial:
   - Milhares de usuários
   - Receita recorrente (SaaS)
   - Marketplace de dados
```

---

**Esta arquitetura permite crescimento incremental, começando simples e escalando conforme necessidade!**
