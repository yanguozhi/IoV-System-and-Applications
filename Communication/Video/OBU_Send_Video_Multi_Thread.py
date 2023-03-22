# -*- coding: UTF-8 -*-
# This is a sample Python script.
import copy
import socket
import struct
import sys
import threading
import time

import cv2
# import keyboard
from queue import Queue

import numpy as np
import pyrealsense2 as rs


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

IP_ADDRESS = '192.168.62.199'
PORT = 30300
PACKET_SIZE = 2842
WIDTH = 640
HEIGHT = 480
FPS = 30


def print_log(is_error: bool = False, content: str = ""):
    print(content)
    return
    content = content + '\n'
    if is_error:
        sys.stderr.write(content)
    else:
        sys.stdout.write(content)


def display(end_event, data):
    # print_log(content='display new data:' + str(data))
    # 显示图像
    cv2.imshow("V2V See Through", data)
    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        end_event.set()


def transmit(sock, data):
    # print_log(content='transmit new data:' + str(data))
    encoded_image = cv2.imencode('.jpg', data)[1].tobytes()
    # 将图像分包传输到指定的 IP 地址和端口号
    data_length = len(encoded_image)
    packets = [encoded_image[i: i + PACKET_SIZE] for i in range(0, data_length, PACKET_SIZE)]
    for index, packet in enumerate(packets):
        # 为每个包添加包头， 每个包格式为： 图片总长度+包序列号+数据包内容
        send_data = struct.pack('i', data_length) + struct.pack('i', index) + packet
        sock.sendto(send_data, (IP_ADDRESS, PORT))
        time.sleep(0.001)


def display_thread_wrapper(queue: Queue, end_event: threading.Event, wait_timeout: int, total_timeout: int):
    total_wait_time = 0
    cv2.namedWindow('V2V See Through', cv2.WINDOW_AUTOSIZE)
    while not end_event.is_set():
        if total_wait_time >= total_timeout:
            print_log(is_error=True, content='display wait timeout, quit!')
            break
        try:
            data = queue.get(block=True, timeout=wait_timeout)
        except Exception:
            print_log(content='no data in display queue\n')
            total_wait_time += wait_timeout
        else:
            # display
            display(end_event, data)
            total_wait_time = 0
    print_log(content='display thread quit')


def transmit_thread_wrapper(queue: Queue, end_event: threading.Event, wait_timeout: int, total_timeout: int):
    total_wait_time = 0
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not end_event.is_set():
        if total_wait_time >= total_timeout:
            print_log(is_error=True, content='transmit wait timeout, quit!')
            break

        try:
            data = queue.get(block=True, timeout=wait_timeout)
        except Exception:
            print_log(content='no data in transmit queue')
            total_wait_time += wait_timeout
        else:
            # transmit
            transmit(sock, data)
            total_wait_time = 0
    sock.close()
    print_log(content='transmit thread quit')


def test_multi_thread():
    # 配置RealSense相机
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)

    # 启动 RealSense 相机
    pipeline.start(config)

    timeout = 2
    max_wait_time = 5
    kill_event = threading.Event()
    display_queue, transmit_queue = Queue(), Queue()

    display_thread = threading.Thread(target=display_thread_wrapper,
                                      args=(display_queue, kill_event, timeout, timeout * max_wait_time))
    transmit_thread = threading.Thread(target=transmit_thread_wrapper,
                                       args=(transmit_queue, kill_event, timeout, timeout * max_wait_time))
    display_thread.start()
    transmit_thread.start()

    while not kill_event.is_set():
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        print_log(content='received new frame')
        # 将帧转换为 OpenCV 图像
        frame = (np.asanyarray(color_frame.get_data()))

        display_queue.put(copy.deepcopy(frame))
        transmit_queue.put(copy.deepcopy(frame))
        time.sleep(0.1)

    display_thread.join()
    transmit_thread.join()

    # 关闭 RealSense 相机和 socket
    pipeline.stop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test_multi_thread()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
