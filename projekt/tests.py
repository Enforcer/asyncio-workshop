import asyncio

from .app import create_app


async def test_receives_sent_message(test_client):
    client = await test_client(create_app)
    connection = await client.ws_connect('/ws?nickname=JohnDoe')

    await connection.send_json({
        'message': 'Hello, world!', 'from': 'JohnDoe', 'timestamp': 0
    })
    response = await asyncio.wait_for(connection.receive_json(), 0.05)

    assert response['message'] == 'Hello, world!'
    assert response['from'] == 'JohnDoe'


async def test_presence(test_client):
    client = await test_client(create_app)

    connection = await client.ws_connect('/ws?nickname=JohnDoe')

    response = await client.get('/members')
    members_list = await response.json()

    assert members_list == ['JohnDoe']

    await connection.close()
    response = await client.get('/members')
    members_list = await response.json()

    assert members_list == []

async def test_conversation_between_two_users(test_client):
    client = await test_client(create_app)

    connection_one = await client.ws_connect('/ws?nickname=JohnDoe')
    connection_two = await client.ws_connect('/ws?nickname=JonSnow')

    await connection_one.send_json({'message': 'xDDD', 'from': 'JohnDoe', 'timestamp': 0})
    response = await asyncio.wait_for(connection_two.receive_json(), 0.05)

    assert response['message'] == 'xDDD'
    assert response['from'] == 'JohnDoe'


async def test_new_client_gets_old_messages(test_client):
    client = await test_client(create_app)

    connection_one = await client.ws_connect('/ws?nickname=JohnDoe')

    await connection_one.send_json({'message': 'LOL', 'from': 'JohnDoe', 'timestamp': 0})
    await connection_one.close()

    connection_two = await client.ws_connect('/ws?nickname=JonSnow')
    response = await asyncio.wait_for(connection_two.receive_json(), 0.05)

    assert response['message'] == 'LOL'
    assert response['from'] == 'JohnDoe'
