you need to do something like this to snap the /app/dist dir out of the docker container:

```
docker cp <container_id>:/app/dist /mnt/c/Code/errbot/src/status_page/dist
```