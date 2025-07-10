# Lite Workflow

This project is a lightweight workflow management system.

## Requirements

- Python 3.12
- [uv](https://github.com/astral-sh/uv)

## Setup

1. **Install uv**

   If you don't have `uv` installed, you can install it with:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create a virtual environment**

   Create and activate a virtual environment using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   Install the required packages from `pyproject.toml`:
   ```bash
   uv pip install -e .
   ```

## Running the Project

Once the setup is complete, you can run the main application:

```bash
python main.py
```

