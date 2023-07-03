FROM python:3.10

# Set arguments
ARG USERNAME=immobyte-developer
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG APP_PATH=/opt/immobyte

# Create non-root user
RUN groupadd --gid $USER_GID $USERNAME
RUN useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Set environment variables  
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Create directory
WORKDIR ${APP_PATH}

COPY --chown=$USERNAME:$USERNAME requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=$USERNAME:$USERNAME . .
 
# Use non-root user
USER $USERNAME

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]