TelegramBot
===========

TelegramBot - это учебный проект.

Установка
---------

Создайте виртуальное окружение и активируйте его. Далее в виртуальном окружении выполните:

.. code-block:: text

    pip install -r requirements.txt

Настройка
---------

Создайте файл settings.py и добавьте туда следующие настройки:

.. code-block:: python

    TG_TOKEN = "Токен (API ключ) который получили от BotFather"
    TG_API_URL = "https://telegg.ru/orig/bot"

Запуск
------

В активированном виртуальном окружении выполните:

.. code-block:: python

    python3 bot.py