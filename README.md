# Markdown Pandoc Processor

Docker container for preparation of pandoc conversion of git courses for OER repositories and Google Search.

* course format: markdown
* creates lrmi tags in _metadata.json_ for html output (https://www.dublincore.org/specifications/lrmi/lrmi_1/)
* creates _title.txt_ with metadata
* converts gitlab math formulas to latex math formulas
* uses default _pandoc.css_, if no _pandoc.css_ exists
* prepared course will be available in _course-prepared.md_
* images from wikimedia commons will get automatically a license notice
* license notice for overall content is added to the end of the document, depending on the license in _metadata.yml_

Example project: https://gitlab.com/TIBHannover/oer/course-metadata-test

## Input
 * course in markdown-format
 * meta-data in file _metadata.yml_
     * mandatory fields: _license_, _creator -> givenName_, _creator -> familyName_, _name_, _inLanguage_

## Options

* You can use the following options in file _config.yml_ (see also _default-config.yml_)
    * **output** - define which output-files to generate
        * **format** - format of the output like epub, html, pdf, ...
    * **generate_landingpage** - generate a html-landing-page (true/false)
    * **reuse_note**
        * **generate_license_note** - generate the license-note at the document-end in the "reuse note"-section (true/false)
        * **generate_sources_note** - generate the link to the gitlab source at the document-end in the "reuse note"-section (true/false)
        * **generate_tullu_tasll_note** - generate the TULLU / TASSL note at the document-end in the "reuse note"-section (true/false)
* When you call `pandoc-preparation.sh` you can use the following options
    * **[your-markdown-course]** - required, name of your markdown course (without .md extension)
    * **--no-license** - (DEPRECATED - use **reuse_note.generate_license_note** in _config.yml_ instead) optional, deactivate generation of link-hint at the document-end (Hinweis zur Nachnutzung)
    * **--no-sources** - (DEPRECATED - use **reuse_note.generate_sources_note** in _config.yml_ instead) optional, deactivate generation of link to the gitlab source at the document-end (Hinweis zur Nachnutzung)
    * **--no-tullu** - (DEPRECATED - use **reuse_note.generate_tullu_tasll_note** in _config.yml_ instead) optional, deactivate generation of TULLU hint at the document-end (Hinweis zur Nachnutzung)

## Usage (CLI)

Use your current directory as a docker volume, that includes your markdown course and your _metadata.yml_ and set this volume in the environment variable _COURSE_DIR_.

```
docker run -it --volume "`pwd`:/data" -e COURSE_DIR=/data registry.gitlab.com/tibhannover/oer/markdown-pandoc-processor <your-markdown-course>
```

## Usage (GitHub Actions)

Your github project has to contain your markdown course, your _metadata.yml_ and a _.github/workflows/_ workflow

You clould also use one of our templates to create the basic file structure automatically, for example https://github.com/TIBHannover/markdown-documents-template

<details><summary>Example workflow <i>publish-documents.yml</></summary>

```
name: Publish documents
on: [push]

env:
  MARKDOWN_SOURCE_FILENAME: "course"
  OUTPUT_FILENAME: "document"
  USER_AGENT: "$GITHUB_REPOSITORY ($GITHUB_SERVER_URL/$GITHUB_REPOSITORY)"

jobs:
  prepare-pandoc:
    runs-on: ubuntu-latest
    container:
      image: registry.gitlab.com/tibhannover/oer/markdown-pandoc-processor
    steps:
      - uses: actions/checkout@v3
      - run: /build/pandoc-preparation.sh $MARKDOWN_SOURCE_FILENAME
      - uses: actions/upload-artifact@v3
        with:
          name: prepared-data
          path: ${{ github.workspace }}
          retention-days: 1

  build-documents:
    runs-on: ubuntu-latest
    container:
      image: pandoc/latex:3.1.1
    needs: prepare-pandoc
    steps:
      - uses: actions/download-artifact@v3
        with:
          name: prepared-data
      - run: |
          ls -l
          ./.pandoc-generate.sh
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
    needs: build-documents
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

</details>

## Usage (GitLab-CI)

Your gitlab project has to contain your markdown course, your _metadata.yml_ and a _.gitlab-ci.yml_

<details><summary>Example <i>.gitlab-ci.yml</i></summary>

```
variables:
  MARKDOWN_SOURCE_FILENAME: "course"
  OUTPUT_FILENAME: "document"
  USER_AGENT: "$CI_PROJECT_TITLE ($CI_PROJECT_URL)"

preparepandoc:
  image:
    name: registry.gitlab.com/tibhannover/oer/markdown-pandoc-processor
    entrypoint: [""]
  stage: build
  script:
    - /build/pandoc-preparation.sh <your-markdown-course-file>
  artifacts:
    untracked: true
    expire_in: 5min

pages:
  image:
    name: pandoc/latex:3.1.1
    entrypoint: [""]
  stage: deploy
  dependencies:
    - preparepandoc
  script:
    - ./.pandoc-generate.sh
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
