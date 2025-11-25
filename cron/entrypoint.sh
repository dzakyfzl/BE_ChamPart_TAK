#!/bin/sh
if [ -z "$CRON_SECRET_KEY" ]; then
  echo "Error: CRON_SECRET_KEY tidak ditemukan!"
  exit 1
fi

sed "s|{{KEY}}|$CRON_SECRET_KEY|g" /app/crontab.template > /etc/crontabs/root


chmod 0644 /etc/crontabs/root


touch /var/log/cron.log

echo "Crontab berhasil dikonfigurasi dengan Environment Variable."
echo "Menjalankan Cron..."


exec "$@"