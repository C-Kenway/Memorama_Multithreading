import socket
import random
import threading

HOST = "localhost"
PORT = 12345
buffer_size = 1024
numConn = 4

# Variable global para almacenar el estado del juego
game_state = None
game_lock = threading.Lock()

def build_board(difficulty):
    if difficulty == "1":
        words = ['gato', 'perro', 'oso', 'conejo']
        board_size = 8
        modo = 'Principiante'
    elif difficulty == "2":
        words = ['gato', 'perro', 'oso', 'conejo', 'pez', 'lobo', 'jirafa', 'canario', 'iguana']
        board_size = 18
        modo = 'Avanzado'
    else:
        return None

    board = random.sample(words * 2, board_size)
    random.shuffle(board)
    flipped = ['X'] * board_size
    print(board)
    return board, flipped, board_size, modo

def play_game(client_socket, board, flipped, board_size):
    attempts = 0
    last_choice = None
    while True:
        choice = int(client_socket.recv(buffer_size).decode().strip())
        if choice < 0 or choice >= board_size:
            client_socket.send(str('Intente de nuevo.').encode())
            client_socket.send(str('Opción inválida').encode())
            attempts = 0
        elif flipped[choice] != 'X':
            client_socket.send(str("Anterior:" + carta_previa).encode())
            client_socket.send(str('Carta ya seleccionada').encode())
            attempts = 0
        else:
            attempts += 1
            flipped[choice] = board[choice]
            carta = board[choice]
            if attempts == 2:
                client_socket.send(str('Carta Volteada: '+carta).encode())
                if board[choice] == board[last_choice]:
                    client_socket.send(str('\n¡Felicidades! Ha formado una pareja').encode())
                    flipped[last_choice] = board[last_choice]
                    flipped[choice] = board[choice]
                    attempts = 0
                    if "X" not in flipped:
                        client_socket.sendall(str('\n¡Felicidades! Ha ganado el juego\n').encode())
                        break
                else:
                    client_socket.sendall(str('No fue pareja. Sigue jugando\n').encode())
                    flipped[last_choice] = 'X'
                    flipped[choice] = 'X'
                    attempts = 0
            elif attempts == 1:
                client_socket.sendall(str('Carta Volteada: '+carta).encode())
                client_socket.sendall(str('Siguiente tiro').encode())
                last_choice = choice
                carta_previa = carta
def run_game(client_socket):
    global game_state
    game = game_state
    if game is not None:
        board, flipped, board_size, modo = game
        print("Listo para jugar")
        client_socket.send(str(modo).encode())
        play_game(client_socket, board, flipped, board_size)
    else:
        print("Algo salió mal")
    client_socket.close()

def servirPorSiempre(socketTcp, listaconexiones):
    global game_state
    try:
        while True:
            client_socket, client_addr = socketTcp.accept()
            print(f"Se ha establecido una conexión desde {client_addr[0]}:{client_addr[1]}")
            client_socket.send(str("Dificultad: 1)Principiante 2)Avanzado \nIngrese número:").encode())
            difficulty = client_socket.recv(buffer_size).decode().strip()
            with game_lock:
                if game_state is None:
                    game_state = build_board(difficulty)
                listaconexiones.append(client_socket)
                thread_read = threading.Thread(target=run_game, args=[client_socket])
                thread_read.start()
    except Exception as e:
        print("Error en servir")
        print(e)

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("Hilos activos:", threading.active_count())
    print("Enumeración:", threading.enumerate())
    print("Conexiones:", len(listaconexiones))
    print(listaconexiones)

listaconexiones = []
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")
    servirPorSiempre(TCPServerSocket, listaconexiones)
