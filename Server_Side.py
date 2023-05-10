import socket
import random
import threading

HOST = "localhost"
PORT = 12345
buffer_size = 1024
numConn = 4
def start_game(client_socket, difficulty):
    if difficulty == "1":
        words = ['gato', 'perro', 'oso', 'conejo']
        board_size = 8
        client_socket.send("Modo: Principiante".encode())
    elif difficulty == "2":
        words = ['gato', 'perro', 'oso', 'conejo','pez','lobo','jirafa','canario','iguana']
        board_size = 18
        client_socket.send('Modo: Avanzado'.encode())
    else:
        client_socket.send('Opción inválida'.encode())
        return None

    board = random.sample(words * 2, board_size)
    random.shuffle(board)
    flipped = ['X'] * board_size
    print(board)
    return board, flipped, board_size

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
                print(carta)
                client_socket.sendall(str(carta).encode())
                client_socket.sendall(str('Siguiente tiro').encode())
                last_choice = choice
                carta_previa = carta

def run_game(client_socket):
    client_socket.send(str("Dificultad: 1)Principiante 2)Avanzado \n Ingrese numero:").encode())
    difficulty = client_socket.recv(buffer_size).decode().strip()
    game = start_game(client_socket, difficulty)
    print("Antes de la funcion game")
    if game is not None:
        board, flipped, board_size = game
        print("listo para jugar")
        play_game(client_socket, board, flipped, board_size)
    else:
        print(game)
        print("Algo malo paso")
    # Cerrar la conexión con el cliente
    client_socket.close()

def servirPorSiempre(socketTcp, listaconexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print(f"Se ha establecido una conexión desde {client_addr[0]}:{client_addr[1]}")
            listaconexiones.append(client_conn)
            thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr])
            thread_read.start()
            gestion_conexiones(listaConexiones)
    except Exception as e:
        print("error en servir")
        print(e)

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)

def recibir_datos(conn, addr):
    cur_thread = threading.current_thread()
    print("Recibiendo datos del cliente {} en el {}".format(addr, cur_thread.name))
    try:
        run_game(conn)
    except Exception as e:
        print("error en recibir")
        print(e)
    finally:
        conn.close()

listaConexiones = []
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones)
