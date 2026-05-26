# Encrypted P2P File Transfer

Aplicație distribuită de comunicare criptată între stații, realizată în Python. Proiectul permite transmiterea de mesaje și fișiere criptate într-o topologie P2P mesh, folosind socket-uri TCP, Diffie-Hellman pentru negocierea cheii și Blowfish-CBC pentru criptarea datelor.

## Funcționalități

- Comunicare directă între stații prin socket TCP
- Topologie P2P mesh cu 2-5 stații
- Fiecare nod are rol dublu: server TCP și client TCP
- Negociere de cheie folosind Diffie-Hellman
- Criptare simetrică folosind Blowfish implementat manual
- Mod de operare Blowfish-CBC cu IV random de 8 bytes
- Padding PKCS#7 pentru blocuri de 8 bytes
- Trimitere mesaje criptate către un peer
- Trimitere mesaje criptate către toți peerii conectați
- Trimitere fișiere criptate către un peer
- Trimitere fișiere criptate către toți peerii conectați
- Împărțirea fișierelor în chunks de 4096 bytes
- Reconstruirea fișierului la recepție
- Interfață grafică realizată cu Tkinter
- Teste pentru Blowfish și Blowfish-CBC

## Arhitectură

Proiectul folosește o arhitectură P2P descentralizată de tip mesh. Nu există un server central care rutează toate mesajele. Fiecare stație rulează propria componentă de server, pentru a primi conexiuni, și propria componentă de client, pentru a se conecta la celelalte stații.

Exemplu de topologie mesh cu 4 stații:

```text
+-----------+---------+-----------+
| Laptop A  |---------| Laptop B  |
| port 5555 |         | port 5556 |
+-----------+---------+-----------+
      |   \             /   |
      |    \           /    |
      |     \         /     |
      |      \       /      |
+-----------+---------+-----------+
| Laptop C  |---------| Laptop D  |
| port 5557 |         | port 5558 |
+-----------+---------+-----------+
```

Pentru 4 stații, un mesh complet are 6 conexiuni logice:

```text
Laptop A <-> Laptop B
Laptop A <-> Laptop C
Laptop A <-> Laptop D
Laptop B <-> Laptop C
Laptop B <-> Laptop D
Laptop C <-> Laptop D
```

Fiecare conexiune directă negociază propria cheie Diffie-Hellman și folosește propria cheie simetrică Blowfish.

## Fluxul aplicației

```text
1. Se pornește nodul local pe un port TCP.
2. Nodul se conectează la unul sau mai mulți peers.
3. Pentru fiecare conexiune se execută Diffie-Hellman.
4. Secretul comun este folosit pentru cheia Blowfish.
5. Mesajele și fișierele sunt criptate cu Blowfish-CBC.
6. Datele sunt trimise prin protocolul propriu peste TCP.
7. Receptorul decriptează mesajele sau reconstruiește fișierele.
```

## Criptare

Algoritmul simetric folosit este Blowfish, implementat manual, fără biblioteci externe de criptografie.

Blowfish lucrează pe blocuri de 64 de biți, adică 8 bytes. Pentru mesaje și fișiere de dimensiune variabilă, proiectul folosește modul CBC:

```text
plaintext -> padding PKCS#7 -> IV random -> Blowfish-CBC -> IV + ciphertext
```

La decriptare:

```text
IV + ciphertext -> Blowfish-CBC decrypt -> eliminare padding -> plaintext
```

Pentru fiecare mesaj sau chunk de fișier se generează un IV random de 8 bytes. IV-ul este atașat la începutul datelor criptate și este folosit la decriptare.

## Protocol peste TCP

TCP este orientat pe flux de bytes, deci nu păstrează automat granițele mesajelor. Din acest motiv, proiectul folosește un protocol propriu de framing.

Formatul general al unui pachet este:

```text
[4 bytes header_len][header_json][4 bytes payload_len][payload]
```

Header-ul conține informații precum tipul pachetului, iar payload-ul conține datele efective.

Tipuri de pachete folosite:

- `MESSAGE` - mesaj text criptat
- `FILE_START` - începutul transferului de fișier
- `FILE_CHUNK` - chunk criptat din fișier
- `FILE_END` - finalul transferului de fișier

## Transfer de fișiere

Fișierele sunt citite în chunks de 4096 bytes. Fiecare chunk este criptat și trimis separat.

Formula pentru numărul de pachete:

```text
numar_pachete = ceil(dimensiune_fisier / 4096)
```

Exemplu:

```text
Fisier: test.txt
Dimensiune: 7263 bytes
Chunk size: 4096 bytes
Numar pachete = ceil(7263 / 4096) = 2
```

La recepție, fiecare chunk este decriptat și scris secvențial în fișierul reconstruit.

## Structura proiectului

```text
Encrypted-P2P-File-Transfer/
├── blowfish.py          # Implementare Blowfish + Blowfish-CBC
├── client.py            # Conectare la peers si trimitere mesaje
├── constants.py         # Constante Blowfish
├── diffie_hellman.py    # Implementare Diffie-Hellman
├── gui.py               # Interfata grafica Tkinter
├── main.py              # Punct alternativ de pornire
├── node_a.py            # Test/demo consola pentru nod A
├── node_b.py            # Test/demo consola pentru nod B
├── p2p_utils.py         # Transfer fisiere pe chunks
├── protocol.py          # Protocol de framing peste TCP
├── server.py            # Server TCP pentru receptie
├── test_cbc.py          # Test simplu pentru Blowfish-CBC
├── test.txt             # Fisier de test
└── tests/
    └── test_blowfish.py # Teste unitare Blowfish
```

## Rulare

### 1. Clonează repository-ul

```bash
git clone https://github.com/AndreeaStati/Encrypted-P2P-File-Transfer.git
cd Encrypted-P2P-File-Transfer
```

### 2. Rulează aplicația GUI

```bash
python3 gui.py
```

Pentru un demo local cu două stații, deschide două terminale și rulează în fiecare:

```bash
python3 gui.py
```

Configurare exemplu:

Stația 1:

```text
Nume: Laptop A
Port local: 5555
Peer name: Laptop B
Peer IP: 127.0.0.1
Peer port: 5556
```

Stația 2:

```text
Nume: Laptop B
Port local: 5556
Peer name: Laptop A
Peer IP: 127.0.0.1
Peer port: 5555
```

Pași:

1. Apasă `Pornește nod` pe fiecare stație.
2. Apasă `Conectează` către peer.
3. Trimite mesaje sau fișiere criptate.

## Demo mesh cu 4 stații

Pentru test local, se pot porni 4 instanțe ale aplicației:

```text
Laptop A - port 5555
Laptop B - port 5556
Laptop C - port 5557
Laptop D - port 5558
```

Toate folosesc IP-ul:

```text
127.0.0.1
```

Fiecare stație se poate conecta la celelalte stații prin introducerea numelui, IP-ului și portului peer-ului.

Exemplu pentru Laptop A:

```text
Laptop B - 127.0.0.1 - 5556
Laptop C - 127.0.0.1 - 5557
Laptop D - 127.0.0.1 - 5558
```

După conectare, se poate folosi:

- `Trimite` pentru mesaj către peer-ul selectat
- `Trimite către toți` pentru mesaj către toți peerii conectați
- `Trimite fișier` pentru fișier către peer-ul selectat
- `Trimite fișier către toți` pentru fișier către toți peerii conectați

## Testare

### Test Blowfish-CBC

```bash
python3 test_cbc.py
```

Rezultat așteptat:

```text
Test CBC reusit.
```

### Teste unitare

```bash
python3 -m unittest discover -s tests -v
```

### Verificare fișier primit

După transfer, se poate verifica dacă fișierul primit este identic cu cel original:

```bash
sha256sum test.txt primit_test.txt
```

Dacă hash-urile sunt identice, fișierul a fost transmis, decriptat și reconstruit corect.

## Observații

- Proiectul este realizat pentru scop educațional.
- Nu folosește biblioteci externe de criptografie.
- Blowfish este implementat manual.
- Comunicarea dintre stații se face prin socket TCP.
- În modul local, toate stațiile pot rula pe același laptop, folosind porturi diferite.
- Într-o rețea LAN, fiecare stație folosește IP-ul real al celorlalte stații.

## Limitări și îmbunătățiri posibile

- Autentificare cu username și parolă pentru fiecare peer
- Evitarea conexiunilor duplicate între aceleași două stații
- Salvarea fișierelor primite în directoare separate pentru fiecare nod
- Trimiterea payload-ului binar direct, fără conversie hex în JSON
- Adăugarea unui mecanism HMAC pentru verificarea integrității mesajelor
- Descoperirea automată a stațiilor din rețea
- Suport pentru configurare din fișier

## Tehnologii folosite

- Python 3
- Socket TCP
- Threading
- Tkinter
- Diffie-Hellman
- Blowfish-CBC
- JSON
- Base64
