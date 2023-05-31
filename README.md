# Markdown Pandoc Processor

Docker container for Pandoc conversion of Markdown files to various output formats including preparation for OER repositories and Google Search.

* input format: markdown
* creates lrmi tags in _metadata.json_ for html output (https://www.dublincore.org/specifications/lrmi/lrmi_1/)
* creates _title.txt_ with metadata
* converts gitlab math formulas to latex math formulas
* uses default _pandoc.css_, if no _pandoc.css_ exists
* generated and prepared documents will be available as _\<OUTPUT_FILENAME\>.\<extension\>_
* images from wikimedia commons will get automatically a license notice
* license notice for overall content is added to the end of the document, depending on the license in _metadata.yml_
* builds various output files via pandoc like PDF, HTML, ...

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
    * **content_files** - (optional, default: use alphabetical order of all available markdown-files without README.md) ordered list of markdown-files to use as input.
    
    If the default alphabetical sort order is used, the configuration does not have to be adjusted for each new md file - however, the alphabetical sorting must be taken into account when naming the files, e.g. by using leading numbers in the file names (e.g. 01_introduction.md, 02_course.md, 03_appendix.md). If the sort order is defined via _content_files_, each new Markdown file must be added in the configuration - the naming of the files does not matter in this case.
* Environment variables
    * **OUTPUT_FILENAME** - (default: `document`) the base filename of generated documents (without extension)
    * **USER_AGENT** - set the user agent that is used by pandoc during creation of output files

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
