v2.1.0

gen-chglog command:

```
python gen-chglog.py {version} -r README.md -r src/bean_tools/__init__.py -r pyproject.toml
# Undo commit and build to include with commit
poetry build
```
