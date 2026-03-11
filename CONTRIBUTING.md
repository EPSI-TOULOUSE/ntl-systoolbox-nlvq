# Contributing

## Setup project

```shell
python -m venv ./venv
pip install '.[dev]'
```

```shell
python src/main.py
```

## Build binaries

```shell
pyinstaller src/main.py --onefile --name ntl
```
