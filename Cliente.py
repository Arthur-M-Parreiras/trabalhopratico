import socket
import threading


class BlackjackClient:
    def __init__(self, server_host='localhost', server_port=5000):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (server_host, server_port)
        self.player_name = input("Digite seu nome: ").strip()
        self.pontos = 0
        self.cartas = []
        self.playing = False

        # Envia mensagem de entrada
        self.send_message(f"ENTRAR:{self.player_name}")

        # Thread para receber mensagens
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

        self.run()

    def calculate_card_value(self, card):
        """Calcula o valor da carta conforme regras do Blackjack"""
        value = card[:-1]  # Remove o naipe

        if value in ['K', 'Q', 'J']:  # Rei, Dama, Valete = 10
            return 10
        elif value == 'A':  # Ás pode ser 1 ou 11 (implementação básica como 11)
            return 1
        else:  # Números de 2-10
            return int(value)

    def send_message(self, message):
        """Envia mensagem para o servidor"""
        try:
            self.client_socket.sendto(message.encode(), self.server_address)
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def receive_messages(self):
        """Processa mensagens recebidas do servidor"""
        while True:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                message = data.decode().strip()

                if message.startswith('CARTA:'):
                    card = message[6:]
                    self.cartas.append(card)
                    card_value = self.calculate_card_value(card)
                    print(f"\nVocê recebeu: {card} (Valor: {card_value})")

                elif message.startswith('PONTOS:'):
                    self.pontos = int(message[7:])
                    print(f"\n=== SUA MÃO ATUAL ===")
                    print(f"Cartas: {', '.join(self.cartas)}")
                    print(f"Pontuação total: {self.pontos}")

                    # Mostra detalhamento dos valores
                    print("\nDetalhe das cartas:")
                    for card in self.cartas:
                        value = self.calculate_card_value(card)
                        print(f"- {card}: {value} ponto{'s' if value != 1 else ''}")

                    print("=====================\n")

                elif message.startswith('RESULTADO:'):
                    result = message[10:]
                    print(f"\n=== RESULTADO FINAL ===")
                    print(f"Você {result}!")
                    print(f"\nSuas cartas:")
                    for card in self.cartas:
                        value = self.calculate_card_value(card)
                        print(f"- {card}: {value} ponto{'s' if value != 1 else ''}")
                    print(f"\nPontuação final: {self.pontos}")
                    print("======================")
                    self.playing = False

                elif message.startswith('MENSAGEM:'):
                    print(f"\n[Servidor] {message[9:]}")

                elif message.startswith('STATUS:'):
                    print(f"\n[Status] {message[7:]}")

            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break

    def run(self):
        """Loop principal do cliente"""
        print("\n=== BLACKJACK UDP CLIENT ===")
        print("Comandos disponíveis:")
        print("1 - Pedir carta (Hit)")
        print("2 - Parar (Stand)")
        print("3 - Ver status")
        print("0 - Sair\n")

        print("Regras:")
        print("- Ás (A) vale 1 pontos")
        print("- Figuras (K, Q, J) valem 10 pontos")
        print("- Números (2-10) valem seu valor nominal")
        print("- Objetivo: chegar o mais perto possível de 21 sem estourar\n")

        self.playing = True

        while self.playing:
            try:
                choice = input("Sua escolha (1-3): ").strip()

                if choice == '1':
                    self.send_message("PEDIR_CARTA")
                elif choice == '2':
                    self.send_message("PARAR")
                elif choice == '3':
                    self.send_message("STATUS")
                elif choice == '0':
                    print("Saindo...")
                    break
                else:
                    print("Opção inválida. Tente novamente.")

            except KeyboardInterrupt:
                print("\nSaindo...")
                break
            except Exception as e:
                print(f"Erro: {e}")

        self.client_socket.close()


if __name__ == '__main__':
    BlackjackClient()