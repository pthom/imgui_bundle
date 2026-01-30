---
name: review-book
description: Review a Jupyter Book by reading its _toc.yml and all referenced files, then provide a structured analysis
disable-model-invocation: true
argument-hint: [book-path]
---

# Review Jupyter Book

Review the Jupyter Book located at `$ARGUMENTS` (default: `docs/book` if no argument provided).

## Steps

1. **Read the table of contents**: Read `_toc.yml` in the book directory to understand the structure

2. **Parse the structure**: Extract all file references from the TOC, noting:
   - Parts/chapters organization
   - File paths (relative to book directory)
   - Any notebooks (.ipynb files)

3. **Read all files systematically**: Read each file in order, including:
   - The root file specified in `root:`
   - All chapter files in each part
   - Note: For .ipynb files, read them as notebooks

4. **Analyze and report**: Provide a structured report with:

   ### Structure Summary
   - Overview of parts and chapters
   - Total file count

   ### Quality Assessment
   For each major section:
   - Content completeness
   - Code example quality (Python/C++ parity)
   - Link validity (demo links, API references)

   ### Issues Found
   - Typos and grammatical errors
   - Broken or inconsistent links
   - Formatting problems
   - Missing content
   - Outdated information

   ### Suggestions
   - Improvements for clarity
   - Missing documentation
   - Structural improvements

## Notes

- Read files in parallel where possible to reduce time
- For large books, summarize rather than quote extensively
- Flag any files that fail to read
- Check for consistency in formatting patterns across similar pages
