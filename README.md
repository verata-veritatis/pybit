# pybit
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
Python3 API connector for Bybit's HTTP and Websockets APIs.

## About
Put simply, `pybit` (Python + Bybit) is a lightweight one-stop-shop module for the Bybit HTTP and WebSocket APIs. I was personally never a fan of auto-generated connectors that used a mosh-pit of various modules you didn't want (sorry, `bravado`) and wanted to build my own Python3-dedicated connector with very little external resources. The goal of the connector is to provide traders and developers with an easy-to-use high-performing module that has an active issue and discussion board leading to consistent improvements.

## Development
As a user of the module myself, `pybit` is being actively developed, especially since Bybit is making changes and improvements to their API on a daily basis (we're still missing some key functions such as bulk order submission or withdrawals). `pybit` uses `requests` and `websocket-client` for its methods, alongside other built-in modules. Anyone is welcome to branch/fork the repository and add their own upgrades. If you think you've made substantial improvements to the module, submit a pull request and I'll gladly take a look.

## Installation
`pybit` requires Python 3.6.1 or higher. The module can be installed manually or via [PyPI](https://pypi.org/project/pybit/) with `pip`:
```
pip install pybit
```

## How to Use
You can retrieve the HTTP and WebSocket classes like so:
```python
from pybit import HTTP, WebSocket
```
Create an HTTP session and connect via WebSocket:
```python
session = HTTP(test_net=False, api_key='...', api_secret='...')
ws = WebSocket(
    endpoint='wss://stream.bybit.com/realtime', 
    subscriptions=['order', 'position'], 
    api_key='...', 
    api_secret='...'
)
```
Information can be sent to, or retrieved from, the Bybit APIs:
```python
# Get orderbook.
session.get_orderbook(symbol='BTCUSD')
# Place three long orders.
for i in [5000, 5500, 6000]:
    session.place_active_order(
        symbol='BTCUSD', 
        order_type='Limit', 
        side='Buy', 
        qty=100, 
        price=i
    )
# Check on your order and position through WebSocket.
ws.fetch(['order', 'position'])
```
Check out the example python files for more information on available
endpoints and methods.

## Contact
You can reach out to me via Telegram: @verataveritatis. I'm pretty active on the [BybitAPI Telegram](https://t.me/Bybitapi) group chat.
## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/verata-veritatis"><img src="https://avatars0.githubusercontent.com/u/9677388?v=4" width="100px;" alt=""/><br /><sub><b>verata-veritatis</b></sub></a><br /><a href="https://github.com/verata-veritatis/pybit/commits?author=verata-veritatis" title="Code">💻</a> <a href="https://github.com/verata-veritatis/pybit/commits?author=verata-veritatis" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!