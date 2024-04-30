cd ..
del /s /f /q dist
python -m build
python -m twine upload --repository pypi dist/*