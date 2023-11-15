FROM python:3.10

# Set arguments
ARG USERNAME=immobyte-developer
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG APP_PATH=/opt/immobyte
ARG ETC_PATH=/etc/apt/
ARG KEYRINGS_PATH=$ETC_PATH/keyrings
ARG NODE_MAJOR=20

# Create non-root user
RUN groupadd --gid $USER_GID $USERNAME
RUN useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Set environment variables  
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1
# Adds working directory to python path
ENV PYTHONPATH "${PYTHONPATH}:${APP_PATH}"

# Node.js
# Download and import the Nodesource GPG key
RUN apt-get update -qq && apt-get install -y ca-certificates curl gnupg
RUN mkdir -p $KEYRINGS_PATH
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o $KEYRINGS_PATH/nodesource.gpg
# Create deb repository
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee $ETC_PATH/sources.list.d/nodesource.list
# Run Update and Install
RUN apt-get update -qq && apt-get install -y nodejs

# Create directory
WORKDIR $APP_PATH

COPY --chown=$USERNAME:$USERNAME requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=$USERNAME:$USERNAME . .
 
# Use non-root user
USER $USERNAME

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "immobyte.wsgi"]
