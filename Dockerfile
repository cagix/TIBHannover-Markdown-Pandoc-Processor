FROM pandoc/latex:3.1.1

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install PyYAML
RUN pip3 install requests
RUN pip3 install yq
RUN apk add --update jq
RUN pip3 install Jinja2

ENV MD_INPUT_DIR=
WORKDIR /build

COPY helper.py .
COPY create-image-license-reference.py .
COPY create-lrmi-json-tag.py . 
COPY pandoc-preparation.sh .
COPY default-pandoc.css .
COPY default-config.yml .
COPY template-landingpage.html .
COPY create-pandoc-script.py .
COPY pandoc-generate.sh.j2 .
COPY process.sh .

ENTRYPOINT ["/build/process.sh"]
