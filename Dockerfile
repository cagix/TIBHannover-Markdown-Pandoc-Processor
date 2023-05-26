FROM python:3-slim-bullseye

RUN pip install PyYAML
RUN pip install requests
RUN pip install yq
RUN apt update && apt install -y jq
RUN pip install Jinja2

ENV COURSE_DIR=
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

ENTRYPOINT ["/build/pandoc-preparation.sh"]
