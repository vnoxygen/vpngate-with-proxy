# vpngate-with-proxy
VPN GATE client for linux
* Be able to connect to open vpn servers at **http://www.vpngate.net/en/** directly or through proxy
* Auto add DNS to fix DNS leak.
* Auto filter out dead VPN servers. (updated on August 16th)

Work on debian based system. Tested on Ubuntu and Raspbian.

I will wrap SoftEther_vpn later when I have time. You are welcome to fork this repo and wrap SoftEther_vpn yourself.

**Indicator**: Tested on Ubuntu and is only enabled by default on Ubuntu. For other distro,
you can test it by *$ ./vpn_indicator.py* after launching *vpnproxy_tui.py*

![](http://s19.postimg.org/580s2qyo3/2connect_success.png)

# Dependency:
* **openvpn**: ```$ sudo apt-get install openvpn```
* **resolvconf**: ```$ sudo apt-get install resolvconf```   Only if you use the version in 'old' directory
* **python 2.7.x**: should already be shipped with your linux
* **python-requests**: ```$ sudo apt-get install python-requests```
* **python-urwid 1.3+**: ```$ sudo apt-get install python-urwid``` Only if you use `tui` version (terminal user interface)

Except *python 2.7.x*, all other dependencies should be automatically installed at first run.

# How to use:

### 0. Pre-installation
  * If you has just installed your os, please update your os for it to fetch packages list and know where to download
  other packages later.

  ```Shell
  $ sudo apt-get update && sudo apt-get upgrade
  ```
  If your network is behind a proxy
  ```Shell
    $ export http_proxy="http://your_proxy:your_port"
    $ export https_proxy="http://your_proxy:your_port"
    $ sudo -E apt-get update && sudo -E apt-get upgrade
  ```

  * Please check the os clock and calendar is correct for openvpn authentication works properly.

### 1. Installation:

  Using *git*:
  ```Shell
  $ sudo apt-get install git
  $ git clone https://github.com/Dragon2fly/vpngate-with-proxy.git
  ```
  
  If your network is behind a proxy:
  ```Shell
    $ export http_proxy="http://your_proxy:your_port"
    $ export https_proxy="https://your_proxy:your_port"
    $ sudo -E apt-get install git
    $ git clone https://github.com/Dragon2fly/vpngate-with-proxy.git
  ```
  
  **OR**
  
  Download: https://github.com/Dragon2fly/vpngate-with-proxy/archive/master.zip
  It contains the "vpngate-with-proxy" folder. Extract it into anywhere you want eg: `$HOME`.

### 2. First run:
  If you have configured **system wide proxy** or proxy in firefox, it'd better to **turn** it **off**. After vpn tunnel is established,
  the programs that use system wide proxy may failed to connect to the internet using your proxy.

  Launch vpngate-with-proxy by

  ```Shell
  $ cd vpngate-with-proxy
  $ ./vpnproxy_tui.py
  ```
  
  or 
  ```Shell
  $ cd vpngate-with-proxy
  $ ./vpnproxy_cli.py
  ```
  
   - **vpnproxy_tui.py** has better UI, colorful and easier to use.
   - **vpnproxy_cli.py** is normal terminal application, lightweight and is aim to run on server (RaspberryPi ?)

Then the program will first setup a configuration file `config.ini` by asking you for **proxy** if needed to 
connect to the Internet. After that it will show the default configuration of the program. 
Change any parameter to suit you and press **Enter** to continue. 
Next time launching this program, you won't see this configuration again. Either modify `config.ini` or check **5. Some notes**

  If no thing goes wrong, the vpn server's list will show up.

  ![](http://s19.postimg.org/qgegk6d4z/1startup.png)

### 3. Interaction:
  * Connect to a specific vpn server by typing its *index* number (eg: 11) and then Enter.
  If nothing went wrong, a `successfully` message show up.
  ![](http://s19.postimg.org/603g1y2v7/4oldandnew.png)

  * Your currently chosen server will be highlighted with `dark blue` color.
  * All connected servers before the current one is show in `dark red` color.
  * Change your desire setting by press the `F#` key corresponding to that setting. Hit that `F#` key again to discard all changes and close setting popup. Setting will only be saved when you hit `<OK>` or Enter.
    * **F2**: **Proxy**, use http proxy? address? port?
    * **F3**: **DNS**, change DNS when connecting to vpn? which dns to change to?
    * **F4**: **Country**, looking for a specific country or all that available?
    * **F5**: **Sort by**, sort these servers by what parameter?

   ![](http://s19.postimg.org/xtyfwvmkj/6menu.png)

  * **Vpn command**: As you mentioned above, give an index of the server then hit Enter will open a vpn tunnel from your to that server. And there are still some more.

    * **r**, **refresh**: fetch new server's data from vpngate.net or mirrors
    * **restore**: will restore your system DNS back to original one
    * **kill**: send SIGTERM to all `openvpn` processes
    * **q**: terminate vpn tunnel, then quit the program
    * **log**: check if current season is logged or not. Log file is `vpn.log` and is in the same folder with this program. Every time you start the program, log file is rewritten (old content will be lost) if `log` is turned on.
      * **log on**: turn on logging
      * **log off**: turn off logging

  * Other keys and combinations:
    * **Up, Down, PgUp, PgDown**: scroll the server list
    * **F10**      : toggle logging on/off
    * **Esc**      : clear the text in any input form (*vpn command*, *Proxy*, *Country*)
    * **Ctrl + F5**: the same as `r` or `refresh` *command*
    * **Ctrl + r** : the same as `restore` *command*
    * **Ctrl + k** : the same as `kill` *command*
    * **Ctrl + c** : if connected to vpn server, terminate vpn tunnel, turn back to normal state.
      Else, quit the program

### 4. After VPN Tunnel is established successfully:
  A successful connection doesn't mean you have access to the Internet. If you can access the Internet through selected vpn
server, that doesn't mean you are totally safe.
  1. _Check if you can access the Internet_:
    * try browse some websites. Low *score* VPN servers tend to block you out of the Internet  

  2. _Check DNS leak_:
  
   If you are serious about privacy, this is necessary. DNS server knows the web addresses that you connected to,
   unless you type IP address directly.

     To know your current DNS provider, https://www.dnsleaktest.com or https://ipleak.net

     * Turn on `DNS fix` by press `F3` before connecting to vpn server. Choose some good DNS from http://pcsupport.about.com/od/tipstricks/a/free-public-dns-servers.htm
     * Connect to any VPN server and test if your dns provider is changed.
  
  If DNS is not changed, make sure that you have turned off your system wide proxy and try again.
  While using the ethernet for vpn, connected to wifi may reset your DNS.  
  
You could also use below command in Ubuntu to see trace route:
  ```Shell
  $ mtr -rw google.com
  ```

### 5. Some notes:
  * To view or change settings before the program fetches server's list:
  ```Shell
  $ ./vpnproxy_tui.py config
  ```
  
  * (vpnproxy_cli.py only) To view or change settings at server's list: type *Vpn command* **c** or **config** then Enter

  * **Ctrl+z**: Try not to press this combination while program is running. It will not terminate the vpn tunnel nor kill the program properly.
   Which means iptable may be left messed up, DNS won't reset to original, you may be **still in vpn**.

  * The program only shows the last log line at the bottom of terminal. In fact, there is 20 last lines of the log.
   To view these lines, you just need to extend the high of the terminal window.
   ![log](http://s19.postimg.org/5c48tuzur/7loglines.png)
   The log is shown up side down so the latest information will be in the highest place

  * If your terminal looks weird after program crashed or `Ctrtl+z`, `$ reset` would help


# Troubleshoot:
  Symptom: The program is unable to fetch new server data nor connect to any vpn server, your networking is not back to normal.

  That is when `restore`, `kill` and `log on` *command* come in handy.

  1. **kill** all openvpn processes
  2. **quit** the program and launch it again. If it can fetch the server data, OK.

  If it doesn't
  3. `sudo iptables -F` to delete all changes to the iptable, then `$ sudo service network-manager restart`
  and do step 2 again.

  Restart your system or reconnect to wifi or ethernet will also help.
  If it still doesn't, your proxy may be offline or `\etc\resolv.conf`'s content is incorrect.
  Ping your proxy from another computer to test. And double check `\etc\resolv.conf`
  
  If your network is behind a proxy, although the program has limited the number of socket connection per second,
  there is a chance that your ip will be blocked because of spamming too many socket connection 
  (to test if OpenVPN servers are still alive) during a short time, in other words, DDoS your proxy. 
  Search in the source code for **test_interval** and increase it a little bit. 