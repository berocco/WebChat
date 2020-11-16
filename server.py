LISTEN_ADDRESS = ('0.0.0.0', 8080)

import websockets
import asyncio
import json

# The set of clients connected to this server. It is used to distribute
# messages.
clients = {} #: {websocket: name}

@asyncio.coroutine
def client_handler(websocket, path):
    print('Novo cliente', websocket)
    print(' ({} cilentes online)'.format(len(clients)))
    mt = {'mt':'clients', 'data':', '.join(list(clients.values()))}
    yield from websocket.send(json.dumps(mt))

    # The first line from the client is the name
    name = yield from websocket.recv()
    mt = {'mt':'serv', 'data':'Bem vindo ao chat, {}!'.format(name)}
    yield from websocket.send(json.dumps(mt))
    clients[websocket] = name
    for client, _ in clients.items():
        mt = {'mt':'clients', 'data':', '.join(list(clients.values()))}
        yield from client.send(json.dumps(mt))
        if not client == websocket:
            mt = {'mt':'serv', 'data':name + ' se juntou ao chat'}
            yield from client.send(json.dumps(mt))

    # Handle messages from this client
    while True:
        try:
            message = yield from websocket.recv()
        except:
            their_name = clients[websocket]
            del clients[websocket]
            print('Client closed connection', websocket)
            for client, _ in clients.items():
                mt = {'mt':'clients', 'data':', '.join(list(clients.values()))}
                yield from client.send(json.dumps(mt))
                mt = {'mt':'serv', 'data':name + ' saiu do chat'}
                yield from client.send(json.dumps(mt))
            break
        # Send message to all clients
        if message[0] != "\\":
            for client, _ in clients.items():
                mt = {'mt':'mess', 'data':'{}: {}'.format(name, message)}
                yield from client.send(json.dumps(mt))
        else:
            try:
                to = message[1:].split(' ')[0]
                a = next((server for server, nome in clients.items() if nome == to), None)
                mt = {'mt':'pm', 'data':'[Private] {}: {}'.format(name, ' '.join(message.split(' ')[1:]))}
                yield from a.send(json.dumps(mt))
                mt = {'mt':'pm', 'data':'[Private to {}] {}: {}'.format(to, name, ' '.join(message.split(' ')[1:]))}
                yield from websocket.send(json.dumps(mt))
            except:
                mt = {'mt':'server', 'data':'Usuário não encontrado'}
                yield from websocket.send(json.dumps(mt))


start_server = websockets.serve(client_handler, *LISTEN_ADDRESS)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()