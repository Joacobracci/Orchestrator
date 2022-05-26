# import socket
# serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serv.bind(('127.0.0.1', 7777))
# serv.listen(5)
# while True:
# conn, addr = serv.accept()
# from_client = ''
# while True:
#     data = conn.recv(4096)
#     if not data: break
#     from_client += data
#     print (from_client)
#     conn.send("I am SERVER")
# conn.close()
# print ('client disconnected')

# import socket
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(('127.0.0.1', 7777))
# client.send("I am CLIENT")
# from_server = client.recv(4096)
# client.close()
# print (from_server)

# import socket
# host='127.0.0.1'
# port=7777
# s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# s.connect((host,port))
# st='pingection ss'
# byt=st.encode()
# s.send(byt)


import websockets
import asyncio

async def listen():
    url="ws://127.0.0.1:7777/trigger"
    
    async with websockets.connect(url) as ws:
        while True:
            msg = await ws.recv()
            print(msg)
    
asyncio.get_event_loop().run_until_complete(listen())
asyncio.get_event_loop().run_forever()