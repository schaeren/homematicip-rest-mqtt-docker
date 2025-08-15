### Configuration file `logging.json`

```
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s : %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "handlers": {
        "stdout": {
            "level": "INFO",
            "formatter": "simple",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "level": "DEBUG",
            "formatter": "simple",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/log/hmip2mqtt.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": ["stdout", "file"]
        }
    }
}
```

This file configures the Python logger used in the container. The [offical documentation](https://docs.python.org/3/library/logging.config.html#) may be quite hard to read, but there exist other inofficial sources (I used e.g. [this video](https://www.youtube.com/watch?v=9L77QExPmI0), but it's mainly for developers). 

This example defines two logging outputs (handlers):
- `simple` writes to the standard output, i.e. to the Docker log. You can see it with the command `docker logs <container>`. Logging messages are filtered to `INFO`, i.e. no `DEBUG` messages.
- `file` writes to the file `/log/hmip2mqtt.log`, including `DEBUG` messages. As soon as the size of 10 MBytes is reached, a new file is created. The last 5 files are retained, the others are deleted. To make this file accessible outside the container, it must be assigned to an external file in `compose.yaml` under `volumes`.

Remark:
If no external logging configuration file is mapped in `compose.yaml`, the default config file in the container is used. This one writes only to the standard output, but including the DEBUG messages.