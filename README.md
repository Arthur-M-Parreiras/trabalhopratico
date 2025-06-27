# Blackjack UDP Client

Um cliente para jogar Blackjack via UDP em Python, com comunicação com um servidor dedicado.

## Funcionalidades

- Conexão com servidor UDP para jogar Blackjack
- Recebe 2 cartas iniciais do servidor
- Sistema de pontuação com regras simplificadas:
  - Ás (A) vale 1 ponto
  - Figuras (K, Q, J) valem 10 pontos
  - Números (2-10) valem seu valor nominal
- Interface interativa no terminal
- Detalhamento das cartas e pontuação

## Requisitos

- Python 3.6 ou superior
- Servidor de Blackjack UDP compatível

## Como Executar

1. Clone o repositório:
https://github.com/Arthur-M-Parreiras/trabalhopratico


2. Execute o cliente (o servidor deve estar rodando):
python client.py e client2.py


3. Siga as instruções no terminal:
   - Digite seu nome
   - Use os comandos para jogar

## Comandos do Jogo

| Comando | Ação                |
|---------|---------------------|
| 1       | Pedir carta (Hit)   |
| 2       | Parar (Stand)       |
| 3       | Ver status          |
| 0       | Sair do jogo        |

## Regras do Jogo

- Objetivo: chegar o mais perto possível de 21 pontos sem estourar
- Você começa com 2 cartas
- O dealer (servidor) controla as regras completas do jogo
- O cliente apenas exibe suas cartas e pontuação

