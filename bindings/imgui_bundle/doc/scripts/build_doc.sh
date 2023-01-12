#!/usr/bin/env bash

# You will need to install asciidoctor, asciidoctor-reducer and pandoc:
#     brew install asciidoctor
#     gem install asciidoctor-reducer
#     brew install pandoc

this_dir=$(dirname -- "$0")
doc_dir=$this_dir/..
repo_dir=$doc_dir/../../../
gh_pages_dir=$repo_dir/docs
cd $doc_dir

# asciidoctor-reducer will preprocess the includes, so that github display the readme nicely
echo "generate Readme.adoc (for github)"
asciidoctor-reducer Readme_source.adoc -o Readme.adoc

# Generate a markdown doc for pypi
echo "Generating Readme_pypi.md (for pypi)"
asciidoctor -b docbook --attribute env_pypi=1 Readme_source.adoc
pandoc -f docbook -t markdown_strict Readme_source.xml -o ../Readme_pypi.md

# Generate html doc for github pages
echo "Generating $gh_pages_dir/index.html (for github pages)"
asciidoctor --attribute env_gh_pages=1 Readme_source.adoc -o $gh_pages_dir/index.html
