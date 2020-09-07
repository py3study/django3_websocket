# ！/usr/bin/python3
# -*- coding: utf-8 -*-
import paramiko


async def websocket_application(scope, receive, send):
    while True:
        event = await receive()

        if event['type'] == 'websocket.connect':
            await send({
                'type': 'websocket.accept'
            })

        if event['type'] == 'websocket.disconnect':
            break

        if event['type'] == 'websocket.receive':
            if event['text'] == 'ping':
                await send({
                    'type': 'websocket.send',
                    'text': 'pong!'
                })

            # 这里根据web页面获取的值进行对应的操作
            if event['text'] == 'laying_eggs':
                print("要执行脚本了")
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
                    await send({
                        'type': 'websocket.send',
                        'text': nextline
                    })
                    # 判断消息为空时,退出循环
                    if not nextline:
                        break

                ssh.close()  # 关闭ssh连接
                # 关闭websocket连接
                await send({
                    'type': 'websocket.close',
                })
