#!/usr/bin/python3

from web3 import Web3
import requests
import telebot
import emoji
import time
import os
from pythonpancakes import PancakeSwapAPI

ps = PancakeSwapAPI()
mai_cake = ps.tokens("0xe985e923b6c52b420dd33549a0ebc2cdeb0ae173")
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/d2f78cc8828f4c7b9ac7065a09a6427f"))
contract = w3.eth.contract(address=Web3.toChecksumAddress("0x068c0626100631db4e0518401e2ab62359bca89b"), abi='''[
    {
        "inputs": [],
        "name": "getPrice",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "mai_eth_price",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "mai_usdt_price",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "eth_usdt_price",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]'''
)


def get_mai_price():
    (mai_eth_price18, mai_usd_price18, eth_price6) = contract.functions.getPrice().call()
    (mai_eth_price, mai_usd_price, eth_price) = (mai_eth_price18/10**18, mai_usd_price18/10**6, eth_price6/10**6)

    print("MAI price on Uniswap V3 (MAI/ETH): $%5.4f [%10.8f ETH]" % (mai_eth_price * eth_price, mai_eth_price))
    print("MAI price on Uniswap V3 (MAI/USDT): $%5.4f" % (mai_usd_price))

    response = requests. get("https://global-openapi.bithumb.pro/openapi/v1/spot/ticker?symbol=MAI-USDT")
    json = response.json()
    bithumb_price = float(json['data'][0]['c'])
    print("MAI price on Bithumb (MAI/USDT):   $%5.4f" % bithumb_price)

    ps = PancakeSwapAPI()
    mai_cake = ps.tokens("0xe985e923b6c52b420dd33549a0ebc2cdeb0ae173")
    data = mai_cake["data"]
    mai_bnb_price = float(data["price_BNB"])
    mai_pcs_usd_price = float(data["price"])

    return (bithumb_price, mai_eth_price * eth_price, mai_eth_price, mai_usd_price, mai_pcs_usd_price, mai_bnb_price)

api_key = os.environ['MINDSYNC_TG_API_KEY']
bot = telebot.TeleBot(api_key)


@bot.message_handler(commands=['price'])
def price(message):
    (bithumb_usd, univ3_maieth_usd, univ3_eth, univ3_maiusdt, pcs_maiusdt, pcs_maibnb) = get_mai_price()
    bot.reply_to(message, emoji.emojize('''🐳 <b>MAI/USDT: 🚀</b>

$%.6f  <b><a href="https://www.bithumb.pro/en-us/exchange/professional?q=MAI-USDT">Bithumb</a></b>\n
$%.6f  <b><a href="https://info.uniswap.org/#/pools/0xf80071b5f13f7ba7504752908ddb449be7e21cc9">Uniswap V3</a></b>

🐳 <b>MAI/ETH: 🚀</b>

$%.6f  <b><a href="https://info.uniswap.org/#/pools/0x8d274f951c4330982146e718a1cee58802b1c372">Uniswap V3</a></b>

🐳 <b>MAI/BNB: 🚀</b>

$%.6f  <b><a href="https://pancakeswap.finance/swap/0xe985e923b6c52b420dd33549a0ebc2cdeb0ae173">Pancakeswap</a></b>

💡 Tip: <i>Click on the exchange name to trade MAI</i>

🔄 <b>Swap ERC20-BEP20:</b>

https://bridge.mindsync.ai
\n
''' % (bithumb_usd, univ3_maiusdt, univ3_maieth_usd, pcs_maiusdt)), parse_mode='HTML', disable_web_page_preview='true')


while True:
    try:
        bot.polling(none_stop=True, timeout=120)
    except Exception as e:
        print(str(e))
        time.sleep(30)
