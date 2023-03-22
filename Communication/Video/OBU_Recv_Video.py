# -*- coding: UTF-8 -*-
import sys

import cv2
import struct
import socket
import numpy as np
import threading
import gc
from queue import Queue

IP_ADDRESS = '192.168.62.117'
PORT = 30301
PACKETUNIT = 2850
WIDTH = 640
HEIGHT = 480


def print_log(is_error: bool = False, content: str = " "):
    content = content + '\n'
    if is_error:
        sys.stderr.write(content)
    else:
        sys.stdout.write(content)


def display(end_event, data):
    # 显示图像
    cv2.imshow('V2V See Through', data)
    if cv2.waitKey(1) == 27:  # 按下ESC键盘退出
        cv2.destroyAllWindows()
        end_event.set()


def receive(sock, queue: Queue, end_event: threading.Event):
    image_total = b''
    img_packet_dict = {}
    total_size = 0
    while not end_event.is_set():
        try:
            data, addr = sock.recvfrom(PACKETUNIT)
        except Exception:
            print_log(content='Recv timeout')
            raise IOError
        else:
            fhead_size = struct.unpack('i', data[:4])[0]
            count = struct.unpack('i', data[4:8])[0]
            img_packet = data[8:]
            img_packet_dict[count] = img_packet
            recvd_size = len(img_packet)
            total_size += recvd_size
            print_log(content=f'Fhead:{fhead_size}, Count:{count}, Recv:{recvd_size}, SumRecv:{total_size}')
            # count 为 表示收到最后一个包，发送方包从1开始计数， 计数0表示最后一个包
            if count == 0:
                # 没有丢包， 将数据包重组为图片，放进展示队列
                if total_size == fhead_size:
                    end_packet = img_packet_dict[count]
                    del img_packet_dict[count]
                    for i in sorted(img_packet_dict):
                        image_total += img_packet_dict[i]
                    image_total += end_packet
                    nparr = np.frombuffer(image_total, np.uint8)
                    img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    print_log(content='Add a new frame')
                    queue.put(img_decode)
                    image_total = b''
                    img_packet_dict.clear()
                    total_size = 0
                    gc.collect()
                else:  # 说明有丢包，丢弃前面接收的所有数据包，该图片包不完整
                    image_total = b''
                    img_packet_dict.clear()
                    total_size = 0


def display_thread_wrapper(queue: Queue, end_event: threading.Event, wait_timeout: int, total_timeout: int):
    total_wait_time = 0
    cv2.namedWindow('V2V See Through', cv2.WINDOW_NORMAL)
    black_bg = np.zeros((HEIGHT, WIDTH))
    while not end_event.is_set():
        if total_wait_time >= total_timeout:
            print_log(is_error=True, content='Display wait timeout, quit!')
            break
        try:
            data = queue.get(block=True, timeout=wait_timeout)
        except Exception:
            print_log(content='No data in display queue\n')
            display(end_event, black_bg)
            total_wait_time += wait_timeout
        else:
            # display
            display(end_event, data)
            total_wait_time = 0
    print_log(content='Display thread quit')


def receive_thread_wrapper(queue: Queue, end_event: threading.Event, timeout: int, total_timeout: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_ADDRESS, PORT))
    sock.settimeout(timeout)
    print("Bind Up on 30301")
    print('Start Receiving ...')

    total_wait_time = 0
    while not end_event.is_set():
        if total_wait_time >= total_timeout:
            print_log(is_error=True, content='Receive wait timeout, quit!')
            break
        try:
            receive(sock, queue, end_event)
        except IOError:
            total_wait_time += timeout
        else:
            total_wait_time = 0

    sock.close()
    print_log(content='Receive thread quit')


def main_thread():
    timeout = 1  # 阻塞线程秒数
    max_wait_time = 100
    kill_event = threading.Event()
    display_queue = Queue()
    display_thread = threading.Thread(target=display_thread_wrapper,
                                      args=(display_queue, kill_event, timeout, timeout * max_wait_time))
    receive_thread = threading.Thread(target=receive_thread_wrapper,
                                      args=(display_queue, kill_event, timeout, timeout * max_wait_time))

    receive_thread.start()
    display_thread.start()

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        kill_event.set()

    display_thread.join()
    receive_thread.join()


if __name__ == '__main__':
    print('''Receiving Start, Press 'ESC' to  Quit''')
    main_thread()
