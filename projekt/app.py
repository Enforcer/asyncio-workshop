import asyncio
import json
import logging
import time
from collections import deque
from contextlib import contextmanager

from aiohttp import (
    web,
    WSMsgType,
)


chat_logger = logging.getLogger('chat_logger')
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
)
chat_logger.addHandler(handler)
chat_logger.setLevel(level=logging.INFO)


@contextmanager
def chat_presence(app, nickname, ws):
    app['chat_members'][nickname] = ws
    chat_logger.info('%s joins the chat', nickname)
    yield
    chat_logger.info('%s leaves the chat', nickname)
    del app['chat_members'][nickname]


def get_messages_from_last_10_minutes(app):
    ten_minutes_ago = time.time() - 60 * 10
    app['messages_archive'] = [
        message for message in app['messages_archive']
        if message['timestamp'] >= ten_minutes_ago
    ]
    return app['messages_archive']


async def websocket_handler(request):
    nickname = request.GET['nickname']
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    members_dict = request.app['chat_members']

    # sending old messages
    archival_messages = get_messages_from_last_10_minutes(request.app)
    for message in archival_messages:
        await ws.send_json(message)

    with chat_presence(request.app, nickname, ws):

        async for msg in ws:

            if msg.type == WSMsgType.TEXT:
                decoded_data = msg.json()
                message = {
                    'message': decoded_data['message'],
                    'from': nickname,
                    'timestamp': time.time()
                }
                request.app['messages_archive'].append(message)
                coros = [
                    member_ws.send_json(message)
                    for member_ws in members_dict.values()
                ]
                # return_exceptions silents exceptions because they are returned
                # in a list, not thrown
                await asyncio.gather(*coros, return_exceptions=True)
            elif msg.type == WSMsgType.ERROR:
                chat_logger.warning('ws connection closed with exception %s', ws.exception())

    return ws


async def index(request):
    return web.FileResponse('./index.html')


async def css(request):
    return web.FileResponse('./static/style.css')


async def reconnecting_websocket(request):
    return web.FileResponse('./static/reconnecting-websocket.min.js')


async def members(request):
    return web.json_response(list(request.app['chat_members'].keys()))


async def rooms(request):
    return web.json_response([])


def create_app(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_get('/', index)
    app.router.add_get('/members', members)
    app.router.add_get('/rooms', rooms)
    app.router.add_get('/style.css', css)
    app.router.add_get('/reconnecting-websocket.min.js', reconnecting_websocket)
    app.router.add_get('/ws', websocket_handler)
    app['chat_members'] = {}
    # each element is a tuple (time.time(), message)
    app['messages_archive'] = []
    return app


def dump_archival_messages_to_hard_drive(app):
    chat_logger.info('Saving messages to file...')
    data = json.dumps(app['messages_archive'])
    with open('messages.dump', 'wb') as file:
        file.write(data.encode())
    chat_logger.info('Saved %d messages to file.', len(app['messages_archive']))
    asyncio.get_event_loop().call_later(15, dump_archival_messages_to_hard_drive, app)


def load_archival_messages(app):
    try:
        with open('messages.dump', 'rb') as file:
            app['messages_archive'] = json.loads(file.read())
        chat_logger.info('Loaded %d messages from file.', len(app['messages_archive']))
    except FileNotFoundError:
        chat_logger.warning('No messages loaded, because file does not exist.')


if __name__ == '__main__':
    app = create_app()
    load_archival_messages(app)
    asyncio.get_event_loop().call_later(15, dump_archival_messages_to_hard_drive, app)
    web.run_app(app, port=8080)
