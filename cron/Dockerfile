FROM alpine:3.18


RUN apk add --no-cache curl

WORKDIR /app


COPY crontab.template /app/crontab.template
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["crond", "-f", "-l", "8"]