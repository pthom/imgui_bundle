#!/usr/bin/env bash

# You will need to install asciidoctor, asciidoctor-reducer, pandoc and pygments.rb
#     brew install asciidoctor
#     gem install asciidoctor-reducer
#     gem install asciidoctor-multipage
#     gem install pygments.rb
#     brew install pandoc

this_dir=$(dirname -- "$0")
doc_dir=$this_dir/..
repo_dir=$doc_dir/../../..
gh_pages_dir=$repo_dir/docs
cd "$doc_dir" || exit


# Generate preprocessed Readme.adoc for Github readme (env_gh_readme)
echo "generate Readme.adoc (for github)"
asciidoctor-reducer --attribute env_gh_readme=1 Readme_source.adoc -o Readme.adoc


# Generate a markdown doc for pypi  (env_pypi)
echo "Generating Readme_pypi.md (for pypi)"
asciidoctor -b docbook --attribute exclude_collapsible_details=1 --attribute env_pypi=1 Readme_source_pypi.adoc
pandoc -f docbook -t markdown_strict Readme_source_pypi.xml -o ../Readme_pypi.md


# Generate multipage html doc for github pages (env_gh_pages)
echo "Generating $gh_pages_dir/index.html (for github pages)"
cp Readme_source.adoc index.adoc  # first copy to index.adoc, so that the main page is index.html
asciidoctor-multipage --attribute env_gh_pages=1 -D $gh_pages_dir index.adoc
rm index.adoc
