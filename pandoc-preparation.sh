#!/bin/sh

WORKDIR=/build

if [ -n "$MD_INPUT_DIR" ]; then
  echo "using input directory $MD_INPUT_DIR"
  cd "$MD_INPUT_DIR" || exit 1
fi
pwd
ls -l

if [ ! -f "metadata.yml" ]; then
	echo "'metadata.yml' not found."
	exit 1
fi

if [ ! -f "pandoc.css" ]; then
	echo "Using default pandoc.css"
	cp $WORKDIR/default-pandoc.css pandoc.css
fi
if [ ! -f "config.yml" ]; then
	echo "Using default config.yml"
	cp $WORKDIR/default-config.yml config.yml
fi
if [ ! -f "template-landingpage.html" ]; then
  cp $WORKDIR/template-landingpage.html .template-landingpage.html
fi
cp $WORKDIR/template-landingpage-de.yml .template-landingpage-de.yml
cp $WORKDIR/template-landingpage-en.yml .template-landingpage-en.yml

if [ ! "$(yq '. | has("url")' metadata.yml)" = true ]; then
  test -n "$CI_PROJECT_URL" && yq -i -Y ".url = \"$CI_PROJECT_URL\"" metadata.yml
  test -n "$GITHUB_ACTIONS" && yq -i -Y ".url = \"${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}\"" metadata.yml
fi
if [ ! "$(yq '. | has("datePublished")' metadata.yml)" = true ]; then
  DATE_PUBLISHED=$(date -u +"%Y-%m-%d %H:%M")
  yq -i -Y ".datePublished = \"$DATE_PUBLISHED\"" metadata.yml
fi
if [ "$(yq '. | has("content_files")' config.yml)" = true ]; then
  CONTENT_FILES=$(yq -r '."content_files"[]' config.yml | tr '\n' ' ')
else
  CONTENT_FILES=$(ls -1 *.md | grep -v -e README.md | tr '\n' ' ')
fi
echo "Using input files $CONTENT_FILES"
pandoc -f markdown -t markdown -s -o .pd-preparation-merged.md --file-scope $CONTENT_FILES

python3 $WORKDIR/create-image-license-reference.py .pd-preparation-merged.md
python3 $WORKDIR/create-metadata-files.py
python3 $WORKDIR/create-toc.py .pd-preparation-tagged.md

sed -e ':a' -e 'N' -e '$!ba' -e "s/\`\`\`math\n\([^$]*\)\n\`\`\`/\$\$\1\$\$/g" .pd-preparation-tagged.md > pd-preparation-tempfile1.md
sed -e ':a' -e 'N' -e '$!ba' -e "s/\\$\`\([^\`]*\)\`\\$/\$\1\$/g" pd-preparation-tempfile1.md > .pd-preparation-prepared.md

rm pd-preparation-tempfile1.md
rm .pd-preparation-tagged.md

python3 $WORKDIR/create-pandoc-script.py .pd-preparation-prepared.md
