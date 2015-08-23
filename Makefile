
clean: clean-eggs clean-build
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete

clean-eggs:
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

clean-api-doc:
	@rm -rf docs/modules/*

api-doc:
	@sphinx-apidoc -e -o docs/modules/ hystrix/

test:
	python setup.py test

release: clean
	git tag `python setup.py -q version`
	git push origin `python setup.py -q version`
	python setup.py sdist
	python setup.py bdist_wheel
	twine upload dist/*

rst:
	@pandoc --from=markdown --to=rst --output=README.rst README.md
