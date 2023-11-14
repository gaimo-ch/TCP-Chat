#!/usr/bin/env python3
import argparse
import datetime
import socket
import netifaces
from rich.console import Console

def server(interface):
    server_ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    server_port = 5000
    bufsize = 4096
    format = 'utf-8'
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    console = Console()

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Address already in use対策
        server_socket.bind((server_ip, server_port))
        server_socket.listen()

        while True:
            console.rule(f'TCP Chat Server 📡 Listening on {server_ip}:{server_port}', style='blue')

            client_socket, (client_ip, client_port) = server_socket.accept()

            console.print(f'{date} - Accepted a connection from {client_ip}:{client_port}', justify='center')

            client_msg = client_socket.recv(bufsize) # クライアントからのメッセージを受信
            console.print(client_msg.decode(format), justify='center') # クライアントからのメッセージを表示

            server_msg =  f'{date} - Finished'
            client_socket.sendall(server_msg.encode(format)) # クライアントにメッセージを送信
        
            client_socket.close()

    except socket.error as e:
        console.print(f'Socket error: {e}', style='bold red')
        server_socket.close()

    except KeyboardInterrupt:
        console.print('Finishing...', justify='center')
        server_socket.close()

    console.print('Server closed', justify='center')

def client():
    server_port = 5000
    bufsize = 4096
    format = 'utf-8'
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    console = Console()

    client_socket = None

    try:
        console.rule('TCP Chat Client 📡', style='blue')

        console.print('Enter a IP Address...', justify='center')
        server_ip = input()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        console.print(f'{date} - Connected to {server_ip}:{server_port}', justify='center')
        console.print('Enter a message...', justify='center')

        client_msg = input()
        client_socket.sendall(client_msg.encode(format)) # サーバにメッセージを送信
        server_msg = client_socket.recv(bufsize) # サーバからのメッセージを受信
        console.print(f'{server_msg.decode(format)}', justify='center') # サーバからのメッセージを表示

    except socket.error as e:
        console.print(f'Socket error: {e}', style='bold red')

    except KeyboardInterrupt:
        console.print('Finishing...', justify='center')

    finally:
        if client_socket is not None:
            client_socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP Chat')
    subparsers = parser.add_subparsers(dest='command', help='Choose command (server or client)')

    server_parser = subparsers.add_parser('s', help='Run TCP Chat Server')
    server_parser.add_argument('-i', '--interface', type=str, default='ens18', help='Network interface (default: ens18)')

    client_parser = subparsers.add_parser('c', help='Run TCP Chat Client')

    args = parser.parse_args()

    if args.command == 's':
        server(args.interface)
    elif args.command == 'c':
        client()
    else:
        print("Invalid command. Use 's' or 'c'.")
