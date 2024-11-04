# Url-shortener application 


Что это? Всё просто. Вы помните, что `UrlShortener` возвращает произвольную комбинацию символов в укороченном URL. А в VIP ссылках, это не так: пользователь сам указывает, какой будет его короткая ссылка, конечно, только если заданная им комбинация символов свободна.

Формальное описание интерфейса на OpenAPI 3.0 тут [openapi.yaml](openapi.yaml)

А ниже для общего представления неформальное описание.

make_shorter на входе получает:
```
url = "user-defined-long-url"
optional vip_key = "user-defined-symbols"
optional time_to_live = 1
optional time_to_live_unit = SECONDS, MINUTES, HOURS, DAYS
```

Максимальный TimeToLive не должен превышать 2 дней (иначе красивые vip ссылки закончатся).

В ответ на операцию приходит
```
short_url = "example.com/xyz" - короткая ссылка
secret_key - ключ для управления ссылкой
```

Ну или ошибка 400, если есть какие-то проблемы с входными параметрами, например, если vip_key уже занят или переданы невалидные значения для TTL.

### Требования

Необходимо, чтобы были установлены следующие компоненты:

- `Docker` и `docker-compose`
- `Python 3.12`
- `Poetry`

### Установка

1. Создание виртуального окружения и установка зависимостей
```commandline
poetry install
```

2. Активация виртуального окружения

```commandline
poetry shell
```


### Запуск

0. Создать `.env` файл с этими переменными (можно командой `make env`)
```dotenv
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=...
POSTGRES_PORT=5432
```

2. Создание базы в docker-контейнере (чтобы не работать с локальной базой):
```commandline
make db
```
2. Выполнение миграций:
```commandline
make migrate head
```
3. Запуск приложения:
```commandline
make run
```

Посмотреть документацию можно после запуска приложения по адресу `http://127.0.0.1:8080/swagger`.
### Тестирование

- Запуск тестов со всеми необходимыми флагами:
```commandline
make test
```

- Запуск тестов с генерацией отчета о покрытии:
```commandline
make test-cov
```

### Статический анализ

- Запуск линтеров
```commandline
make lint
```

- Запуск форматирования кода
```commandline
make format
```

### Дополнительные команды

- Создание новой ревизии:
```commandline
make revision
```
- Открытие базы данных внутри Docker-контейнера:
```commandline
make open_db
```

- Вывести список всех команд и их описание:
```commandline
make help
```
