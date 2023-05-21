FROM docker.io/ubuntu:22.04

ENV DEBIAN_FRONTEND="noninteractive"

COPY SALT-PROJECT-GPG-PUBKEY-2023.gpg /usr/share/keyrings/salt-keyring.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/salt-keyring.gpg arch=amd64] https://repo.saltproject.io/salt/py3/ubuntu/22.04/amd64/latest jammy main" \
	| tee /etc/apt/sources.list.d/salt.list

RUN apt-get update               \
	&& apt-get install            \
			--yes                   \
			--quiet                 \
			--no-install-recommends \
		apt-transport-https        \
		ca-certificates            \
	&& apt-get update             \
	&& apt-get install            \
			--yes                   \
			--quiet                 \
			--no-install-recommends \
		openssh-server             \
		python3                    \
		salt-ssh                   \
		whois                      \
                                 \
   && useradd -m -p "$(echo 'testpass' | mkpasswd -sm sha-512)" testuser \
   && mkdir -p /run/sshd                                                 \
                                 \
   && apt-get clean --yes all    \
   && apt-get autoclean --yes    \
   && apt-get autopurge --yes    \
   && rm --recursive --force /var/lib/apt/lists/*

LABEL maintainer="scheatkode <scheatkode@amplium.io>"                                  \
	org.opencontainers.image.authors="scheatkode <scheatkode@amplium.io>"               \
	org.opencontainers.image.vendor="amplium"                                           \
	org.opencontainers.image.licenses="MIT"                                             \
	org.opencontainers.image.url="https://github.com/amplium/salt-ssh-action"           \
	org.opencontainers.image.documentation="https://github.com/amplium/salt-ssh-action" \
	org.opencontainers.image.source="https://github.com/amplium/salt-ssh-action"        \
	org.opencontainers.image.ref.name="salt-ssh action"                                 \
	org.opencontainers.image.title="salt-ssh action"                                    \
	org.opencontainers.image.description="salt-ssh action"

COPY main.py /main.py
COPY master  /etc/salt/master

ENTRYPOINT ["python3", "/main.py", "test"]
