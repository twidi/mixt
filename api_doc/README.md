# API Doc generator

This directory holds the code that read the code of the mixt module, its docstring, typing annotations, etc, and render an HTML doc using mixt components created on purpose.

## Development

```bash
pip install mixt[doc]
```

## Render

To render the html/css/js files in a directory

```bash
python -m api_doc.export directory
```

The final directory where the doc have to be exported is ``docs``.

It can be done with:

```bash
make doc
```


## Serve

To server the html content on `localhost:8080`:

```bash
python -m api_doc.serve
```
