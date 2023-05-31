#!/bin/sh

MD_FILE=$1
WORKDIR=/build

shift
OPTIONS="$@"
if [ -n "$MD_INPUT_DIR" ]; then
  echo "using input directory $MD_INPUT_DIR"
  cd "$MD_INPUT_DIR" || exit 1
fi
pwd
ls -l

if [ ! -f "$MD_FILE".md ]; then
	echo "markdown file '$MD_FILE'.md not found."
	exit 1
elif [ ! -f "metadata.yml" ]; then
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

if [ ! "$(yq '. | has("url")' metadata.yml)" = true ]; then
  test -n "$CI_PROJECT_URL" && yq -i -Y ".url = \"$CI_PROJECT_URL\"" metadata.yml
  test -n "$GITHUB_ACTIONS" && yq -i -Y ".url = \"${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}\"" metadata.yml
fi
if [ ! "$(yq '. | has("datePublished")' metadata.yml)" = true ]; then
  DATE_PUBLISHED=$(date -u +"%Y-%m-%d %H:%M")
  yq -i -Y ".datePublished = \"$DATE_PUBLISHED\"" metadata.yml
fi

python3 $WORKDIR/create-image-license-reference.py $MD_FILE
python3 $WORKDIR/create-lrmi-json-tag.py

sed -e ':a' -e 'N' -e '$!ba' -e "s/\`\`\`math\n\([^$]*\)\n\`\`\`/\$\$\1\$\$/g" $MD_FILE-tagged.md > pd-preparation-tempfile1.md
sed -e ':a' -e 'N' -e '$!ba' -e "s/\\$\`\([^\`]*\)\`\\$/\$\1\$/g" pd-preparation-tempfile1.md > $MD_FILE-prepared.md

rm pd-preparation-tempfile1.md
rm $MD_FILE-tagged.md

python3 $WORKDIR/create-pandoc-script.py $MD_FILE-prepared.md
