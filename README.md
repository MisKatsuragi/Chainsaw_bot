# This Chainsaw man VK bot

## Для работы

1. Установить VS Code
2. Установить Python 3+
3. Установить плагины/расширения в VS Code extentions:

Python
Pylance
DotENV (для виртуальной среды)
autoDicstring - Python

Остальное для гита и прочих прелестей по усмотрению

## Установка окружение ВК в терминале

Основно:
Из файла, одной командой сразу всё:
pip install -r requirements.txt

По отдельности:
python3 -m pip install vk_api python-dotenv
py -m pip install openpyxl (для экселя)

Если будет ругаться выставить политику для скриптов:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

В конце можно заморозить конфигу среды. Вызывать из дирректории проекта.
python3 -m pip freeze > requirements.txt

Если нет желанию устанавливать окружение в системную среду можно использовать venv

В дирректории проекта:

python -m venv venv
venv\Scripts\activate
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

Далее перейти в созданную venv папку. Установить библиотеки.
pip install vk_api
pip install vkbottle
pip install requests python-dotenv
