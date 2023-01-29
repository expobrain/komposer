mypy:
	poetry run mypy .

test:
	poetry run pytest -x --cov=core --cov=komposer --cov-fail-under=90

serve:
	poetry run mkdocs serve
