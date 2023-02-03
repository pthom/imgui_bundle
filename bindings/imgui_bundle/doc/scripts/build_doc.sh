#!/usr/bin/env bash

# You will need to install asciidoctor, asciidoctor-reducer, pandoc and pygments.rb
#     brew install asciidoctor
#     gem install asciidoctor-reducer
#     gem install pygments.rb
#     brew install pandoc

this_dir=$(dirname -- "$0")
doc_dir=$this_dir/..
repo_dir=$doc_dir/../../../
gh_pages_dir=$repo_dir/docs
cd "$doc_dir" || exit

# Generate preprocessed Readme.adoc for Github readme (env_gh_readme)
echo "generate Readme.adoc (for github)"
asciidoctor-reducer --attribute env_gh_readme=1 Readme_source.adoc -o Readme.adoc

# Generate preprocessed faq.adoc for Github readme (env_gh_readme)
echo "generate faq.adoc (for github)"
asciidoctor-reducer --attribute env_gh_readme=1 faq_source.adoc -o faq.adoc


# Generate a markdown doc for pypi  (env_pypi)
echo "Generating Readme_pypi.md (for pypi)"
asciidoctor -b docbook --attribute exclude_collapsible_details=1 --attribute env_pypi=1 Readme_source.adoc
pandoc -f docbook -t markdown_strict Readme_source.xml -o ../Readme_pypi.md

# Generate html doc for github pages (env_gh_pages)
echo "Generating $gh_pages_dir/index.html (for github pages)"
asciidoctor --attribute env_gh_pages=1 Readme_source.adoc -o $gh_pages_dir/index.html
asciidoctor --attribute env_gh_pages=1 faq_source.adoc -o $gh_pages_dir/faq.html

# Generate markdowns doc for demo_imgui_bundle (env_demo_markdown)
echo "Generate markdowns doc for demo_imgui_bundle"
for doc_file in imgui_bundle_demo_parts/*.adoc; do
asciidoctor --attribute env_demo_markdown=1 -b docbook $doc_file -o $doc_file.xml
# Note: -t markdown-header_attributes means "output markdown, without the extension header_attributes"
# (see extensions here: https://boisgera.github.io/pandoc/markdown/#extension-auto_identifiers
#  and https://pandoc.org/MANUAL.html#general-options)
pandoc -f docbook -t markdown-header_attributes+escaped_line_breaks --columns=2000 $doc_file.xml -o $doc_file.md
done
