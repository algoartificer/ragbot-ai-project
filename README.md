# ragbot-ai-project
OpenAI API project with knowledge base

## Setup

Before running `prototype.py` ensure that your OpenAI API key is available to
the application. The script will look for either `CHROMA_OPENAI_API_KEY` (the
default expected by `chromadb`) or `OPENAI_API_KEY`. Define one of these
environment variables with your key, for example:

```bash
export OPENAI_API_KEY="sk-..."
```

### Steps
Activate the virtual environment by executing `venv\Scripts\activate` (or the
equivalent command on your platform).
