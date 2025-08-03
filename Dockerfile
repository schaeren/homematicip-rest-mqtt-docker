FROM python:latest

# RUN groupadd -g 1000 app_group && \
#     useradd -m -u 1000 -g app_group app_user

# COPY --chown=1000:1000 . .
COPY . .

# RUN "chmod 755 /main.py"

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "./main.py" ]
