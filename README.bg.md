[![WurzelimperiumBot Runner](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml/badge.svg)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/python-app.yml)
[![WurzelimperiumBot Binary Compile and Release](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/release2binary.yml/badge.svg)](https://github.com/MasterZydra/WurzelimperiumBot/actions/workflows/release2binary.yml)
[![Python 3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)
![GitHub](https://img.shields.io/github/license/MasterZydra/WurzelimperiumBot)

A forked from [MrFlamez/Wurzelimperium-Bot](https://github.com/MrFlamez/Wurzelimperium-Bot)

*Read this in other languages: [English](README.md), [German](README.de.md), [Bulgarian](README.bg.md)*

# Wurzelimperium-Bot
Бот за играта Wurzelimperium на Upjers. Насладете се на безплатни премиум опции благодарение на този бот.

**Съдържание**
- [Употреба](#употреба)
- [Опции](#опции)
- [Инсталация](#инсталация)
- [Инсталация на Линукс](#инсталацияналинукс)

## Употреба
Използването на този бот е възможно в различни ситуации:
- **Скрипт**:  
Като [example.py](./example.py) Задачите могат да бъдат създавани като скриптове или да се изпълняват автоматично на вашия компютър.
- **Автоматично**:  
Подобно на използването на скрипт, можете да решавате много по-сложни задачи, които могат да се изпълняват например от GitHub Actions. Научете повече. [automated_script.py](./automated_script.py)
- **Интерактивно**:  
С програмата [console.py](./console.py) Можете да изпълнявате действия чрез използване на входни данни `water` за да напоите всичките градини.

Ако използвате [example.py](./example.py) и [console.py](./console.py) Необходимо е да редактирате файловете, които изпълнявате, и да въведете вашите данни за вход и регион на играта (език).

- **Автономен**:
Наличен е и самостоятелен изпълним файл за Windows. [Win32-CLI-Standalone](https://github.com/MasterZydra/WurzelimperiumBot/releases/)

## Опции
- Вход без браузър
- Напълно автоматизирано поливане на градини.
- Автоматизирано засаждане и прибиране на реколтата.
- Автоматизирана обработка на Wimps в градините. Можете да зададете минималната... (нужни са повече подробности за това какво да се зададе минимално) наличност в бележките на акаунта. Напр. minStock: 100 или minStock(Apple): 200
- Можете да деактивирате бота, като напишете `stopWIB` в бележника.
- Автоматично получаване на ежедневния бонус за влизане.

## Инсталация
**Използва venv**  <small>[askUbuntu](https://askubuntu.com/questions/1465218/pip-error-on-ubuntu-externally-managed-environment-%C3%97-this-environment-is-extern)</small>  
1. Инсталация на venv: `sudo apt install python3-venv`  
2. Създаване на виртуална среда в папка env: `python3 -m venv env`
3. Стартиране на виртуалната среда: `source env/bin/activate`  
4. Инсталация на изисквания: `pip install -r ./requirements.txt`

**Изисквания:** [Python 3](https://www.python.org/download/releases/3.0/)
1. Инсталация на изисквания:  
`pip install -r ./requirements.txt`
2. Задайте данни за вход ([example.py](./example.py) и/или [console.py](./console.py)).  
   Със автоматичният скрипт [automated_script.py](./automated_script.py) трябва да добавите данните като флаг: </br>
   `python3 ./automated_script.py <server-nr> <username> <password> <lang>` </br>
   Пример: python3 ./automated_script.py 12 FooBar password1337 en
3. Стартирайте скрипта.

## Инсталация на Линукс
Инсталационнипт скрипт за Линукс се намира в клон Юникс [`unix`](https://github.com/MasterZydra/WurzelimperiumBot/tree/unix).  
Благодарности към [xRuffKez](https://github.com/xRuffKez) за разработката на скрипта.
