# A Esmeralda da Floresta

RPG por turnos desenvolvido em Python e Pygame. O jogador enfrenta esqueletos em nove níveis e o Guardião da Esmeralda no nível 10.

![Combate contra um esqueleto envenenado](docs/img/combate.png)

## Recursos

- Quatro ações de combate: ataque, bola de fogo, cura e defesa.
- Gestão de HP, stamina e mana entre batalhas.
- Esqueletos envenenados com fraquezas a dano mágico e físico.
- Chefe final com animação de entrada, combate e encerramento.
- Interface redimensionável e efeitos de dano.
- Inimigos com 10% menos HP e dano para reduzir a dificuldade.

## Ações

| Ação | Custo | Efeito |
| --- | --- | --- |
| Ataque | 11 ST | 14–20 de dano físico |
| Bola de Fogo | 16 MP | 26–34 de dano mágico |
| Curar | 13 MP | Recupera 26–34 HP |
| Defender | — | Reduz em 40% o próximo golpe e recupera até 24 ST e 10 MP |

## Capturas de tela

![Introdução do Guardião da Esmeralda](docs/img/chefe-intro.png)

![Combate contra o Guardião da Esmeralda](docs/img/chefe-luta.png)

![Cena de vitória](docs/img/vitoria.png)

## Executar

Requer Python 3.10 ou posterior.

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

## Estrutura

```text
assets/       Imagens e fontes
docs/img/     Capturas de tela
src/          Combate, interface e lógica do jogo
run.py        Ponto de entrada
```
