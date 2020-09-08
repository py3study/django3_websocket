import json
from channels.generic.websocket import AsyncWebsocketConsumer
import paramiko
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

# 同步方式，仅作示例，不使用
class SyncConsumer(WebsocketConsumer):
    def connect(self):
        self.username = "xiao"  # 临时固定用户名
        print('WebSocket建立连接：', self.username)
        # 直接从用户指定的通道名称构造通道组名称
        self.channel_group_name = 'msg_%s' % self.username

        # 加入通道层
        # async_to_sync(…)包装器是必需的，因为ChatConsumer是同步WebsocketConsumer，但它调用的是异步通道层方法。(所有通道层方法都是异步的。)
        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name,
            self.channel_name
        )  
        
        # 接受WebSocket连接。
        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name,
            {
                'type': 'get_message',
            }
        )

    def disconnect(self, close_code):
        print('WebSocket关闭连接')
        # 离开通道
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name,
            self.channel_name
        )

    # 从WebSocket中接收消息
    def receive(self, text_data=None, bytes_data=None):
        print('WebSocket接收消息：', text_data,type(text_data))
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # print("receive message",message,type(message))
        # 发送消息到通道
        async_to_sync(self.channel_layer.group_send)(
            self.channel_group_name,
            {
                'type': 'get_message',
                'message': message
            }
        )

    # 从通道中接收消息
    def get_message(self, event):
        # print("event",event,type(event))
        if event.get('message'):
            message = event['message']
            # 判断消息
            if message == "close":
                # 关闭websocket连接
                self.disconnect(self.channel_group_name)
                print("前端关闭websocket连接")

            # 判断消息，执行脚本
            if message == "laying_eggs":
                # 执行的命令或者脚本
                command = 'bash /opt/test.sh'

                # 远程连接服务器
                hostname = '192.168.31.196'
                username = 'root'
                password = 'root'

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=hostname, username=username, password=password)
                # 务必要加上get_pty=True,否则执行命令会没有权限
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                # result = stdout.read()
                # 循环发送消息给前端页面
                while True:
                    nextline = stdout.readline().strip()  # 读取脚本输出内容
                    # print(nextline.strip())

                    # 发送消息到客户端
                    self.send(
                        text_data=nextline
                    )
                    print("已发送消息:%s" % nextline)
                    # 判断消息为空时,退出循环
                    if not nextline:
                        break

                ssh.close()  # 关闭ssh连接
                # 关闭websocket连接
                self.disconnect(self.channel_group_name)
                print("后端关闭websocket连接")