import pytest
from aiohttp import web
from hasoffers_api.api import Api, ApiController, ApiMethod, \
    ApiRequest, APIUsageExceededRateLimit

pytest_plugins = 'aiohttp.pytest_plugin'


async def test_api_builder():
    network = 'test_network'
    apikey = 'test_apikey'

    controller_name = 'test_controller'
    method_name = 'method_name'

    builder = Api(network=network, apikey=apikey)

    controller = getattr(builder, controller_name)

    assert isinstance(controller, ApiController) is True

    method = getattr(controller, method_name)

    assert isinstance(method, ApiMethod) is True

    payload = {
        'filters': {
            'id': 1,
        },
    }

    request = method(payload)

    assert isinstance(request, ApiRequest) is True
    assert network in request.url

    assert request.params == dict(
        NetworkToken=apikey,
        Target=controller_name,
        Method=method_name,
        **payload,
    )


async def done_handler(request):
    return web.json_response({
        'response': {
            'data': 'Done',
            'errorMessage': '',
        },
    })


async def usagelimit_handler(request):
    return web.json_response({
        'response': {
            'data': '',
            'errorMessage': 'API usage exceeded rate limit:',
        },
    })


async def paging_handler(request):
    return web.json_response({
        'response': {
            'data': {
                'page': 0,
                'pageCount': 10,
                'data': [
                    'Done',
                ],
            },
            'errorMessage': '',
        },
    })


async def test_api_request(loop):

    builder = Api(network='network', apikey='apikey')
    request = builder.Controller.Method({})

    app = web.Application()
    app.router.add_route('GET', '/done', done_handler)
    app.router.add_route('GET', '/usagelimit', usagelimit_handler)
    app.router.add_route('GET', '/paging', paging_handler)

    host, port = '127.0.0.1', 8000

    server = loop.create_server(app.make_handler(), host, port)
    loop.create_task(await server)

    request.url = 'http://{host}:{port}/done?'.format(host=host, port=port)
    response = await request
    assert response == 'Done'

    request.url = 'http://{host}:{port}/usagelimit?'.format(host=host, port=port)

    with pytest.raises(APIUsageExceededRateLimit):
        await request

    request = builder.Controller.Method({
        'limit': 100,
    })
    request.url = 'http://{host}:{port}/paging?'.format(host=host, port=port)

    pages = 10

    async for results in request:
        pages -= 1

        for result in results:
            assert result == 'Done'

    assert pages == 0
