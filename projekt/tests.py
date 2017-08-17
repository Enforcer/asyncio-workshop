from .app import app


async def test_receives_sent_message(test_client):
    client = await test_client(app)
    connection = await client.ws_connect('/ws?nickname=JohnDoe')

    message = 'Hello, world!'
    await connection.send_str(message)
    response = await connection.receive_json()

    assert response['message'] == message
