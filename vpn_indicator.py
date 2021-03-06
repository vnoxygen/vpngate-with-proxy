#!/usr/bin/env python 
# -*- coding: utf-8 -*-
__author__ = 'duc_tin'

from Queue import Empty, Queue
from threading import Thread
from subprocess import call
import select
import signal, os
import socket, errno
import time

try:
    from gi.repository import Gtk, GLib
    from gi.repository import AppIndicator3 as appindicator
    from gi.repository import Notify as notify
except ImportError:
    print 'Lack of Gtk related modules!'
    print 'VPN indicator will not run!'


class InfoServer:
    def __init__(self, port):
        self.host = 'localhost'
        self.port = port
        self.buffer = 2048  # buffer
        self.backlog = 1

        self.is_listening = False
        self.is_connected = False
        self.is_dead = False
        self.client = None

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_address = self.host, self.port

        self.last_msg = ''

        self.readlist = [self.sock]  # use for select

    def listen(self):
        try:
            self.sock.bind(self.server_address)
            self.sock.listen(self.backlog)
            print 'listening'

            return True
        except socket.errno, e:
            print e
            return False

    def check_io(self, q_info):
        """Receive information about vpn tunnel
            :type q_info: Queue
        """
        while True:

            # try to bind the socket
            while not self.is_listening:
                self.is_listening = self.listen()
                time.sleep(2)

            # normal select protocol
            readable, _, _ = select.select(self.readlist, [], [])
            for s in readable:
                if s is self.sock:

                    if self.is_dead:
                        print 'Server: Received dead signal'
                        self.sock.close()
                        return 0
                    else:
                        self.client, addrr = self.sock.accept()
                        self.readlist.append(self.client)
                        self.is_connected = True
                        print 'Server: Connected with %s:%s' % addrr
                        q_info.put('connected')

                else:  # client sent something
                    try:

                        data = self.client.recv(self.buffer)
                        if data:
                            print 'main sent: ', data
                        else:
                            self.is_connected = False
                            self.readlist.remove(self.client)
                            print 'main disconnected'

                        q_info.put(data)

                    except socket.error as e:
                        print 'Client die unexpectedly'
                        self.is_connected = False

    def send(self, msg):
        if msg == 'dead':
            self.is_dead = True
            self.sock.shutdown(socket.SHUT_RDWR)

        elif self.is_connected:
            try:
                self.client.sendall(msg)
                return True
            except socket.error:
                return False
        else:
            return False


class InfoClient:
    def __init__(self, port):
        self.host = 'localhost'
        self.port = port

        self.buffer = 2048  # buffer
        self.sock = socket.socket()
        self.server_address = self.host, port
        self.is_connected = False

        self.last_msg = ''

    def connect(self):
        while not self.is_connected:
            try:
                self.sock = socket.create_connection(self.server_address)
                # print 'socket: connected'
                self.is_connected = True

                # update current status
                if self.last_msg:
                    self.send(self.last_msg)

            except socket.error, e:
                # print str(e)
                time.sleep(2)

    def check_io(self, q_cmd):
        """Receive information about vpn tunnel
            :type q_cmd: Queue
        """
        while True:

            if self.is_connected:
                # check if there is cmd from indicator
                readable, _, _ = select.select([self.sock], [], [])
                try:

                    data = self.sock.recv(self.buffer)
                    if data:
                        # print data
                        q_cmd.put(data)
                    else:
                        self.is_connected = False
                        # print 'server die'

                except socket.error as e:
                    print 'Server die unexpectedly'
                    self.is_connected = False
            else:
                self.connect()

    def send(self, msg):
        self.last_msg = msg
        if self.is_connected:
            try:
                self.sock.sendall(msg)
                return True
            except socket.error:
                return False
        else:
            return False


class VPNIndicator:
    def __init__(self, q_info, sender):
        signal.signal(signal.SIGINT, self.handler)
        signal.signal(signal.SIGTERM, self.handler)

        # pipe for send/recv data to tcp server
        self.q_info = q_info
        self.send = sender

        self.APPINDICATOR_ID = 'myappindicator'
        self.icon1 = os.path.abspath('connected.svg')
        self.icon2 = os.path.abspath('connectnot.svg')
        self.icon345 = [os.path.abspath(icon) for icon in ['connecting1.svg','connecting2.svg','connecting3.svg']]
        self.hang = False
        self.is_connecting = False
        self.icon_th = 0

        self.last_recv = ['']
        self.indicator = appindicator.Indicator.new(self.APPINDICATOR_ID, self.icon2,
                                                    appindicator.IndicatorCategory.APPLICATION_STATUS)

        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        # Add menu to indicator
        self.indicator.set_menu(self.build_menu())

        self.notifier = notify.Notification.new('', '', None)
        self.notifier.set_timeout(2)

        notify.init(self.APPINDICATOR_ID)

    def run(self, *args):
        GLib.timeout_add(1000, self.callback, *args)
        GLib.timeout_add(700, self.blinking)
        Gtk.main()

    def blinking(self):
        if self.is_connecting:
            if self.icon_th == 3:
                self.icon_th = 0
            self.indicator.set_icon(self.icon345[self.icon_th])
            self.icon_th += 1
        return True

    def reload(self, data_in):
        if data_in:
            print data_in[:12]

            self.last_recv = data_in.split(';')
            if 'connecting' in data_in:
                print 'set blinking'
                self.is_connecting = True
            else:
                self.is_connecting = False

            if 'connected' in data_in:
                self.hang = False
                self.status('', self.last_recv)
            elif 'successfully' in data_in:
                self.indicator.set_icon(self.icon1)
                self.status('', self.last_recv)
            elif 'terminate' in data_in:
                self.indicator.set_icon(self.icon2)
                self.status('', ['terminate'])
            elif 'Offline' in data_in and not self.hang:
                self.indicator.set_icon(self.icon2)
                self.status('', ["Offline"])
                self.hang = True
            elif 'main exit' in data_in:
                self.quit()

        # return True

    def build_menu(self):
        menu = Gtk.Menu()

        # change focus to main program terminal
        focus_main = Gtk.MenuItem('Show main')
        focus_main.connect('activate', self.change_focus)
        menu.append(focus_main)

        menu.append(Gtk.SeparatorMenuItem())

        # show status popup
        current_status = Gtk.MenuItem('VPN Status')
        current_status.connect('activate', self.status, self.last_recv)
        menu.append(current_status)

        # connect to the next vpn on the list
        next_vpn = Gtk.MenuItem('Next VPN')
        next_vpn.connect('activate', self.send_cmd, 'next')
        menu.append(next_vpn)

        menu.append(Gtk.MenuItem())

        # connect to the next vpn on the list
        stop_vpn = Gtk.MenuItem('Stop VPN')
        stop_vpn.connect('activate', self.send_cmd, 'stop')
        menu.append(stop_vpn)

        menu.append(Gtk.SeparatorMenuItem())

        # quit button
        item_quit = Gtk.MenuItem('Quit indicator')
        item_quit.connect('activate', self.handler, '')
        menu.append(item_quit)

        menu.show_all()
        return menu

    def quit(self, source=None):
        # send dead signal to tcp server
        self.send('dead')
        notify.uninit()
        Gtk.main_quit()

    def change_focus(self, menu_obj):
        call(['wmctrl', '-a', 'vpngate-with-proxy'])

    def status(self, menu_obj, messages=''):
        """

        :type messages: list
        """

        if menu_obj:
            messages = self.last_recv

        self.notifier.close()

        if 'connected' in messages[0]:
            summary = 'Connected to main program'
            body = ''
        elif 'successfully' in messages[0]:
            print messages[1:]
            tags = ['Ping:', 'Speed:', 'Up time:', 'Season:', 'Log:', 'Score:', 'Protocol:', 'Portal:']
            msg = messages[1:3] + [item for items in zip(tags, messages[3:9]) for item in items]
            summary = 'VPN tunnel established'

            body = '''
            {:<20}{:<15}    {:>19} {:<15}
            {:<18} {:<8} Mbps
            {:<18}{:<15}   {:>20} {:<20}
            {:<22}{:<15}
            {:<21}{:<15}
            '''.format(*msg)
        elif 'terminate' in messages[0]:
            summary = 'VPN tunnel has broken'
            body = 'Please choose a different server and try again'
        elif 'Offline' in messages[0]:
            summary = 'VPN program is offline'
            body = "Click VPN indicator and choose 'Quit' to quit"
        else:
            summary = 'Status unknown'
            body = "Waiting for connection from main program"

        self.notifier.update(summary, body, icon=None)
        self.notifier.show()

    def handler(self, signal_num, frame):
        print 'Indicator: quit now'
        self.quit('')

    def send_cmd(self, menu_obj, arg):
        print 'Indicator sent:', arg
        self.send(arg)

    def callback(self):
        try:
            data = self.q_info.get_nowait()
            self.reload(data)
        except Empty:
            pass

        return True


if __name__ == '__main__':
    # queue for interacting between indicator and server
    q = Queue()

    server = InfoServer(8088)
    t = Thread(target=server.check_io, args=(q,))     # shouldn't be daemon
    t.start()

    indicator = VPNIndicator(q, server.send)
    indicator.run()
    t.join()
