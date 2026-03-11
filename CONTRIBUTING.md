# Contributing

## Setup project

```shell
python -m venv ./venv
pip install '.[dev]'
```

```shell
python -m src.main
```

## Build docker image

```shell
docker build -t ntl .
```

## Build binaries

```shell
pyinstaller src/main.py --onefile --name ntl
```
