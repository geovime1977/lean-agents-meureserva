# MeuReserva

Assistente financeiro para baixa renda: orcamento 50/30/20 automatico,
micro-reserva via Pix e gamificacao de metas.

## Como rodar

```bash
cd ~/projetos/assistente-financeiro-baixa-renda
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Funcionalidades

- Orcamento 50/30/20 automatico
- Categorizacao inteligente de gastos
- Agendamento de micro-reserva Pix
- Metas financeiras com gamificacao
- Streaks e badges de conquista
- Dashboard com graficos

## Deploy

Streamlit Community Cloud:
1. Conecte o repositorio GitHub
2. Config: streamlit run app.py
3. Variaveis de ambiente: SECRET_KEY, SECRET_PREMIUM_KEY, PIX_KEY
