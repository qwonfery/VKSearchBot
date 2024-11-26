class Message:
    API_KEY_INVITE = "Теперь отправь ключ API."
    FOLDER_ID_INVITE = "Теперь отправь идентификатор каталога (https://yandex.cloud/ru/docs/resource-manager/operations/folder/get-id#console_1)"
    DOMAINS_INVITE = "Теперь отправь домен или домены, по которым мы будем смотреть позиции (разделите домены запятой)."
    PROCESS_INFO = "Запрос получен, обрабатываю"


class BotMessage(Message):
    QUERY_INVITE = "Привет! Отправьте мне CSV/TXT файл с запросами или строку с запросами."


class CLIMessage(Message):
    QUERY_INVITE = "Привет! Отправь мне название CSV/TXT файла с запросами. Он должен быть в той же папке что и скрипт."
