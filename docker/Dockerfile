FROM yoyonel/python:3.7.3-slim-stretch-grpc1.21.1

COPY . /app

WORKDIR /app

ARG PYPI_SERVER=https://pypi.org/simple/

ARG APP_ENTRY_POINT=pyconfr_2019_grpc_nlp_server_tweet_features
ENV APP_ENTRY_POINT ${APP_ENTRY_POINT}
ARG APP_EXPOSE_PORT=50051
ENV APP_EXPOSE_PORT ${APP_EXPORT_PORT}

RUN pip install --upgrade pip && \
    pip install \
        --extra-index-url ${PYPI_SERVER} \
        $(find dist -maxdepth 1 -type f -printf "%T@ %p\n" | sort -nr | head -1 | cut -d ' ' -f 2) && \
        python -m spacy download en_core_web_sm && \
    rm -rf ~/.cache/pip

EXPOSE ${APP_EXPOSE_PORT}
CMD ${APP_ENTRY_POINT}