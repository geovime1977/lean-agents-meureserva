# MeuReserva — Guia de Instalação

Assistente financeiro pessoal com orçamento 50/30/20, controle de gastos e metas de reserva. Roda 100% na sua máquina — seus dados **não saem daqui**.

────────────────────────────────────────────────────────────

## O que o MeuReserva faz

- **Orçamento 50/30/20** automático — 50% essenciais, 30% desejos, 20% reserva
- **Registro de gastos** organizado por categoria
- **Metas financeiras** com gamificação (badges, streaks)
- **Micro-reserva por Pix** (opcional) — QR code pra transferir pequenos valores pra você mesmo
- **Dashboard visual** com gráficos de evolução

Não precisa de internet depois de instalado. Seus dados ficam num arquivo na sua pasta pessoal — sem cadastro, sem nuvem, sem cobrança.

────────────────────────────────────────────────────────────

## Requisitos

- Computador com **Windows** ou **Mac**
- **Python 3.10** ou mais recente instalado (grátis em https://www.python.org/downloads/)
  - **Windows:** na tela de instalação, marque a caixa **"Add Python to PATH"** antes de clicar em Install
  - **Mac:** o instalador do site do Python já configura tudo
- Cerca de **200 MB de espaço em disco**
- Conexão à internet **só na primeira instalação** (pra baixar as bibliotecas)

────────────────────────────────────────────────────────────

## Como instalar — 3 passos

### Passo 1 — Descompactar o pacote

Se recebeu em `.zip`, dá duplo-clique nele e extrai tudo para uma pasta à sua escolha (ex: `Área de Trabalho/MeuReserva/`).

Vai aparecer esta estrutura:

```
MeuReserva/
├── 1-INSTALAR-mac.command       ← instalador Mac
├── 1-INSTALAR-windows.bat       ← instalador Windows
├── 2-RODAR-mac.command          ← abrir o app (Mac)
├── 2-RODAR-windows.bat          ← abrir o app (Windows)
├── meureserva.zip               ← o app comprimido
└── LEIA-ME.md                   ← este documento
```

### Passo 2 — Rodar o instalador (uma vez só)

**No Mac:**
1. Duplo-clique em `1-INSTALAR-mac.command`
2. Se aparecer *"não pode ser aberto porque é de um desenvolvedor não identificado"*:
   - Clique com o **botão direito** no arquivo → **Abrir** → confirme **Abrir**
3. Aguarde uns 2-3 minutos (a janela vai mostrar o progresso 1/5, 2/5, ...)
4. Quando aparecer *"Instalacao concluida com sucesso"*, feche a janela.

**No Windows:**
1. Duplo-clique em `1-INSTALAR-windows.bat`
2. Se o Windows perguntar sobre *"Windows protegeu seu PC"*:
   - Clique em **Mais informações** → **Executar assim mesmo**
3. Aguarde uns 2-3 minutos (a janela preta mostra o progresso).
4. Quando aparecer *"Instalacao concluida com sucesso"*, pressione **ENTER** para fechar.

### Passo 3 — Abrir o app (sempre que quiser usar)

- **Mac:** duplo-clique em `2-RODAR-mac.command`
- **Windows:** duplo-clique em `2-RODAR-windows.bat`

O navegador abre sozinho em http://localhost:8512.

Para encerrar, fecha a janela preta/terminal ou aperta **Ctrl+C** nela.

────────────────────────────────────────────────────────────

## Primeira vez usando

1. **Crie uma conta local** — só um nome de usuário e um PIN de 4 dígitos. Nada disso vai pra internet, fica só na sua máquina.
2. **Cadastre sua renda mensal** — o app calcula automaticamente quanto vai pra essenciais, desejos e reserva.
3. **Comece a registrar gastos** — cada compra vai pra uma categoria.
4. **Crie uma meta** — ex: "Reserva de emergência de R$1.500 em 6 meses". O app mostra o quanto falta.

────────────────────────────────────────────────────────────

## Funcionalidade opcional: Micro-Reserva por Pix

Se você quiser transferir automaticamente pequenos valores pra sua própria conta poupança/investimento via Pix, edite o arquivo `meureserva/.env` (dentro da pasta descompactada) e coloque **sua** chave Pix na linha `PIX_KEY=`:

```
PIX_KEY=seu-email@exemplo.com
```

Aceita e-mail, CPF, telefone (com DDD) ou chave aleatória. Se deixar em branco, essa funcionalidade fica desabilitada e o app funciona normalmente.

────────────────────────────────────────────────────────────

## Se algo der errado

**"Python não está instalado"** (ao rodar o instalador)
→ Instale de https://www.python.org/downloads/ e rode o instalador de novo. No Windows, lembre da caixa "Add Python to PATH".

**"Address already in use" na porta 8512**
→ Outro programa está usando essa porta. Feche outros apps ou reinicie o computador.

**Janela abre e fecha muito rápido no Windows**
→ Abra o Prompt de Comando (cmd), vá até a pasta e rode `1-INSTALAR-windows.bat` de lá — assim a mensagem de erro fica visível.

**Não abre no navegador automaticamente**
→ Abra o navegador manualmente e digite http://localhost:8512

**Quero desinstalar tudo**
→ Basta apagar a pasta MeuReserva inteira. Nada foi instalado fora dela — nem no sistema, nem no registro do Windows. Seus dados também são apagados junto (não tem backup em nuvem).

────────────────────────────────────────────────────────────

## Privacidade

- Nenhum dado sai da sua máquina.
- Não há cadastro em servidor.
- Não há telemetria (o app foi configurado para desligar a coleta de estatísticas do Streamlit).
- Se você deletar a pasta, todos os dados são apagados junto.

────────────────────────────────────────────────────────────

Autor: Geovane Virmecati · Eixo Estratégico · eixoestrategico.com.br
