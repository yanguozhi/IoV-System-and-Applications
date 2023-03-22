# coding=utf-8
import socket
import struct
import datetime
import time

import cv2

IP_ADDRESS = '192.168.62.199'
PORT = 30300
PACKET_UNIT = 2842  # 最大为2850，每个包包头有8个字节：包长+包序号


def image_resize(image, size):
    """
    : param image: 图片路径
    : param size: 缩放后的尺寸，（0，0）表示不缩放
    : return: 图片数据，np_array
    """
    img = cv2.imread(image)
    if size == (0, 0):
        return img
    else:
        img = cv2.resize(img, (size[0], size[1]))
        cv2.imwrite('./{}_{}_{}.jpg'.format(image[:-4], size[0], size[1]), img)
    return img


def udp_send(image, socket_process):
    """
    :param image: 要发送的图片数据
    :param socket_process: socket连接
    :return:
    """
    start_time = datetime.datetime.now()
    print("Client Vehicle A Starts Sending Image: ", start_time)
    encoded_image = cv2.imencode('.jpg', image)[1].tobytes()
    data_length = len(encoded_image)
    print("Fhead: {} bytes will be send!".format(data_length))
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
    end_time = datetime.datetime.now()
    print("Client Vehicle A Ends Sending Image: ", end_time)
    print('Transmission Cost: ', end_time - start_time)


if __name__ == '__main__':
    img_path = './data/bus.jpg'
    sized_image = image_resize(img_path, (640, 640))
    # 创建UDP socket
    print("Start Initializing Socket Process")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_send(sized_image, sock)
    sock.close()
