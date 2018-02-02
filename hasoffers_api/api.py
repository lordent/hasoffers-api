import aiohttp
import ujson
import asyncio
from multidimensional_urlencode import urlencode


class ApiError(Exception):
    pass


class InvalidAuthorization(ApiError):
    pass


class MissingRequiredArgument(ApiError):
    pass


class APIUsageExceededRateLimit(ApiError):
    pass


class FailedToHydrateRows(ApiError):
    pass


class NetworkTokenIsNotAuthenticated(ApiError):
    pass


class IPIsNotWhiteListed(ApiError):
    pass


ERRORS = {
    'Invalid Authorization': InvalidAuthorization,
    'Missing required argument': MissingRequiredArgument,
    'API usage exceeded rate limit': APIUsageExceededRateLimit,
    'Failed to hydrate rows': FailedToHydrateRows,
    'is not authenticated': NetworkTokenIsNotAuthenticated,
    'is not white-listed': IPIsNotWhiteListed,
}


class ApiRequest:

    def __init__(self, url, params, auto_retry=False):
        self.url = url
        self.params = params or dict()
        self.auto_retry = auto_retry

    def __await__(self):
        return self.api_call(self.url + urlencode(self.params)).__await__()

    async def __aiter__(self):
        if 'limit' in self.params:
            self.params.update(page=0)
            result = await self
            yield result['data']
            for page in range(1, result['pageCount']):
                self.params.update(page=page)
                yield (await self)['data']
        else:
            yield await self

    async def api_call(self, url):
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url) as response:
                result = ujson.loads(await response.read())

        if 'response' in result:
            if result['response']['errorMessage']:
                for error_type, error_class in ERRORS.items():
                    if error_type in result['response']['errorMessage']:

                        if error_class is APIUsageExceededRateLimit \
                                and self.auto_retry:
                            await asyncio.sleep(1)
                            return await self

                        raise error_class(result['response']['errorMessage'])
                raise ApiError(result['response']['errorMessage'])

            return result['response']['data']
        return result


class ApiMethod:

    def __init__(self, api_controller, name):
        self.api_controller = api_controller
        self.name = name

    def __call__(self, params=None, auto_retry=False):
        url = 'https://%s/Apiv3/json?' % '%s.api.hasoffers.com' % self.api_controller.api.network
        params = dict(
            NetworkToken=self.api_controller.api.apikey,
            Target=self.api_controller.name,
            Method=self.name,
            **(params or dict())
        )
        return ApiRequest(url, params, auto_retry=auto_retry)


class ApiController:

    def __init__(self, api, name):
        self.api = api
        self.name = name

    def __getattr__(self, api_method_name):
        return ApiMethod(self, api_method_name)


class Api:
    """Async HasOffers Network API driver
    https://developers.tune.com/network/

    Usage examples:
    - request collection of objects
      async for results in api.Offer.findAll({
        'filters': {
            'status': 'active',
        },
        'contain': [
            'Goal',
            'Country',
        ],
        'limit': 100, # Set `limit` value for paging results
      }, auto_retry=True): # Use `auto_retry` for continue on API usage limit
        for res in results.values():
            print(res['Offer']['name'])
            if res['Goal']:
                print(len(res['Goal']))

    - request one object or call method
      affiliate = await api.Affiliate.findById({'id': 1})
    """

    def __init__(self, network, apikey):
        self.network = network
        self.apikey = apikey

    def __getattr__(self, api_controller_name):
        return ApiController(self, api_controller_name)
