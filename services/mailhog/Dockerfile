FROM mailhog/mailhog:latest

USER root

# Tools needed by the auth script, plus the binary path the compose command expects
RUN apk add --no-cache bash dos2unix && \
    mkdir -p /root/go/bin && \
    ln -sf "$(command -v MailHog)" /root/go/bin/MailHog

# Copy the commands directory into the container
COPY services/mailhog/commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

# Ensure all scripts in the commands directory have Unix-style line endings and are executable
RUN dos2unix /commands/setup_mailhog_auth.sh && chmod +x /commands/setup_mailhog_auth.sh

# The published image starts MailHog directly; clear it so the compose command runs the auth script first
ENTRYPOINT []
