from .app import create_app


async def test_receives_sent_message(test_client):
    client = await test_client(create_app)
    connection = await client.ws_connect('/ws?nickname=JohnDoe')

    message = 'Hello, world!'
    example_payload = {'message': message, 'from': 'JohnDoe', 'timestamp': 0}
    await connection.send_json(example_payload)
    response = await connection.receive_json()

    assert response['message'] == message
