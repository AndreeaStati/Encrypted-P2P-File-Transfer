import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue

from server import start_server
from client import connect_to_peer, send_to, send_to_all
from p2p_utils import send_file_segmented
from blowfish import encrypt_bytes


class P2PInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted P2P File Transfer")

        self.connections = {}
        self.lock = threading.Lock()
        self.logs = queue.Queue()
        self.selected_file = None

        self.my_name = tk.StringVar(value="Laptop A")
        self.my_port = tk.StringVar(value="5555")
        self.peer_name = tk.StringVar(value="Laptop B")
        self.peer_ip = tk.StringVar(value="127.0.0.1")
        self.peer_port = tk.StringVar(value="5556")
        self.message = tk.StringVar()

        self.build_ui()
        self.process_logs()

    def build_ui(self):
        config = tk.LabelFrame(self.root, text="Configurare nod")
        config.pack(fill="x", padx=10, pady=5)

        tk.Label(config, text="Nume:").grid(row=0, column=0)
        tk.Entry(config, textvariable=self.my_name).grid(row=0, column=1)

        tk.Label(config, text="Port local:").grid(row=0, column=2)
        tk.Entry(config, textvariable=self.my_port, width=8).grid(row=0, column=3)

        tk.Button(config, text="Porneste nod", command=self.start_node).grid(row=0, column=4, padx=5)

        peer = tk.LabelFrame(self.root, text="Peer")
        peer.pack(fill="x", padx=10, pady=5)

        tk.Label(peer, text="Nume peer:").grid(row=0, column=0)
        tk.Entry(peer, textvariable=self.peer_name).grid(row=0, column=1)

        tk.Label(peer, text="IP:").grid(row=0, column=2)
        tk.Entry(peer, textvariable=self.peer_ip).grid(row=0, column=3)

        tk.Label(peer, text="Port:").grid(row=0, column=4)
        tk.Entry(peer, textvariable=self.peer_port, width=8).grid(row=0, column=5)

        tk.Button(peer, text="Conecteaza", command=self.connect_peer).grid(row=0, column=6, padx=5)

        chat = tk.LabelFrame(self.root, text="Chat criptat")
        chat.pack(fill="both", expand=True, padx=10, pady=5)

        self.output = tk.Text(chat, height=15)
        self.output.pack(fill="both", expand=True)

        bottom = tk.Frame(chat)
        bottom.pack(fill="x")

        tk.Entry(bottom, textvariable=self.message).pack(side="left", fill="x", expand=True)
        tk.Button(bottom, text="Trimite", command=self.send_message).pack(side="left", padx=5)

        tk.Button(
            bottom,
            text="Trimite catre toti",
            command=self.send_message_all
        ).pack(side="left", padx=5)
        
        file_frame = tk.LabelFrame(self.root, text="Transfer fisier")
        file_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(file_frame, text="Alege fisier", command=self.choose_file).pack(side="left", padx=5)
        tk.Button(file_frame, text="Trimite fisier", command=self.send_file).pack(side="left", padx=5)

        tk.Button(
            file_frame,
            text="Trimite fisier catre toti",
            command=self.send_file_to_all
        ).pack(side="left", padx=5)
        
        self.progress = ttk.Progressbar(file_frame, length=300)
        self.progress.pack(side="left", padx=10)

    def log(self, msg):
        self.logs.put(msg)

    def process_logs(self):
        while not self.logs.empty():
            msg = self.logs.get()
            self.output.insert("end", msg + "\n")
            self.output.see("end")
        self.root.after(100, self.process_logs)

    def start_node(self):
        port = int(self.my_port.get())
        threading.Thread(
            target=start_server,
            args=(port, self.log),
            daemon=True
        ).start()
        self.log(f"[GUI] Nod pornit pe portul {port}")

    def connect_peer(self):
        peer = {
            "name": self.peer_name.get(),
            "ip": self.peer_ip.get(),
            "port": int(self.peer_port.get())
        }

        threading.Thread(
            target=connect_to_peer,
            args=(peer, self.connections, self.lock),
            daemon=True
        ).start()

        self.log(f"[GUI] Incerc conectarea la {peer['name']} {peer['ip']}:{peer['port']}")

    def send_message(self):
        msg = self.message.get().strip()
        if not msg:
            return

        send_to(
            self.peer_name.get(),
            msg,
            self.my_name.get(),
            self.connections,
            self.lock
        )

        self.log(f"[{self.my_name.get()}] {msg}")
        self.message.set("")

    def choose_file(self):
        self.selected_file = filedialog.askopenfilename()
        if self.selected_file:
            self.log(f"[GUI] Fisier selectat: {self.selected_file}")

    def send_file(self):
        if not self.selected_file:
            messagebox.showwarning("Atentie", "Alege mai intai un fisier.")
            return

        peer_name = self.peer_name.get()

        with self.lock:
            peer_data = self.connections.get(peer_name)

        if not peer_data:
            messagebox.showerror("Eroare", "Peer-ul nu este conectat.")
            return

        def worker():
            sock = peer_data["socket"]
            p = peer_data["p"]
            s = peer_data["s"]

            self.root.after(0, lambda: self.progress.config(value=0))

            def update_progress(current, total):
                self.root.after(0, lambda: self.progress.config(maximum=total, value=current))
                self.log(f"[GUI] Pachet trimis: {current}/{total}")

            send_file_segmented(
                sock,
                self.selected_file,
                p,
                s,
                encrypt_bytes,
                update_progress
            )

            self.log("[GUI] Fisier trimis.")

        threading.Thread(target=worker, daemon=True).start()

    def send_message_all(self):
        msg = self.message.get().strip()

        if not msg:
            return

        send_to_all(
            msg,
            self.my_name.get(),
            self.connections,
            self.lock
        )

        self.log(f"[{self.my_name.get()} -> ALL] {msg}")
        self.message.set("")

    def send_file_to_all(self):
        if not self.selected_file:
            messagebox.showwarning("Atentie", "Alege mai intai un fisier.")
            return

        with self.lock:
            peers = list(self.connections.items())

        if not peers:
            messagebox.showerror("Eroare", "Nu exista peers conectati.")
            return

        def worker(peer_name, peer_data):
            sock = peer_data["socket"]
            p = peer_data["p"]
            s = peer_data["s"]

            self.log(f"[GUI] Incep trimiterea fisierului catre {peer_name}")

            def update_progress(current, total):
                self.log(f"[GUI] {peer_name}: pachet trimis {current}/{total}")

            send_file_segmented(
                sock,
                self.selected_file,
                p,
                s,
                encrypt_bytes,
                update_progress
            )

            self.log(f"[GUI] Fisier trimis catre {peer_name}")

        for peer_name, peer_data in peers:
            threading.Thread(
                target=worker,
                args=(peer_name, peer_data),
                daemon=True
            ).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = P2PInterface(root)
    root.mainloop()