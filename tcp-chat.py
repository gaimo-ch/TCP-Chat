#!/usr/bin/env python3
import datetime
import socket
import netifaces
from rich.console import Console
from typing import Optional
import typer

console = Console()
server_port = 5000
bufsize = 4096
format = 'utf-8'
date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

app = typer.Typer()

@app.command("s")
def run_server(nic: str = typer.Argument('ens18', help='Network interface (default: ens18)')):
    """Run TCP Chat Server"""
    server_ip = netifaces.ifaddresses(nic)[netifaces.AF_INET][0]['addr']

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

            server_msg = f'{date} - Finished'
            client_socket.sendall(server_msg.encode(format)) # クライアントにメッセージを送信
        
            client_socket.close()

    except socket.error as e:
        console.print(f'Socket error: {e}', style='bold red')
        server_socket.close()

    except KeyboardInterrupt:
        console.print('Finishing...', justify='center')
        server_socket.close()

    console.print('Server closed', justify='center')

@app.command("c")
def run_client(server_ip: str = typer.Argument(..., help='Server IP address')):
    """Run TCP Chat Client"""
    client_socket = None

    try:
        console.rule('TCP Chat Client 📡', style='blue')

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
    app()
