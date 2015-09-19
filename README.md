Execution of docker
```
docker run -d -P  \
    -v `pwd`/config.py:/usr/src/app/config.py \
    -v /tmp/gallerydb/:/tmp/gallerydb \
    -v /tmp/files/:/tmp/files \
    --name tgbot zunbado/gallerybot
```
