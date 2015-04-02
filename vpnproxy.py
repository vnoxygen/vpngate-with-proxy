#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'duc_tin'

import os
import re
import requests
import base64
from subprocess import call, check_output, CalledProcessError, Popen
import time
import datetime
import sys


# proxy server and port
proxy = '133.44.62.220'
port = '8080'

proxies = {
    'http': 'http://' + proxy + ':' + port,
    'https': 'http://' + proxy + ':' + port,
}


class Server():
    dns_leak_stop = 'script-security 2\r\nup update-resolv-conf.sh\r\ndown update-resolv-conf.sh\r\n'

    def __init__(self, data):
        self.ip = data[1]
        self.score = data[2]
        self.ping = int(data[3]) if data[3]!='-' else 'inf'
        self.speed = int(data[4])
        self.country = data[6]
        self.NumSessions = data[7]
        self.uptime = data[8]
        self.logPolicy = data[11]
        self.config_data = data[-1]

    def write_file(self):
        txt_data = base64.b64decode(self.config_data)
        add_proxy = txt_data.replace('\r\n;http-proxy-retry\r\n', '\r\nhttp-proxy-retry 5\r\n')
        added_proxy = add_proxy.replace('\r\n;http-proxy [proxy server] [proxy port]\r\n',
                                        '\r\nhttp-proxy %s %s\r\n' % (proxy, port))
        dns_fixed = added_proxy + Server.dns_leak_stop
        tmp_vpn = open('vpn_tmp', 'w+')
        tmp_vpn.write(dns_fixed)
        return tmp_vpn

    def __str__(self):
        speed = self.speed/1000.**2
        uptime = datetime.timedelta(milliseconds=int(self.uptime))
        uptime = re.split(',|\.', str(uptime))[0]
        return '\t  %s\t  %s ms    %.2f Mbps\t  %s\t %s'\
               % (self.country, self.ping, speed, uptime.ljust(7), self.logPolicy)


def get_data():
    try:
        vpn_data = requests.get('http://www.vpngate.net/api/iphone/', proxies=proxies).text.replace('\r', '')
        servers = [line.split(',') for line in vpn_data.split('\n')]
        labels = servers[1]
        labels[0] = labels[0][1:]
        servers = {s[0]: Server(s) for s in servers[2:] if len(s) > 1}
        return servers
    except:
        print 'Failed to get VPN servers data\nCheck your network setting and proxy'

vpn_list = get_data()
ranked = sorted(vpn_list.keys(), key=lambda x: vpn_list[x].speed, reverse=True)

while True:
    print 'Index\t Country   Ping\t    Speed\t Up Time\t  Log Policy'
    for index, key in enumerate(ranked[:20]):
        print index, ':', vpn_list[key]
    try:
        user_input = raw_input('Choose vpn No.: ')
        if user_input in ['Q', 'q', 'quit', 'exit']:
            sys.exit()
        chose = int(user_input)
        print 'Connect to %s'.center(40) % vpn_list[ranked[chose]].ip
        vpn_file = vpn_list[ranked[chose]].write_file()
        vpn_file.close()
        call(['sudo', 'openvpn', '--config', os.path.abspath(vpn_file.name)])
    except KeyboardInterrupt:
        time.sleep(0.5)
        print "Select another VPN server or 'q' to quit"

# path to .ovpn containing folder
# path = '/home/duc_tin'
# ovpn = [fi for fi in os.listdir('/home/duc_tin') if fi[-4:] == 'ovpn']
# count = 0

# # add proxy and dns patch to ovpn file
# for fi in ovpn:
#     with open(path + '/' + fi, 'r+') as fvpn:
#         lines = fvpn.readlines()
#         if ';http-proxy-retry\r\n' in lines:
#             index1 = lines.index(';http-proxy-retry\r\n')
#             lines[index1] = 'http-proxy-retry 5\r\n'
#             lines[index1 + 1] = 'http-proxy 133.44.62.220 8080\r\n'
#             fvpn.seek(0)
#             fvpn.writelines(lines)
#             count += 1
#         if dns_leak_stop[0] not in lines:
#             fvpn.writelines(dns_leak_stop)
# print 'changed %s file(s)' % count

# sort ovpn file by modified time
# modtime = lambda x: time.ctime(os.path.getmtime(x))
# ovpn.sort(key=modtime, reverse=True)

# vpn_dict = dict(zip(range(len(alive)), [server for alv in alive for server in ovpn if alv in server]))
# vpn_dict = dict(zip(range(len(ovpn[:20])), ovpn[:20]))



# select ovpn to run
# while True:
#     for key in vpn_dict:
#         print key, ':', vpn_dict[key], 'available' if addr.findall(vpn_dict[key])[0] in alive else ''
#     try:
#         user_input = raw_input('Choose vpn No.: ')
#         if user_input in ['Q', 'q', 'quit', 'exit']:
#             sys.exit()
#         choose_vpn = int(user_input)
#         call(['sudo', 'openvpn', '--config', vpn_dict[choose_vpn]])
#     except KeyboardInterrupt:
#         time.sleep(0.5)
#         print 'Select another VPN server'