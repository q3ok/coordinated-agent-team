# Function Plot CLI

## What it is

Function Plot CLI is a Python 3.11+ terminal application for plotting mathematical functions with a safe expression evaluator, evaluating `y` for a chosen `x`, marking the point on the graph, and exporting the latest render to a plain-text report.

## Features

- Numbered menu workflow: Plot, Evaluate/Mark, Recents, Export, Exit
- AST-whitelisted expression validation and evaluation (no raw `eval`)
- Deterministic terminal rendering with Unicode-first output and ASCII fallback
- Persistent recent functions stored in JSON (deduplicated, max 10)
- Marker overlay for evaluated points when inside viewport
- `.txt` export with metadata and rendered graph body

## Requirements

- Python `3.11+`
- `pip`
- Terminal window large enough for the default graph view (recommended: at least 80x24)

## Quickstart

Run from `demo-function-plot-cli`:

```bash
python -m pip install -r requirements.txt
python -m function_plot_cli.cli
```

Main menu options:

1. Plot function
2. Evaluate y for x and mark point
3. Show recent plots
4. Export current plot to file
5. Exit

## Allowed expression syntax

- Operators: `+`, `-`, `*`, `/`, `**`
- Variable: `x`
- Functions: `sin`, `cos`, `tan`, `sqrt`, `log`, `exp`
- Constants: `pi`, `e`

Unsupported examples: `__import__`, attribute access, indexing, comprehensions, lambdas.

## Scripts

- Test:

```bash
python -m pytest -q
```

- Build package (optional, requires `build`):

```bash
python -m pip install build
python -m build
```

- Lint:

No dedicated lint script is configured for this demo package.

## Project structure

```text
demo-function-plot-cli/
	function_plot_cli/
		cli.py
		config.py
		errors.py
		exporter.py
		expression.py
		input_parser.py
		models.py
		plotting.py
		renderer.py
		storage.py
		ui.py
	tests/
		test_cli_flow.py
		test_exporter.py
		test_expression.py
		test_plotting.py
		test_renderer.py
		test_storage.py
	pyproject.toml
	requirements.txt
	README.md
```

## Troubleshooting

- `No active function. Plot a function first.`: select menu option 1 before option 2.
- `No rendered plot available. Plot a function first.`: export requires at least one successful plot.
- Domain errors (for example `sqrt(-1)` or `log(0)`): use values and ranges valid in real numbers.
- Empty recents or recents reset: missing/corrupt recents JSON is handled by fallback to empty history.
- Export write failure: verify the output path is writable and ends with `.txt`.

## License

This repository is licensed under the GNU Affero General Public License v3. See the root [LICENSE](../LICENSE).
