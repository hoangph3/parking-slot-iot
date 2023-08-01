#! /usr/bin/env python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QCoreApplication
import socket, sys
from time import sleep
import random
from keeper.environments import SystemEnv
from loguru import logger


class SendUDP(QThread):
    def __init__(self, ID,remote_address,parent = None):
        QThread.__init__(self,parent)
        # Lấy thông tin về ID của IoT
        self.ID = ID
        # Gán trạng thái mặc định cho IoT#
        # state = 0: không có xe; state = 1: có xe
        self.state = 0
        # Remote_address: địa chỉ IP + cổng UDP tương ứng trên máy chủ
        # Ví dụ IP của máy chủ là 192.168.1.10, cổng UDP là 1001,
        # thì Remote_address = "192.168.1.10:1001"
        self.remote_address = remote_address
        # Thiết lập kết nối UDP
        self.send_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        # Lấy thông tin IP và Port để tạo ra địa chỉ UDP chuẩn
        address = self.remote_address.split(':')
        self.remote_UDP_address = (address[0],int(address[1]))
        self.parent = parent
    """
    Gửi thông tin phản hồi về State của IoT lên PC trung tâm, giả lập với hàm random
    """
    def run(self):
        # Implement own function
        while True:
            # Tạo dữ liệu giả lập trạng thái chỗ để xe
            if random.randint(0,10)>6:
                self.state = 1 - self.state
            # Đóng gói msg_feedback: "@ID:State"
            msg = "@{0}:{1}"
            msg_feedback = msg.format(self.ID,self.state)
            logger.info("Send: {}".format(msg_feedback))
            # Gửi dữ liệu đi
            self.send_socket.sendto(msg_feedback.encode(),self.remote_UDP_address)
            sleep(2)  # Time delay between 2 consecutive sends

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    # Tạo các thread giả lập thiết bị IoT với từng ID riêng
    # Chú ý, gán địa chỉ cổng cần giống với ID của IoT cho dễ quản lý,
    N = SystemEnv.num_slots
    List_IoT = []
    Host_IP = SystemEnv.api_host
    # Tạo ra N thiết bị IoT ảo
    for k in range(N):
        address = '{0}:{1}'
        ID = k+1
        Port = 1000+ID
        udp_address = address.format(Host_IP,Port)
        IoT = SendUDP(ID,udp_address)
        List_IoT.append(IoT)

    # Chạy các thiết bị IoT ảo
    for k in range(N):
        List_IoT[k].start()

    sys.exit(app.exec_())
