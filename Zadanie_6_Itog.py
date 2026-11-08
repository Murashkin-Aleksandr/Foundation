from tkinter import *
from tkinter import messagebox as mb
from tkinter import ttk
import requests


def update_crypto_label(event):
    crypto_label.config(text=currencies[crypto_combobox.get()])
"""crypto_combobox.get() вызов метода get() у виджета ttk.Combobox. Он возвращает текущее выбранное (или введённое) значение из выпадающего списка в виде строки."""

def update_fiat_label(event):
    fiat_label.config(text=fiats[fiat_combobox.get()])


def exchange():
    crypto_id = crypto_combobox.get().strip()
    fiat_code = fiat_combobox.get().strip().lower()

    if not (crypto_id and fiat_code):
        mb.showwarning('Внимание', 'Выберите криптовалюту и фиатную валюту')
        return

    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': crypto_id, 'vs_currencies': fiat_code},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if crypto_id in data and fiat_code in data[crypto_id]:
            price = data[crypto_id][fiat_code]
            mb.showinfo('Цена', f'1 {currencies[crypto_id]} = {price:,.2f} {fiats[fiat_code]}')
        else:
            mb.showerror('Ошибка', 'Не удалось получить цену')
    except requests.exceptions.RequestException as er:
        mb.showerror('Ошибка сети', str(er))


currencies = {
    'bitcoin': 'Bitcoin (BTC)',
    'ethereum': 'Ethereum (ETH)',
    'tether': 'Tether (USDT)',
    'binancecoin': 'BNB',
    'solana': 'Solana (SOL)',
    'ripple': 'XRP',
    'dogecoin': 'Dogecoin (DOGE)',
    'cardano': 'Cardano (ADA)',
    'tron': 'TRON (TRX)',
    'polkadot': 'Polkadot (DOT)',
}

fiats = {
    'usd': 'Доллар США',
    'eur': 'Евро',
    'rub': 'Российский рубль',
    'gbp': 'Фунт стерлингов',
    'jpy': 'Японская йена',
    'cny': 'Китайский юань',
    'kzt': 'Казахстанский тенге',
}

root = Tk()
root.title('Курс криптовалют')
root.geometry('360x200')

Label(root, text='Криптовалюта').pack()
crypto_combobox = ttk.Combobox(root, values=list(currencies.keys()), state='readonly')
crypto_combobox.pack(pady=3, padx=10)
crypto_combobox.bind('<<ComboboxSelected>>', update_crypto_label)
crypto_label = ttk.Label()
crypto_label.pack()

Label(root, text='Фиатная валюта').pack(padx=10)
fiat_combobox = ttk.Combobox(root, values=list(fiats.keys()), state='readonly')
fiat_combobox.pack(pady=3, padx=10)
fiat_combobox.bind('<<ComboboxSelected>>', update_fiat_label)
fiat_label = ttk.Label()
fiat_label.pack()

Button(text='Получить цену', command=exchange).pack(pady=15, padx=10)

root.mainloop()