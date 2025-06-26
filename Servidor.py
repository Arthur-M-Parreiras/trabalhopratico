import socket
import random
from threading import Thread, Lock
import time


class BlackjackServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        self.players = {}
        self.game_active = False
        self.lock = Lock()
        self.current_game_id = 0
        print(f"Servidor Blackjack UDP iniciado em {host}:{port}...")

    def create_deck(self):
        """Cria um baralho completo de 52 cartas"""
        valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        naipes = ['♦', '♥', '♠', '♣']
        return [f"{valor}{naipe}" for naipe in naipes for valor in valores]

    def calculate_card_value(self, card):
        """Calcula o valor de uma carta no Blackjack"""
        value = card[:-1]  # Remove o naipe
        if value in ['J', 'Q', 'K']:
            return 10
        elif value == 'A':
            return 11  # Simplificação - em um jogo real poderia ser 1 ou 11
        else:
            return int(value)

    def handle_client_messages(self):
        """Thread principal para lidar com mensagens dos clientes"""
        while True:
            try:
                data, addr = self.server_socket.recvfrom(1024)
                message = data.decode().strip()

                if ':' in message:
                    cmd, *args = message.split(':')
                    args = ':'.join(args)  # Reune os argumentos caso tenham outros ':'
                else:
                    cmd, args = message, ''

                with self.lock:
                    if cmd == 'ENTRAR':
                        self.handle_player_join(addr, args)
                    elif cmd == 'PEDIR_CARTA':
                        self.handle_card_request(addr)
                    elif cmd == 'PARAR':
                        self.handle_player_stop(addr)
                    elif cmd == 'STATUS':
                        self.send_status(addr)
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")

    def handle_player_join(self, addr, player_name):
        """Lida com novos jogadores querendo entrar no jogo"""
        if addr in self.players:
            self.send_message(addr, "MENSAGEM:Você já está no jogo!")
            return

        if self.game_active and len(self.players) >= 4:
            self.send_message(addr, "MENSAGEM:Partida em andamento, aguarde a próxima")
            return

        self.players[addr] = {
            'nome': player_name,
            'pontos': 0,
            'cartas': [],
            'parou': False,
            'perdeu': False
        }

        self.send_message(addr, f"MENSAGEM:Bem-vindo, {player_name}! Aguarde outros jogadores...")

        if len(self.players) >= 2 and not self.game_active:
            self.start_new_game()

    def start_new_game(self):
        """Inicia uma nova partida"""
        self.current_game_id += 1
        self.game_active = True
        self.deck = self.create_deck()
        random.shuffle(self.deck)

        print(f"\n=== Iniciando partida #{self.current_game_id} ===")
        print(f"Jogadores: {[p['nome'] for p in self.players.values()]}")

        # Distribui cartas iniciais
        for addr in self.players:
            self.players[addr]['pontos'] = 0
            self.players[addr]['cartas'] = []
            self.players[addr]['parou'] = False
            self.players[addr]['perdeu'] = False

            # Distribui 2 cartas iniciais
            for _ in range(2):
                self.deal_card(addr)

        self.broadcast("MENSAGEM:Partida iniciada! Suas cartas iniciais foram enviadas.")

    def deal_card(self, addr):
        """Distribui uma carta para um jogador"""
        if not self.deck:
            self.deck = self.create_deck()
            random.shuffle(self.deck)

        card = self.deck.pop()
        card_value = self.calculate_card_value(card)

        self.players[addr]['cartas'].append(card)
        self.players[addr]['pontos'] += card_value

        self.send_message(addr, f"CARTA:{card}")
        self.send_message(addr, f"PONTOS:{self.players[addr]['pontos']}")

        print(f"Jogador {self.players[addr]['nome']} recebeu {card} (Total: {self.players[addr]['pontos']})")

        # Verifica se estourou 21
        if self.players[addr]['pontos'] > 21:
            self.players[addr]['perdeu'] = True
            self.send_message(addr, "RESULTADO:perdeu")
            self.broadcast(f"MENSAGEM:{self.players[addr]['nome']} estourou 21 pontos!")
            self.check_game_end()

    def handle_card_request(self, addr):
        """Lida com pedido de nova carta"""
        if addr not in self.players or not self.game_active:
            self.send_message(addr, "MENSAGEM:Não há jogo ativo")
            return

        if self.players[addr]['parou'] or self.players[addr]['perdeu']:
            self.send_message(addr, "MENSAGEM:Você já finalizou sua jogada")
            return

        self.deal_card(addr)

    def handle_player_stop(self, addr):
        """Lida com jogador decidindo parar"""
        if addr not in self.players or not self.game_active:
            self.send_message(addr, "MENSAGEM:Não há jogo ativo")
            return

        if self.players[addr]['perdeu']:
            self.send_message(addr, "MENSAGEM:Você já perdeu por estourar 21 pontos")
            return

        self.players[addr]['parou'] = True
        self.send_message(addr, "MENSAGEM:Você parou. Aguarde os outros jogadores...")
        self.broadcast(f"MENSAGEM:{self.players[addr]['nome']} parou com {self.players[addr]['pontos']} pontos")
        self.check_game_end()

    def check_game_end(self):
        """Verifica se a partida terminou"""
        active_players = [
            p for p in self.players.values()
            if not p['parou'] and not p['perdeu']
        ]

        if not active_players:
            self.end_game()

    def end_game(self):
        """Finaliza a partida e determina o vencedor"""
        # Encontra a maior pontuação válida (<=21)
        valid_scores = [
            p['pontos'] for p in self.players.values()
            if p['pontos'] <= 21
        ]

        if valid_scores:
            winning_score = max(valid_scores)
            winners = [
                p['nome'] for p in self.players.values()
                if p['pontos'] == winning_score
            ]

            if len(winners) > 1:
                result_msg = f"RESULTADO:empatou com {winning_score} pontos"
            else:
                result_msg = f"RESULTADO:ganhou com {winning_score} pontos"

            # Envia resultados para todos
            for addr, player in self.players.items():
                if player['pontos'] == winning_score:
                    self.send_message(addr, result_msg)
                else:
                    self.send_message(addr,
                                      f"RESULTADO:perdeu (vencedor: {', '.join(winners)} com {winning_score} pontos")

            self.broadcast(f"MENSAGEM:Partida encerrada! Vencedor(es): {', '.join(winners)}")
        else:
            self.broadcast("RESULTADO:perdeu (todos estouraram 21)")

        self.game_active = False
        self.players = {}
        print("=== Partida encerrada ===")

    def send_message(self, addr, message):
        """Envia uma mensagem para um jogador específico"""
        try:
            self.server_socket.sendto(message.encode(), addr)
        except Exception as e:
            print(f"Erro ao enviar mensagem para {addr}: {e}")

    def broadcast(self, message):
        """Envia uma mensagem para todos os jogadores"""
        for addr in self.players:
            self.send_message(addr, message)

    def send_status(self, addr):
        """Envia o status atual do jogo para um jogador"""
        if addr in self.players:
            player = self.players[addr]
            status = (
                f"STATUS:Nome: {player['nome']}, "
                f"Cartas: {', '.join(player['cartas'])}, "
                f"Pontos: {player['pontos']}, "
                f"Status: {'Parou' if player['parou'] else 'Perdeu' if player['perdeu'] else 'Jogando'}"
            )
            self.send_message(addr, status)
        else:
            self.send_message(addr, "STATUS:Você não está em uma partida ativa")


if __name__ == '__main__':
    server = BlackjackServer()
    Thread(target=server.handle_client_messages, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")