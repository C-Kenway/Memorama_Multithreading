#!/usr/bin/env python3
import socket
import os
HOST = "localhost"  # Nombre del host o direccion ip
#HOST = "192.168.254.223"  # Nombre del host o direccion ip
PORT = 12345  # Puerto usado por el servidor
buffer_size = 1024

#HOST = str(input('Ingrese el la direccion del host para el server: '))
#PORT = int(input('Ingrese el Puerto: '))
# Crear un objeto socket para el cliente
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectar el socket a un servidor remoto en el puerto 5000
cliente.connect((HOST, PORT))
print('Se ha establecido una conexión con el servidor remoto.')

#Selecciona Dificultad del juego
respuesta = cliente.recv(buffer_size).decode()
print(respuesta)
# Envia dificultad
eleccion = str(input())
cliente.send(eleccion.encode())

#Recibe modo de dificultad
respuesta = cliente.recv(buffer_size).decode()
print(respuesta)


# Recibir el tablero oculto del servidor
#tablero_oculto = eval(cliente.recv(buffer_size).decode())
#print('Tablero para tu partida:\n', tablero_oculto)
# Iniciar el bucle del juego
while True:
    # Solicitar al usuario que seleccione una carta
    seleccion = int(input('\nIngrese el número de la carta que desea voltear (0-7): '))

    # Enviar la selección al servidor
    cliente.send(str(seleccion).encode())

    carta_volteada = cliente.recv(buffer_size).decode()
    print(f"Cartas volteadas:{carta_volteada}")

    # Recibir la respuesta del servidor
    respuesta = cliente.recv(buffer_size).decode()
    print(f"Respuesta del servidor:{respuesta}")

    # Verificar si el juego ha terminado
    if '\n ¡Felicidades! Ha ganado el juego' in respuesta:
        break

#tiempoP = cliente.recv(buffer_size).decode()
#print(tiempoP)
#puntaje = cliente.recv(buffer_size).decode()
#print(puntaje)
# Cerrar la conexión con el servidor
cliente.close()