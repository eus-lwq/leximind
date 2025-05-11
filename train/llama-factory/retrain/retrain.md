0. sudo systemctl enable --now cron
1. crontab -e
2. 0 * * * * /bin/bash $HOME/llama-factory/auto_retrain.sh >> $HOME/llama-factory/logs/auto_retrain.log 2>&1

