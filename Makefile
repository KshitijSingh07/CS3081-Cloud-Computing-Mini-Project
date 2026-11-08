PYTHON ?= python
CONFIG ?= training/config.yaml
SUBSET ?=

.PHONY: lint test clean train train-smoke label-clean

lint:
	ruff check worker training service tests scripts

test:
	pytest -q

clean:
	rm -f results/teacher-shard-*.jsonl data/train.jsonl data/train.sha256

train:
	$(PYTHON) training/train.py --config $(CONFIG) $(if $(SUBSET),--subset $(SUBSET),)

train-smoke:
	$(PYTHON) training/train.py --config $(CONFIG) --subset 50

label-clean:
	$(PYTHON) worker/clean.py results/teacher-shard-0.jsonl results/teacher-shard-1.jsonl
