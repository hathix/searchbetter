# How to push to PyPI

Just replace the `$$` with the appropriate text.

```sh
git tag $$ -m "$$"
git push --tags origin master
python setup.py register -r pypi
python setup.py sdist upload -r pypi
```
