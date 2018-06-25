# API Doc generator

This directory holds the code that read the code of the mixt module, its docstring, typing annotations, etc, and render an HTML doc using mixt components created on purpose.

## Development

```bash
pip install mixt[doc]
```

## Render

To render the single html content:

```bash
python -m api_doc.app
```

# Serve

To server the html content on `localhost:8080`:

```bash
python -m api_doc.serve
```
