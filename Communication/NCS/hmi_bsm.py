# -*- coding: utf-8 -*-

from socket import *
import json
import config
import datetime


def hmi_control_tag(hmi_socket, dst, tag):
    hmi_socket.sendto(bytes(tag.encode('UTF-8')), dst)


def obu_ncs_msg(hmi_socket, file):
    record_count = 1
    print('Start Recording BSM...')
    while record_count <= 100:
        data, addr = hmi_socket.recvfrom(1024)
        if len(data) == 0:
            break
        time_start = datetime.datetime.now()
        file.write(str(time_start) + '\n')
        bsm_str = str(data, 'utf-8')
        file.write(bsm_str + '\n')
        if record_count % 20 == 0:
            print("{} BSM have been record!".format(record_count))
        record_count += 1


if __name__ == '__main__':
    # initial configuration
    hmi_ip_port = (config.read_config('hmi', key='ip'), int(config.read_config('hmi', key='port')))
    obu_ip_port = (config.read_config('obu', key='ip'), int(config.read_config('obu', key='port')))
    register = config.read_config('request', key='register')
    activator = config.read_config('request', key='activate')
    deactivator = config.read_config('request', key='deactivate')

    # communication module
    hmi_udp = socket(AF_INET, SOCK_DGRAM)
    hmi_udp.bind(hmi_ip_port)
    print('Bind UDP on {}'.format(hmi_ip_port[1]))

    print('Send Register Request...')
    hmi_control_tag(hmi_udp, obu_ip_port, register)
    with open("log/bsm_3.txt", 'a') as f:
        obu_ncs_msg(hmi_udp, f)
        hmi_control_tag(hmi_udp, obu_ip_port, deactivator)
        f.close()
    print('End Recording BSM!')
