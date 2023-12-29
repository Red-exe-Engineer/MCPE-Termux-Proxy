# MCPE-Termux-Proxy
Creates a proxy to allow for joining MCPI/MCPE 0.6.1 servers using localhost

Borrowed the Proxy class from here: https://github.com/MCPI-Revival/proxy

### Installing
First, you need to install [Termux](https://github.com/termux/termux-app).
Next, run the following commands:
```sh
$ pkg install python wget
$ wget https://raw.githubusercontent.com/Red-exe-Engineer/MCPE-Termux-Proxy/main/mcpe-termux-proxy.py
$ chmod +x mcpe-termux-proxy
$ mv mcpe-termux-proxy ~/../usr/bin/
```
Then you can just run the `mcpe-termux-proxy` command to start whenever it's needed!

### Adding a server
Servers are stored in the `~/.mcpe-servers.json` file, if you don't want to figure out how it works just run the program and select `[New]`, then enter the server address, port, and display name.

### Where to find servers
Join the [MCPI-Revival Discord](https://discord.com/invite/aDqejQGMMy) and check the #mcpi-servers channel.
> Quick reminder that you must be 13+ to use Discord!
