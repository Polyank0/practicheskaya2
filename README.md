# Граф зависимостей пакетов Ubuntu. Вариант №27

Практическая работа №2 по дисциплине «Конфигурационное управление».

Состояние: выполнен этап 1 из 5 (минимальный прототип).

## Общее описание

Консольная программа для анализа зависимостей пакетов Ubuntu (apt).
Менеджеры пакетов и сторонние библиотеки не используются: описание
пакетов скачивается и разбирается средствами стандартной библиотеки Python.

## Функции и настройки

| Параметр | Значение | По умолчанию |
|---|---|---|
| `--package ИМЯ` | имя анализируемого пакета | обязательный |
| `--repository АДРЕС` | URL файла `Packages` или `Packages.gz`; в тестовом режиме путь к файлу | обязательный |
| `--test-mode` | режим работы с тестовым репозиторием | выключен |
| `--output ФАЙЛ` | имя файла с изображением графа, `.svg` | `graph.svg` |
| `--max-depth ЧИСЛО` | максимальная глубина анализа | `10` |
| `--filter ТЕКСТ` | исключить пакеты, имя которых содержит подстроку | пусто |

Каждый параметр проверяется; при ошибке программа печатает `error: ...`
и завершается с кодом 1.

На этом этапе программа выводит все параметры в формате `ключ=значение`.

### Исходные файлы

| Файл | Назначение |
|---|---|
| `src/main.py` | точка входа |
| `src/options.py` | параметры и их проверка |
| `src/errors.py` | тип ошибки `ToolError` |

## Сборка и запуск тестов

Сборка не нужна, требуется Python 3.9 или новее.

```bat
rem Windows
run.bat --package bash --repository URL
test.bat
```

```bash
# Linux, macOS
./run.sh --package bash --repository URL
python3 -m unittest discover -s tests -t . -v
```

Адрес для Ubuntu 22.04:

```
http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
```

Демонстрация (файлы `.bat` и `.sh`):

- `examples/demo_options` — все параметры и ошибки в них;

## Примеры использования

```
$ ./run.sh --package bash --repository URL --max-depth 2
package=bash
repository=URL
test_mode=false
output=graph.svg
max_depth=2
filter=

$ ./run.sh --package bash --repository URL --max-depth abc
error: --max-depth: 'abc' must be a positive integer
```
