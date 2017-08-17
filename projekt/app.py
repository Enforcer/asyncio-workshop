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
            # msg.data - data received
            await ws.send_str('response from a server')
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
    return web.Response(text='[]')


app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/members', members)
app.router.add_get('/style.css', css)
app.router.add_get('/reconnecting-websocket.min.js', reconnecting_websocket)
app.router.add_get('/ws', websocket_handler)

if __name__ == '__main__':
    web.run_app(app, port=8080)
