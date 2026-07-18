# ZyphorixVoice

**Tradutor de Voz em Tempo Real** — base modular para integração com jogos como Roblox, GTA RP, FiveM, Valorant, Discord e VRChat.

## Status

> 🔧 Em desenvolvimento ativo — fase de estruturação inicial (v0.1.0)

## Requisitos

- Python **3.12+**
- Sistema operacional: **Windows 10/11** (suporte a Linux/macOS planejado)

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Ninja10142633/ZyphorixVoice.git
cd ZyphorixVoice

# 2. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
copy .env.example .env      # Windows
# cp .env.example .env       # Linux/macOS

# 5. Execute
python main.py
```

## Estrutura do Projeto

```
ZyphorixVoice/
│
├── app/
│   ├── audio/          # Captura e processamento de áudio (futuro)
│   ├── speech/         # Reconhecimento de fala — Whisper (futuro)
│   ├── translator/     # Motor de tradução (futuro)
│   ├── tts/            # Text-to-Speech (futuro)
│   ├── ui/             # Interface gráfica — CustomTkinter
│   ├── config/         # Configurações e variáveis de ambiente
│   └── utils/          # Utilitários: logger, helpers
│
├── tests/              # Testes automatizados
├── assets/             # Imagens, ícones, recursos estáticos
├── logs/               # Logs gerados em execução (ignorados pelo Git)
│
├── main.py             # Ponto de entrada da aplicação
├── requirements.txt    # Dependências do projeto
├── .env.example        # Template de variáveis de ambiente
└── .gitignore
```

## Roadmap

| Versão | Feature |
|--------|---------|
| v0.1.0 | ✅ Estrutura base + interface gráfica |
| v0.2.0 | 🔲 Captura de áudio em tempo real |
| v0.3.0 | 🔲 Reconhecimento de fala (Whisper) |
| v0.4.0 | 🔲 Tradução automática |
| v0.5.0 | 🔲 Text-to-Speech com voz customizada |
| v1.0.0 | 🔲 Microfone virtual + integração com jogos |

## Licença

Proprietário — © 2026 ZyphorixVoice. Todos os direitos reservados.