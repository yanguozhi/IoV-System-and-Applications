# coding=utf-8

import datetime
import socket
import cv2
import numpy as np
import struct

PACKET_UNIT = 2850


def udp_rec(socket_process):
    image_total = b''
    img_packet_dict = {}
    total_size = 0
    time_list = []
    while True:
        data, addr = socket_process.recvfrom(PACKET_UNIT)
        now = datetime.datetime.now()
        time_list.append(now)
        fhead_size = struct.unpack('i', data[:4])[0]
        count = struct.unpack('i', data[4:8])[0]
        img_packet = data[8:]
        img_packet_dict[count] = img_packet
        recvd_size = len(img_packet)
        total_size += recvd_size
        print(f'Fhead:{fhead_size}, Count:{count}, Recv:{recvd_size}, SumRecv:{total_size}')
        # count 为 表示收到最后一个包，发送方包从1开始计数， 计数0表示最后一个包# a = len(img_packet_dict.keys())
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
                print('Receive A New Frame')
                print('Time Cost,', now - time_list[0])
            else:  # 说明有丢包，丢弃前面接收的所有数据包，该图片包不完整
                print('Lose Packets')
                img_decode = None
            return img_decode


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('192.168.62.117', 30301))
    print('Bind Up on 30301...')
    print('Receiving Start......{}'.format(datetime.datetime.now()))
    recvd_img = udp_rec(s)
    if recvd_img is not None:
        cv2.imwrite('./data/recvd_frame.jpg', recvd_img)
        cv2.imshow('camera: ', recvd_img)
        cv2.waitKey()  # 不带参数表示按下任何键盘按键，都会关闭打开的窗口
        # if cv2.waitKey(5) == 27:  # 按鼠标的ESC键可退出展示窗口
        cv2.destroyAllWindows()
    s.close()
    print('Close the Communication Channel...')
