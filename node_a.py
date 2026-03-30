import threading
import time
from blowfish import expand_key
from server import start_server
from client import connect_to_peer, send_to, send_to_all

MY_NAME = "Laptop A"
MY_PORT = 5555
PEERS = [
    {"name": "Laptop B", "ip": "127.0.0.1", "port": 5556},
    {"name": "Laptop C", "ip": "127.0.0.1", "port": 5557},
]
KEY = b'cheie_secreta_demo'

p, s = expand_key(KEY)

connections = {}
lock = threading.Lock()

def start_all_connections():
    threads = []
    for peer in PEERS:
        t = threading.Thread(
            target=connect_to_peer,
            args=(peer, p, s, connections, lock),
            daemon=True
        )
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def print_peers():
    with lock:
        available = list(connections.keys())
    if available:
        print("\nPeers conectați:")
        for name in available:
            print(f"  - {name}")
    else:
        print("\n(!) Niciun peer conectat încă.")
    print()

def main():
    t_server = threading.Thread(
        target=start_server,
        args=(MY_PORT, p, s),
        daemon=True
    )
    t_server.start()

    time.sleep(1) 

    print(f"\n[*] {MY_NAME} pornit. Mă conectez la peers...\n")
    start_all_connections()
    print(f"\n[*] Gata. Poți trimite mesaje.\n")

    peer_names = [p["name"] for p in PEERS]

    while True:
        print("─" * 45)
        print(f"Comenzi: all | {' | '.join(peer_names)} | peers | exit")
        cmd = input(">> ").strip()

        if cmd == 'exit':
            break

        elif cmd == 'peers':
            print_peers()

        elif cmd == 'all':
            msg = input("Mesaj către toți: ").strip()
            if msg:
                send_to_all(msg, MY_NAME, connections, lock, p, s)

        elif cmd in peer_names:
            msg = input(f"Mesaj către {cmd}: ").strip()
            if msg:
                send_to(cmd, msg, MY_NAME, connections, lock, p, s)

        else:
            print("[!] Comandă necunoscută.")

if __name__ == '__main__':
    main()
