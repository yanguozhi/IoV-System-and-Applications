# -*- coding: UTF-8 -*-
import socket
import struct
import time

import cv2
import numpy as np
import pyrealsense2 as rs

IP_ADDRESS = '192.168.62.199'
PORT = 30300
PACKET_UNIT = 2842
WIDTH = 1280
HEIGHT = 720
FPS = 30


def udp_send(image, socket_process):
    """
    :param image: 要发送的图片数据
    :param socket_process: socket连接
    :return:
    """
    encoded_image = cv2.imencode('.jpg', image)[1].tobytes()
    # 将图像分包传输到指定的 IP 地址和端口号
    data_length = len(encoded_image)
    packets = [encoded_image[i: i + PACKET_UNIT] for i in range(0, data_length, PACKET_UNIT)]
    for index, packet in enumerate(packets):
        # 包计数从1开始，将最后一个包的count置为0，设为标志位
        index += 1
        if packet == packets[-1]:
            # 为最后一个包添加结束标志位， 包格式为： 包总长+0+数据包内容
            send_data = struct.pack('i', data_length) + struct.pack('i', 0) + packet
            socket_process.sendto(send_data, (IP_ADDRESS, PORT))
        else:
            # 为每个包添加包头， 每个包格式为： 图片总长度+包序列号+数据包内容
            send_data = struct.pack('i', data_length) + struct.pack('i', index) + packet
            socket_process.sendto(send_data, (IP_ADDRESS, PORT))
            time.sleep(0.001)


if __name__ == '__main__':
    print("Start Initializing Socket Process")
    # 创建UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Start Initializing Video Camera")
    # 配置RealSense相机
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)

    # 启动 RealSense 相机
    pipeline.start(config)
    cv2.namedWindow('V2V See Through', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('V2V See Through', WIDTH, HEIGHT)
    while True:

        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        # 将帧转换为 OpenCV 图像
        frame_image = np.asanyarray(color_frame.get_data())
        cv2.imshow('V2V See Through', frame_image)
        udp_send(frame_image, sock)
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key == 27:
            cv2.destroyAllWindows()
            break

    # 关闭 RealSense 相机和 socket
    pipeline.stop()
    sock.close()

