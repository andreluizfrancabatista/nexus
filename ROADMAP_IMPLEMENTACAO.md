# Roadmap de Implementação: Do MVP ao Sistema Completo

## Visão Geral do Timeline

```
┌────────────────────────────────────────────────────────────┐
│  Fase 1: MVP Web         │  8-12 semanas                   │
│  Fase 2: Agentes         │  12-16 semanas (após MVP)       │
│  Fase 3: Expansões       │  Contínuo                       │
└────────────────────────────────────────────────────────────┘
```

---

## FASE 1: MVP - Plataforma Web (8-12 semanas)

### Sprint 1: Fundação (Semanas 1-2)

**Setup de Infraestrutura**
- [ ] Criar repositório Git (monorepo ou multi-repo)
- [ ] Configurar estrutura de pastas
- [ ] Setup Docker para desenvolvimento local
- [ ] Configurar variáveis de ambiente (.env)
- [ ] Escolher e configurar hosting (Vercel, AWS, etc)

**Backend Básico**
- [ ] Instalar FastAPI + dependências
- [ ] Criar estrutura de projeto FastAPI
- [ ] Configurar SQLAlchemy + PostgreSQL
- [ ] Migração de schema inicial (Alembic)
- [ ] Endpoint de health check

**Frontend Básico**
- [ ] Criar projeto Next.js com TypeScript
- [ ] Configurar Tailwind CSS ou Material-UI
- [ ] Criar layout base (header, footer, container)
- [ ] Configurar routing

**Deliverables:**
- Repositório configurado
- Backend e frontend rodando localmente
- Database criado

---

### Sprint 2: Autenticação (Semanas 3-4)

**Backend**
- [ ] Implementar registro de usuários
- [ ] Implementar login (JWT)
- [ ] Middleware de autenticação
- [ ] Endpoints: POST /auth/register, POST /auth/login
- [ ] Hash de senhas com bcrypt

**Frontend**
- [ ] Tela de registro
- [ ] Tela de login
- [ ] Gerenciamento de token JWT (localStorage)
- [ ] Protected routes
- [ ] Logout

**Database**
- [ ] Tabela `users`
- [ ] Migrations

**Deliverables:**
- Usuário pode se registrar e fazer login
- Rotas protegidas funcionando

---

### Sprint 3: Upload de Imagens (Semanas 5-6)

**Backend**
- [ ] Endpoint POST /flyers/upload
- [ ] Validação de arquivos (tipo, tamanho)
- [ ] Upload para storage (local ou S3)
- [ ] Criar registro em `flyer_jobs` (status='pending')
- [ ] Retornar job_id

**Frontend**
- [ ] Componente de upload (drag & drop)
- [ ] Preview de imagem antes de upload
- [ ] Barra de progresso
- [ ] Feedback visual (sucesso/erro)

**Database**
- [ ] Tabela `flyer_jobs`
- [ ] Migrations

**Deliverables:**
- Usuário pode fazer upload de imagem
- Imagem é salva e job criado

---

### Sprint 4: Processamento Assíncrono (Semanas 7-8)

**Backend**
- [ ] Configurar Celery + Redis
- [ ] Criar task Celery: `process_flyer(job_id)`
- [ ] Adaptar `main_improved.py` para task
- [ ] Atualizar status do job durante processamento
- [ ] Salvar produtos extraídos na tabela `products`
- [ ] Gerar e salvar CSV

**Database**
- [ ] Tabela `products`
- [ ] Migrations

**Integração**
- [ ] Enfileirar job após upload
- [ ] Worker Celery rodando localmente

**Deliverables:**
- Upload → enfileiramento → processamento funciona
- Produtos salvos no banco
- CSV gerado

---

### Sprint 5: Consulta de Status e Resultados (Semanas 9-10)

**Backend**
- [ ] Endpoint GET /flyers/{job_id}/status
- [ ] Endpoint GET /flyers/{job_id}/result (download CSV)
- [ ] Endpoint GET /flyers/{job_id}/preview (JSON)
- [ ] Endpoint GET /flyers/history (com paginação)
- [ ] Endpoint DELETE /flyers/{job_id}

**Frontend**
- [ ] Dashboard com lista de processamentos
- [ ] Polling de status (ou WebSocket)
- [ ] Visualização de resultados (tabela de produtos)
- [ ] Download de CSV
- [ ] Página de histórico

**Deliverables:**
- Usuário vê status em tempo real
- Usuário baixa CSV
- Histórico funcional

---

### Sprint 6: Polish e Testes (Semanas 11-12)

**Melhorias UX**
- [ ] Loading states
- [ ] Mensagens de erro amigáveis
- [ ] Toasts/notificações
- [ ] Responsividade mobile
- [ ] Acessibilidade básica

**Testes**
- [ ] Testes unitários backend (pytest)
- [ ] Testes de integração
- [ ] Testes E2E frontend (Playwright/Cypress)
- [ ] Teste de carga básico (Locust)

**Documentação**
- [ ] README.md completo
- [ ] API docs (Swagger automático do FastAPI)
- [ ] Guia de deployment

**Deploy**
- [ ] Deploy frontend (Vercel/Netlify)
- [ ] Deploy backend (Heroku/Railway/AWS)
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Monitoramento básico (logs)

**Deliverables:**
- MVP completo e funcional em produção
- Testes passando
- Documentação completa

---

## FASE 2: Sistema de Agentes (12-16 semanas após MVP)

### Sprint 7: Modelagem de Agentes (Semanas 13-14)

**Backend**
- [ ] Criar tabelas: `sources`, `scraping_logs`, `flyer_tracking`
- [ ] Migrations
- [ ] Endpoints CRUD para `sources`
- [ ] Modelo de configuração de agentes (JSON schema)

**Frontend**
- [ ] Interface para adicionar/editar sources
- [ ] Formulário de configuração de agente
- [ ] Validação de configurações

**Deliverables:**
- CRUD de sources funcional
- Admin pode adicionar sites para monitorar

---

### Sprint 8: Agente Básico - Scrapy (Semanas 15-16)

**Scraping**
- [ ] Setup projeto Scrapy
- [ ] Spider genérica configurável
- [ ] Parser de imagens baseado em seletores CSS
- [ ] Download de imagens
- [ ] Deduplicação por hash

**Integração**
- [ ] Agente salva imagens no storage
- [ ] Cria registro em `flyer_tracking`
- [ ] Enfileira jobs de processamento
- [ ] Logs em `scraping_logs`

**Deliverables:**
- Agente Scrapy funcional
- Consegue coletar de sites estáticos

---

### Sprint 9: Orquestração com Airflow (Semanas 17-18)

**Airflow**
- [ ] Setup Airflow (local ou Astronomer)
- [ ] DAG: `scrape_all_sources_daily`
- [ ] DAG: `process_scraped_flyers`
- [ ] DAG: `cleanup_old_data`
- [ ] Configurar conexões (DB, Redis)

**Integração**
- [ ] Airflow trigger scraping jobs
- [ ] Airflow monitora status
- [ ] Alertas de falhas

**Deliverables:**
- Scraping automático rodando diariamente
- Orquestração funcional

---

### Sprint 10: Agente Avançado - Playwright (Semanas 19-20)

**Scraping Dinâmico**
- [ ] Setup Playwright
- [ ] Agente para sites com JavaScript
- [ ] Configuração de selectors dinâmicos
- [ ] Scroll e interações
- [ ] Screenshots para debug

**Anti-Bot**
- [ ] User agents rotativos
- [ ] Delays randômicos
- [ ] Stealth plugin

**Deliverables:**
- Agente Playwright funcional
- Consegue coletar de sites modernos (React/Vue)

---

### Sprint 11: Dashboard de Agentes (Semanas 21-22)

**Frontend**
- [ ] Dashboard de monitoramento de agentes
- [ ] Status de cada source
- [ ] Logs de execução
- [ ] Gráficos de performance
- [ ] Botão de trigger manual

**Backend**
- [ ] Endpoints de estatísticas
- [ ] Endpoint de trigger manual
- [ ] Endpoint de pause/resume

**Deliverables:**
- Admin monitora todos os agentes
- Admin pode intervir manualmente

---

### Sprint 12: Validação e Qualidade (Semanas 23-24)

**Validações**
- [ ] Detectar flyers inválidos
- [ ] Validar se loja foi identificada
- [ ] Comparar com histórico (anomalias)
- [ ] Reprocessamento automático

**Notificações**
- [ ] Sistema de webhooks
- [ ] Emails de alerta
- [ ] Dashboard de alertas

**Deliverables:**
- Sistema robusto com validações
- Alertas funcionando

---

### Sprint 13: Testes e Produção (Semanas 25-26)

**Testes**
- [ ] Testes de agentes (mocks)
- [ ] Testes de integração com Airflow
- [ ] Teste de volume (muitos flyers)

**Deploy**
- [ ] Deploy de agentes
- [ ] Deploy do Airflow
- [ ] Configurar proxies (se necessário)
- [ ] Monitoramento avançado

**Deliverables:**
- Sistema de agentes em produção
- Coletando de múltiplos sites

---

## FASE 3: Expansões (Contínuo)

### Features Prioritárias

**Q1: Analytics Básico**
- [ ] Comparação de preços entre lojas
- [ ] Histórico de preços (gráficos)
- [ ] Produtos em alta
- [ ] Dashboard de insights

**Q2: API Pública**
- [ ] Endpoints públicos
- [ ] Sistema de API keys
- [ ] Rate limiting
- [ ] Documentação para devs
- [ ] SDKs (Python, JS)

**Q3: Machine Learning**
- [ ] Categorização automática de produtos
- [ ] Normalização de nomes
- [ ] Detecção de anomalias
- [ ] Recomendações

**Q4: Mobile App**
- [ ] App React Native ou Flutter
- [ ] Push notifications
- [ ] Escaneamento de código de barras
- [ ] Listas de compras

---

## Recursos Necessários

### Equipe Ideal

**Para MVP (Fase 1):**
- 1 Full-stack developer (ou 1 backend + 1 frontend)
- Part-time: DevOps/Infra

**Para Agentes (Fase 2):**
- + 1 Backend developer (especialista em scraping)
- + 1 DevOps (para Airflow e infra)

**Para Expansão (Fase 3):**
- + 1 Data Scientist (ML)
- + 1 Mobile developer
- + 1 Product Manager

### Custos Estimados

**MVP (Fase 1) - Por Mês:**
- Hosting (Vercel + AWS): $50-100
- Database (RDS ou similar): $30-50
- Redis: $10-20
- OpenAI API: $20-50 (depende do uso)
- **Total: ~$110-220/mês**

**Com Agentes (Fase 2) - Por Mês:**
- MVP costs: $110-220
- Airflow hosting: $50-100
- Workers adicionais: $50-100
- Proxies (se necessário): $50-200
- Aumento de OpenAI: +$100-300
- **Total: ~$360-920/mês**

**Escalado (Fase 3) - Por Mês:**
- Infra: $500-2000
- APIs: $200-1000
- CDN: $50-200
- Monitoramento: $50-100
- **Total: ~$800-3300/mês**

---

## Métricas de Sucesso

### Fase 1 (MVP)
- ✅ 100+ usuários cadastrados
- ✅ 500+ flyers processados
- ✅ Taxa de sucesso > 95%
- ✅ Tempo médio de processamento < 10s
- ✅ NPS > 50

### Fase 2 (Agentes)
- ✅ 20+ sites sendo monitorados
- ✅ 1000+ flyers coletados/semana
- ✅ Taxa de deduplicação > 90%
- ✅ Uptime dos agentes > 95%

### Fase 3 (Expansão)
- ✅ 10,000+ usuários ativos
- ✅ 100,000+ flyers processados/mês
- ✅ API com 1000+ requests/dia
- ✅ Receita mensal > custos

---

## Riscos e Mitigações

### Riscos Técnicos

**Risco 1: Sites mudarem estrutura → Agentes quebram**
- Mitigação: Monitoramento automático de falhas
- Mitigação: Múltiplos seletores de fallback
- Mitigação: Notificações imediatas de falhas

**Risco 2: Bloqueio por anti-bot**
- Mitigação: Proxies rotativos
- Mitigação: Rate limiting conservador
- Mitigação: Comportamento humano (Playwright)

**Risco 3: Custo da OpenAI API crescer muito**
- Mitigação: Cache de resultados
- Mitigação: Fine-tuning de modelo próprio
- Mitigação: Limites por usuário

**Risco 4: Escalabilidade**
- Mitigação: Arquitetura desacoplada
- Mitigação: Horizontal scaling desde o início
- Mitigação: Caching agressivo

### Riscos de Negócio

**Risco 1: Baixa adoção de usuários**
- Mitigação: MVP rápido para validar
- Mitigação: Feedback contínuo de usuários
- Mitigação: Features que resolvem dor real

**Risco 2: Aspectos legais de scraping**
- Mitigação: Consultar advogado especializado
- Mitigação: Respeitar robots.txt e ToS
- Mitigação: Só dados públicos

**Risco 3: Competição**
- Mitigação: Foco em qualidade e precisão
- Mitigação: Features únicas (agentes, analytics)
- Mitigação: Execution speed

---

## Próximos Passos Imediatos

### Semana 1: Decisões Estratégicas
1. ✅ Definir stack final (este doc recomenda Next.js + FastAPI)
2. ✅ Escolher hosting (Vercel + AWS ou similar)
3. ✅ Definir se monorepo ou multi-repo
4. ✅ Criar repositório e estrutura

### Semana 2: Setup Inicial
1. ✅ Configurar ambiente de desenvolvimento
2. ✅ Setup Docker para local dev
3. ✅ Backend: FastAPI + PostgreSQL rodando
4. ✅ Frontend: Next.js rodando
5. ✅ Primeiro deploy (staging)

### Semana 3-4: Primeira Feature
1. ✅ Implementar autenticação completa
2. ✅ Testes da autenticação
3. ✅ Deploy em staging

---

**Este roadmap é flexível e pode ser ajustado conforme feedback e aprendizados!**
