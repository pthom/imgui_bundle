# Build and deploy to pypi:

````
python3 -m build --wheel  --sdist . 
python3 -m build --sdist .

# or 
python3 -m build  .

# then

twine upload dist/*
````

login = __token__
password = ...api_token...

