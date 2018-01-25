# hasoffers_api: Async HasOffers . Network API driver

## HasOffers HTTP Network API Documentation

Full documentation is available at https://developers.tune.com/network/ .

## Usage

### Request collection of objects example
```python
async for results in api.Offer.findAll({
    'filters': {
        'status': 'active',
    },
    'contain': [
        'Goal',
        'Country',
    ],
    'limit': 100, # Set `limit` value for paging results
}, auto_retry=True): # Use `auto_retry` for continue or API usage rate limit
    for res in results.values():
        print(res['Offer']['name'])
        if res['Goal']:
            print(len(res['Goal']))
```

### Request one object or call method
```python
affiliate = await api.Affiliate.findById({'id': 1})
```

## Requirements
- Python >= 3.6
