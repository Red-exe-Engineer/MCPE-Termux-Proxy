#!/usr/bin/env python3

"""
    Created by Red-exe-Engineer.
    Proxy class modified from https://github.com/MCPI-Revival/proxy.
"""
import threading, socket, struct
import json, time, sys, os
import termios, tty


SERVERS = os.environ["HOME"] + "/.mcpe-servers.json"


class Proxy:
    def __init__(self, src_addr, src_port=None, dst_port=None):
        self.__options = {"src_addr": src_addr, "src_port": src_port or 19132, "dst_port": dst_port or 19133}
        self.__running_lock = threading.Lock()
        self.__running = 0
        self.exit = None

    def get_options(self):
        return self.__options

    def run(self):
        self.__running_lock.acquire()
        self.__running += 1
        self.__running_lock.release()

        dst_addr = ("0.0.0.0", self.__options["dst_port"])

        try:
            proc_addr = socket.gethostbyname_ex(self.__options["src_addr"])[2][0]
        except Exception as error:
            self.exit = str(error)
            return

        self.exit = 0

        src_addr = (proc_addr, self.__options["src_port"])
        client_addr = None

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__socket.bind(dst_addr)
        self.__socket.setblocking(False)

        self.running = True

        while self.running:
            self.__running_lock.acquire()
            cond = self.__running < 1
            self.__running_lock.release()

            if cond:
                break

            try:
                data, addr = self.__socket.recvfrom(4096)
                if data[0:1] == b'\x1c':

                    data = data.replace(
                        data[33:35],
                        struct.pack(
                            "!h",
                            struct.unpack("!h", data[33:35])[0] + 8,
                        ),
                    )

                    data += b' (Proxy)'

                if addr == src_addr:
                    self.__socket.sendto(data, client_addr)
                else:
                    if client_addr is None or client_addr[0] == addr[0]:
                        client_addr = addr
                        self.__socket.sendto(data, src_addr)
            except:
                pass

        self.__socket.close()

    def stop(self):
        self.__running_lock.acquire()
        self.__running -= 1
        self.__running_lock.release()


def getch() -> str:
    keys = {"A": "<up>", "B": "<down>"}

    fd = sys.stdin.fileno()
    settings = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, settings)

    if char == "\x1b":
        if (check := getch()) != "[":
            return check

        return keys.get(getch(), "")

    return char


def load_servers() -> dict:
    if not os.path.exists(SERVERS):
        save_servers({})

    try:
        with open(SERVERS, "r") as file:
            return json.load(file)
    except Exception as error:
        print("Unable to load servers:", str(error))
        return {}

def save_servers(servers):
    with open(SERVERS, "w") as file:
        json.dump(servers, file, indent=4)


def new_server() -> tuple[str, str, int] | None:
    def get_string(stage: int, prompt: str, default: str="", valid_keys: str="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&'()*+,-./:;<=>?@\\^_\" "):
        stage_string = " ".join(stages).replace(stages[stage], f'\x1b[1m{stages[stage].upper()}\x1b[0m')
        print(f'[{stage + 1}/3] {stage_string}\n> {stages[stage].title()} {default}', end="", flush=True)
        string = default

        while True:
            key = getch()

            if key in valid_keys and valid_keys:
                string += key
                print(key, end="", flush=True)

            elif key == "\x7f" and string:
                string = string[:-1]
                print("\x1b[1D\x1b[0K", end="", flush=True)

            elif key in "\n\r":
                print("\x1b[2K\x1b[1A\x1b[2K", end="\r")
                return string

    stages = ("address", "port", "name")

    addr = get_string(0, "Address: ")
    port = int(get_string(1, "Port: ", "19132", "1234567890"))
    name = get_string(2, "Name: ", addr)

    print(f'> \x1b[1m{name}\x1b[0m [{addr}:{port}]\nThis right? [y/n] ', end="", flush=True)

    while True:
        key = getch().lower()

        if key in "yn":
            print("\x1b[2K\x1b[1A\x1b[2K", end="\r")
            return (None, (name, addr, port))[key == "y"]


def connect(name, ip, port):
    print(f'Connecting to \x1b[1m{name}\x1b[0m... ', end="", flush=True)

    proxy = Proxy(ip, port, 19132)
    (thread := threading.Thread(target=proxy.run)).start()

    while proxy.exit is None:
        time.sleep(1)

    if proxy.exit:
        print(proxy.exit)
    else:
        print(f'\x1b[2K\rConnected to \x1b[1m{name}\x1b[0m')

    print("Press enter to return ", end="", flush=True)

    while True:
        if getch() in "\n\r":
            break

    print("\x1b[2K\x1b[1A\x1b[2K", end="\r")

    proxy.running = False
    proxy.stop()
    thread.join()


def menu(name: str="Menu", *options) -> str:
    index = 0

    for option in (name, "",) + options[1:]:
        print(" " + option)

    print(f'\x1b[{len(options)}A> \x1b[1m{options[0]}\x1b[0m', end="", flush=True)

    while True:
        key = getch()
        old = index

        if key in list(" \r\n"):
            print("\n" * (len(options) - index), "\x1b[1A\x1b[2K" * (len(options) + 1), sep="", end="\r")
            return options[index]

        elif key == "<up>":
            index = max(0, index - 1)

        elif key == "<down>":
            index = min(len(options) - 1, index + 1)

        if index != old:
            print("\r\x1b[2K " + options[old] + "\x1b[1" + "AB"[int(index > old)], f'\r> \x1b[1m{options[index]}\x1b[0m', end="", flush=True)


def main():
    servers = load_servers()

    while True:
        option = menu("- SERVERS -", *servers.keys(), "[NEW]", "[EXIT]")

        if option in servers:
            action = menu(f'- {option.upper()} -', "Connect", "Delete", "Back")

            if action == "Connect":
                connect(option, *servers[option])
            elif action == "Delete":
                print(f'Deleting \x1b[1m{option}\x1b[0m ({servers[option][0]}:{servers[option][1]})')

                if input(f'Type server name to confirm: ').strip() != option:
                    continue

                del servers[option]
                save_servers(servers)

                print("\x1b[1A\x1b[2K" * 2, end="", flush=True)

        elif option == "[NEW]":
            if not (server := new_server()):
                continue

            servers[server[0]] = server[1:]
            save_servers(servers)

        elif option == "[EXIT]":
            break


if __name__ == "__main__":
    main()
