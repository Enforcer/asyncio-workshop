import asyncio
from aiohttp import (
    web,
    WSMsgType,
)


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # ws.close() - closes connection
    # ws.send_str(str) - sends a str

    async for msg in ws:
        # msg.type - type of a message. See WSMsgType
        # msg.data - data received

        if msg.type == WSMsgType.TEXT:
            await ws.send_json(
                {'message': 'response from the server', 'from': 'anonymous'}
            )
        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    return ws


async def index(request):
    return web.FileResponse('./index.html')


async def css(request):
    return web.FileResponse('./static/style.css')


async def reconnecting_websocket(request):
    return web.FileResponse('./static/reconnecting-websocket.min.js')


async def members(request):
    return web.json_response([])


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
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, port=8080)
