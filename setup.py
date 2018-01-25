from setuptools import setup


setup(
    name='hasoffers_api',
    version='1.0.0',
    description='Async HasOffers Network API driver',
    long_description='',
    author='Vitaliy Nefyodov',
    author_email='vitent@gmail.com',
    packages=['hasoffers_api'],
    url='https://github.com/lordent/hasoffers-api',
    requires=[
        'multidimensional_urlencode',
        'aiohttp',
        'ujson',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ]
)
