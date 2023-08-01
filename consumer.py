#! /usr/bin/env python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QCoreApplication
import socket, sys
from keeper.connections import DBConnector
from keeper.environments import SystemEnv
from loguru import logger


class ReceiveUDP(QThread):
    def __init__(self, local_address, parent = None):
        QThread.__init__(self,parent)
        # Thiết lập kết nối UDP trên máy chủ
        # local_address = "HostIP:Port" ,
        # Ví dụ: local_address = "192.168.1.10:1003" ,
        # + địa chỉ IP của máy chủ trong mạng cục bộ là static IP = 192.168.1.10
        # + cổng UDP được mở cho IoT với ID số 3: Port = 1003
        self.local_address = local_address
        self.local_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        address = self.local_address.split(':')
        self.local_socket.bind((address[0],int(address[1])))
        self.redis_conn = DBConnector.redis_connection

    def run(self):
        while True:
            msg_master, add = self.local_socket.recvfrom(1024)
            if msg_master:
                # Chuyển chuỗi ký tự nhận được sang dạng str
                msg = msg_master.decode('utf-8')
                # Tách trường dữ liệu @ID:state, lấy ID và state
                msg_decode = msg.replace('@','').split(':')
                ID = int(msg_decode[0])
                state = int(msg_decode[1])
                # In kết quả nhận được
                # ID và state sẽ được sử dụng để hiển thị trạng thái trên bản đồ bố trí chỗ để xe
                self.redis_conn.set(ID, state)
                logger.info("Receive: {}".format(msg))

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    # Tạo các thread nhận dữ liệu phản hồi từ các thiết bị IoT
    N = SystemEnv.num_slots
    List_IoT = []
    Host_IP = SystemEnv.api_host
    # Tao ra các thread quản lý N thiết bị IoT
    for k in range(N):
        address = '{0}:{1}'
        ID = k+1
        Port = 1000+ID
        udp_address = address.format(Host_IP,Port)
        IoT = ReceiveUDP(udp_address)
        List_IoT.append(IoT)

    # Chạy N threads quản lý các TB IoT
    for k in range(N):
        List_IoT[k].start()

    sys.exit(app.exec_())
