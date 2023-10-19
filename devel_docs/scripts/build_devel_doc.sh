#!/usr/bin/env bash

# You will need to install asciidoctor, asciidoctor-reducer, pandoc and pygments.rb
#     brew install asciidoctor
#     gem install asciidoctor-reducer
#     gem install asciidoctor-multipage
#     gem install pygments.rb
#     brew install pandoc

this_dir=$(dirname -- "$0")
docs_src=$this_dir/..
gh_devpages_dir=$this_dir/../../docs/devel_docs

echo "docs_src=docs_src"
echo "gh_devpages_dir=gh_devpages_dir"
#cd "develdoc_dir" || exit

# Generate single page html develdoc for github pages (env_gh_pages)
asciidoctor-multipage --attribute env_gh_pages=1 -D $gh_devpages_dir/ $docs_src/index.adoc
