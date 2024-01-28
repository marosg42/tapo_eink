#### Note to myself

- Font.ttc missing

- list.yaml is needed

```
- ip: P115-1.lan
  threshold_up: 10.0
  threshold_down: 6.0
- ip: P115-2.lan
  threshold_up: 10.0
  threshold_down: 3.0
- ip: P115-3.lan
  threshold_up: 5.0
  threshold_down: 1.0
  below_threshold_max_count: 11
```

- env-file is needed

```
TPLINK_LOGIN=
TPLINK_PASSWORD=
TELEGRAM_BOT_ID=
TELEGRAM_SEND_TO=
```


`docker run -d --name tapo_eink  --env-file env-file -v /home/ubuntu/eink/list.yaml:/code/list.yaml -v /home/ubuntu/pictures:/code/pictures --privileged -v /dev/mem:/dev/mem --restart unless-stopped tapo_eink`
