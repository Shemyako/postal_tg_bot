# postal_tg_bot
Tg bot in POSTAL system

## Бот
### Регистрация
![image](https://user-images.githubusercontent.com/52855609/221214789-01fdd793-51ff-4c37-894b-96a98f24cf9d.png)
### Добавление почты
![image](https://user-images.githubusercontent.com/52855609/221215025-95272a03-a655-42bc-b6c3-f26d445ae2c7.png)
### Удаление почты (пока не готово)
![image](https://user-images.githubusercontent.com/52855609/221217579-f965105f-27e7-4683-9b12-2f7fa4038c49.png)
### Список почт
![image](https://user-images.githubusercontent.com/52855609/221217673-3776adb9-fe6f-437c-af69-b8d825219583.png)
### Получение письма из mail.ru

## Переменные окружения
`DATABASE_URL` - ссылка подключения к бд

`BOT_TOKEN` - токен бота

`DOMEN` - домен, под которым находятся почты

`LOG_LEVEL` - уровень логирования

## [Почтовая часть](https://github.com/Shemyako/postal_mail_server):
Получение письма, его парсинг, если есть получатель, то добавляем в очередь и пересылаем

