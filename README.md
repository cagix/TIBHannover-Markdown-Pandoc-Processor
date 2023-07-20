# Markdown Pandoc Processor

Docker container for Pandoc conversion of Markdown files to various output formats including preparation for OER repositories and Google Search.

## Features

* builds various output files via pandoc like PDF, HTML, EPUB, ...
* use multiple markdown files as input
* creates metadata in HTML headers for OER repositories and Google search (based on schema.org)
* converts gitlab math formulas to latex math formulas
* images from wikimedia commons will get automatically a license notice
* license notice for overall content is added to the end of the document, depending on the license in _metadata.yml_
* generate a landing page about the resource

Example project: TODO

## Input
 * documents in markdown-format
 * meta-data in file _metadata.yml_
     * mandatory fields: _license_, _creator -> givenName_, _creator -> familyName_, _name_, _inLanguage_

## Options

* You can use the following options in file _config.yml_ (see also _default-config.yml_)
    * **output** - list of output-files to generate
        * **format** - format of the output like epub, html, pdf, asciidoc
    * **generate_landingpage** - generate a html-landing-page (true/false)
    * **generate_reuse_note** - generate the reuse note at the end of the document
    * **content_files** - (optional, default: use alphabetical order of all available markdown-files without README.md) ordered list of markdown-files to use as input. If the default alphabetical sort order is used, the configuration does not have to be adjusted for each new md file - however, the alphabetical sorting must be taken into account when naming the files, e.g. by using leading numbers in the file names (e.g. 01_introduction.md, 02_course.md, 03_appendix.md). If the sort order is defined via _content_files_, each new Markdown file must be added in the configuration - the naming of the files does not matter in this case.
* Styles
    * You can define your own css in file _pandoc.css_ in your markdown-input-directory. Default css from _default-pandoc.css_ is used if no such file exists.
* Environment variables
    * **OUTPUT_FILENAME** - (default: `document`) the base filename of generated documents (without extension). Generated and prepared documents will be available as _\<OUTPUT_FILENAME\>.\<extension\>_
    * **USER_AGENT** - set the user agent that is used by pandoc during creation of output files

## How To
### Set the order of content files
When creating your documents in different formats, the `Markdown Pandoc Processor` looks for Markdown (`.md`) files.

Your content files may look like this:

```
.
├── chapter01.md
├── chapter02.md
├── chapter03.md
└── chapter04.md
```

_(Note: the `README.md` files is always ignored.)_

In this case, the chapters are numbered and can be simply sorted alphabetically. This is the default behavior: if the optional configuration parameter `content_files` is not supplied, your `.md` files (excluding the `README.md`) are sorted alphabetically.

This also works with leading numbers:

```
.
├── 01_Introduction.md
├── 02_Course.md
└── 03_Appendix.md
```

This would result in exactly the same order:

1. Introduction
2. Course
3. Appendix

However, if your content files are not named using either approach, the ordering might be wrong, e.g. if you have files like this and want them in this order:

```
.
├── Introduction.md
├── Course.md
└── Appendix.md
```

The `Markdown Pandoc Processor` would still order them alphabetically, leading to the following order:

1. Appendix
2. Course
3. Introduction

To prevent this, set the order of the content files manually in `config.yml`:

```
content_files:
  - Introduction.md
  - Course.md
  - Appendix.md
```

The `Markdown Pandoc Processor` will arrange the files in the specified order.

1. Introduction
2. Course
3. Appendix


Please note that if you use the `content_files` configuration, only the files that are listed will be included; all the files not listed will be ignored.

### Link to sections and other content files
It is not only possible to create links to different sections, it is also possible to link to other files. For this, use the anchor of the section heading.

For example, if we have a section starting with the level 2 heading "Section Heading Name":

`## Section Heading Name`

Our anchor will be `#section-heading-name` (with one `#` regardless of the heading level).

To link to a section within the same document:

`[Link to section](#section-heading-name)`

Linking to a section of a different document, e.g. `chapter01.md`:

`[Link to section in chapter 1](chapter01.md#section-heading-name)`

The anchors consist of a `#` and the text of the heading, with some transformations like:

* whitespaces are replaced with -
* all text is transformed to lowercase
* characters that are not letters or numbers are either ignored or replaced

The easiest way to get an anchor is to use a text editor that supports Markdown and autocompletes the links for you, or, if the content files are already on Git, view the anchors by hovering over the heading.
On the left, there will appear a link symbol.
This link includes the anchor on the end starting with the `#`.

## Usage (CLI)

Use your current directory as a docker volume, that includes your markdown documents and your _metadata.yml_ and set this volume in the environment variable _MD_INPUT_DIR_.

```
docker run -it --volume "`pwd`:/data" -e MD_INPUT_DIR=/data registry.gitlab.com/tibhannover/oer/markdown-pandoc-processor
```

## Usage (GitHub Actions)

Your github project has to contain your markdown documents, your _metadata.yml_ and a _.github/workflows/_ workflow

You clould also use one of our templates to create the basic file structure automatically, for example https://github.com/TIBHannover/markdown-documents-template

<details><summary>Example workflow <i>publish-documents.yml</></summary>

```
name: Publish documents
on: [push]

env:
  OUTPUT_FILENAME: "document"
  USER_AGENT: "$GITHUB_REPOSITORY ($GITHUB_SERVER_URL/$GITHUB_REPOSITORY)"

jobs:
  prepare-and-build-documents:
    runs-on: ubuntu-latest
    container:
      image: registry.gitlab.com/tibhannover/oer/markdown-pandoc-processor
    steps:
      - uses: actions/checkout@v3
      - run: |
          /build/process.sh
          ls -l
          mkdir .public
          cp -r * .public
          mv .public public
      - uses: actions/upload-pages-artifact@v1
        with:
          path: ./public

  # Deployment job
  deploy:
    # Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub Pages
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: prepare-and-build-documents
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

</details>

## Usage (GitLab-CI)

Your gitlab project has to contain your markdown documents, your _metadata.yml_ and a _.gitlab-ci.yml_

<details><summary>Example <i>.gitlab-ci.yml</i></summary>

```
variables:
  OUTPUT_FILENAME: "document"
  USER_AGENT: "$CI_PROJECT_TITLE ($CI_PROJECT_URL)"

prepare-and-build-documents:
  image:
    name: registry.gitlab.com/tibhannover/oer/markdown-pandoc-processor
    entrypoint: [""]
  stage: build
  script:
    - /build/process.sh
    - mkdir .public
    - cp -r * .public
    - mv .public public
  artifacts:
    paths:
      - public
  only:
  - master

```
</details>
