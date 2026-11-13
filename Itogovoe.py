from tkinter import Tk, Label, Button   # Импорт из tkinter: главное окно, текстовая метка, кнопка.
from tkinter import messagebox as mb    # Импорт модуля диалоговых окон — для showinfo/showwarning/showerror.
from tkinter import ttk                 # Импорт ttk — «тематизированных» виджетов (Combobox, Label с поддержкой стилей)
import requests                         # Библиотека для HTTP-запросов.
from io import BytesIO                  # BytesIO превращает байты (содержимое картинки) в файлоподобный объект
                                        # Нужно, чтобы PIL.Image.open мог прочитать картинку из памяти, а не с диска.
from PIL import Image, ImageTk          # Image — открытие/ресайз картинки;
                                        # ImageTk — конвертация в формат, понятный Tkinter.


def update_crypto_label(event):
    """Обновляет метку под списком при выборе криптовалюты.
    Tkinter вызывает функцию автоматически, когда пользователь выбирает монету в выпадающем списке:
    - узнаёт, что именно выбрал пользователь;
    - по этому коду находит в словаре currencies красивое название;
    - записывает это название в метку под списком, чтобы пользователь его увидел.
    """
    code = crypto_combobox.get()
    name = currencies[code]
    crypto_label.config(text=name)
    # Альтернативный однострочный вариант:
    # crypto_label.config(text=currencies[crypto_combobox.get()])


def update_fiat_label(event):
    """Обновляет метку под списком при выборе валюты.
    Tkinter вызывает функцию автоматически, когда пользователь выбирает валюту в выпадающем списке:
    - узнаёт, что именно выбрал пользователь;
    - по этому коду находит в словаре fiats красивое название;
    - записывает это название в метку под списком, чтобы пользователь его увидел.
    """
    code = fiat_combobox.get()
    name = fiats[code]
    fiat_label.config(text=name)
    #   Альтернативный однострочный вариант:
    #   fiat_label.config(text=fiats[fiat_combobox.get()])


def exchange():
    """По нажатию на кнопку «Получить цену» выполняет запрос к API и показывает результат.
    - проверяет, что оба поля заполнены;
    - делает GET-запрос к CoinGecko (таймаут 5 с);
    - при успехе показывает цену в диалоге, при ошибке сети/данных — пробуем другой API.
    """
    crypto_id = crypto_combobox.get().strip()
    fiat_code = fiat_combobox.get().strip().lower()

    if not (crypto_id and fiat_code):
        mb.showwarning('Внимание', 'Выберите криптовалюту и фиатную валюту')
        return

    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': crypto_id, 'vs_currencies': fiat_code},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if crypto_id in data and fiat_code in data[crypto_id]:
            price = data[crypto_id][fiat_code]
            mb.showinfo('Цена', f'1 {currencies[crypto_id]} = {price:,.2f} {fiats[fiat_code]}')
        else:
            mb.showerror('Ошибка', 'Не удалось получить цену')
    except requests.exceptions.RequestException as er:
        # CoinGecko не ответил — пробуем CoinPaprika
        if fiat_code == 'kzt':
            mb.showerror('Ошибка сети',
                         'CoinGecko недоступен, а резервный источник не поддерживает тенге'
                         )
            return
        try:
            price = exchange_reserve(crypto_id, fiat_code)
            mb.showinfo(
                'Цена (резервный источник)',
                f'1 {currencies[crypto_id]} = {price:,.2f} {fiats[fiat_code]}\n'
                f'Источник: CoinPaprika'
            )
        except Exception:
            mb.showerror('Ошибка сети', f'CoinGecko: {er}\nCoinPaprika тоже недоступен')


def exchange_reserve(crypto_id, fiat_code):
    """Резервный источник: цена с CoinPaprika.
    - переводим в нужный код
    - возвращаем цену или ошибку
    """
    paprika_id = paprika_ids.get(crypto_id)
    if not paprika_id:
        raise ValueError('Нет соответствия ID для CoinPaprika')

    response = requests.get(
        f'https://api.coinpaprika.com/v1/tickers/{paprika_id}',
        params={'quotes': fiat_code.upper()},   # CoinPaprika ждёт заглавные: RUB, USD
        timeout=5
    )
    response.raise_for_status()
    data = response.json()

    quotes = data.get('quotes', {})
    fiat_upper = fiat_code.upper()
    if fiat_upper not in quotes or 'price' not in quotes[fiat_upper]:
        raise ValueError('CoinPaprika не вернул цену для этой валюты')

    return quotes[fiat_upper]['price']


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

# Соответствие ID CoinGecko -> ID CoinPaprika (для резервного API)
paprika_ids = {
    'bitcoin': 'btc-bitcoin',
    'ethereum': 'eth-ethereum',
    'tether': 'usdt-tether',
    'binancecoin': 'bnb-binance-coin',
    'solana': 'sol-solana',
    'ripple': 'xrp-xrp',
    'dogecoin': 'doge-dogecoin',
    'cardano': 'ada-cardano',
    'tron': 'trx-tron',
    'polkadot': 'dot-polkadot',
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

color_bg = '#EAF6FF' # цвет фона

root = Tk()
root.title('Курс обмена криптовалют')
root.geometry('360x250')
root.configure(bg=color_bg)

# Иконка приложения
icon_url = "https://cdn-icons-png.flaticon.com/512/4843/4843256.png"   # прямая ссылка на картинку
try:
    response = requests.get(icon_url, timeout=5)
    response.raise_for_status()
    img_data = Image.open(BytesIO(response.content))
    img_data = img_data.resize((32, 32))
    icon = ImageTk.PhotoImage(img_data)
    root.iconphoto(True, icon)
except Exception as er:
    print(f'Иконка не загружена: {er}')   # просто сообщение в консоль


Label(root, text='Криптовалюта', bg=color_bg).pack()
crypto_combobox = ttk.Combobox(root, values=list(currencies.keys()), state='readonly')
crypto_combobox.pack(pady=3, padx=10)
crypto_combobox.bind('<<ComboboxSelected>>', update_crypto_label)
crypto_label = ttk.Label(background=color_bg)
crypto_label.pack()

Label(root, text='Фиатная валюта', bg=color_bg).pack(padx=10)
fiat_combobox = ttk.Combobox(root, values=list(fiats.keys()), state='readonly')
fiat_combobox.pack(pady=3, padx=10)
fiat_combobox.bind('<<ComboboxSelected>>', update_fiat_label)
fiat_label = ttk.Label(background=color_bg)
fiat_label.pack()

Button(
    text='Получить курс обмена',
    command=exchange,
    bg='lightblue',
    activebackground='#000080',
    activeforeground='white'
).pack(pady=15, padx=10)

root.mainloop()