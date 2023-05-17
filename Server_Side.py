import socket
import random
import threading

HOST = "localhost"
PORT = 12345
buffer_size = 1024
numConn = 4

game_state = None
lock = threading.Lock()  # Bloqueo para sincronizar los movimientos de los clientes
board = None  # Tablero compartido entre los clientes

def build_board(difficulty):
    if difficulty == "1":
        words = ['gato', 'perro', 'oso', 'conejo']
        board_size = 8
    elif difficulty == "2":
        words = ['gato', 'perro', 'oso', 'conejo', 'pez', 'lobo', 'jirafa', 'canario', 'iguana']
        board_size = 18
    else:
        return 'Opción inválida', None, None

    return f"Modo: {'Principiante' if difficulty == '1' else 'Avanzado'}", random.sample(words * 2, board_size), ['X'] * board_size

def play_game(client_socket, flipped, board_size):
    global board
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
            with lock:
                attempts += 1
                flipped[choice] = board[choice]
                carta = board[choice]
                if attempts == 2:
                    client_socket.send(str(carta).encode())
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
                    #print(carta)
                    client_socket.sendall(str(carta).encode())
                    client_socket.sendall(str('Siguiente tiro').encode())
                    last_choice = choice
                    carta_previa = carta

def run_game(client_socket):
    global game_state
    global board
    client_socket.send(str("Dificultad: 1)Principiante 2)Avanzado \n Ingrese numero:").encode())
    difficulty = client_socket.recv(buffer_size).decode().strip()
    with lock:
        if game_state is None:
            game_state = build_board(difficulty)
    message, game_board, flipped_cards = game_state
    print(game_board)
    if game_board is None:
        client_socket.send(message.encode())
        client_socket.close()
        return
    with lock:
        if board is None:
            board = game_board

    client_socket.send(message.encode())
    play_game(client_socket, flipped_cards, len(board))
    client_socket.close()

def servirPorSiempre(socketTcp, listaconexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conexión establecida con", client_addr)
            listaconexiones.append(client_conn)
            threading.Thread(target=run_game, args=(client_conn,)).start()
            gestion_conexiones(listaconexiones)
    finally:
        for conn in listaconexiones:
            conn.close()

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)

listaconexiones = []
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketTcp:
    socketTcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketTcp.bind((HOST, PORT))
    socketTcp.listen(numConn)
    print("Esperando conexiones en el puerto", PORT)
    servirPorSiempre(socketTcp, listaconexiones)
