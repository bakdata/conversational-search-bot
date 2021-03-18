# Conversational Search Bot

This is the code repo for a conversational search bot for book and movie recommendations. 
It enables natural language queries against Elasticsearch.

Read the accompanying blogpost here ...

## Useful commands

Train model

`rasa train`

To use Spacy models

```
pip install spacy
python -m spacy download en_core_web_md
python -m spacy link en_core_web_md en
```

Run action server locally

`rasa run actions`

Run action server from PyCharm

- New Python run configuration
- Module name: `rasa_sdk`
- Parameters: `--actions actions`

Run rasa shell

`rasa shell` or `rasa shell nlu`

Run tests

`rasa test`

Run cross validation

`rasa test nlu --nlu data/nlu.yml --cross-validation`

Build Docker image

`docker build . -t rasa-bot`

`docker tag rasa-bot:latest rasa-bot:0.0.1`

Add rasa helm repo

`helm repo add rasa-x https://rasahq.github.io/rasa-x-helm`

Install on local Kubernetes

`helm install --namespace rasa --values ./values.yaml rasa-demo rasa-x/rasa-x`
