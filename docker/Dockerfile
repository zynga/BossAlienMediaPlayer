FROM debian:buster

RUN set -ex \
    # Official Mopidy install for Debian/Ubuntu along with some extensions
    # (see https://docs.mopidy.com/en/latest/installation/debian/ )
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl \
        dumb-init \
        gcc \
        gnupg \
        gstreamer1.0-alsa \
        gstreamer1.0-plugins-bad \
        python3-crypto \
        sqlite3 \
        sudo \
        vim \
        curl \
        libldap2-dev \
        libsasl2-dev \
        libssl-dev \
        python3-dev \
        cron \
        net-tools \
        procps \
        python-pykka \
 && mkdir -p /usr/local/share/keyrings \
 && curl -L -o /usr/local/share/keyrings/mopidy-archive-keyring.gpg https://apt.mopidy.com/mopidy.gpg \
 && curl -L https://apt.mopidy.com/buster.list -o /etc/apt/sources.list.d/mopidy.list \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        mopidy \
        mopidy-local \
        mopidy-spotify \
 && apt-get install -y python3-pip \
 && pip3 install -U six \
 && pip3 install \
        cryptography \
        pyasn1 \
        pyopenssl \
        requests[security] \
        python-ldap \
 && mkdir -p /var/lib/mopidy/.config \
 && ln -s /config /var/lib/mopidy/.config/mopidy \
    # Clean-up
 && apt-get purge --auto-remove -y \
        gcc \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* ~/.cache

# Start helper script.
COPY entrypoint.sh /entrypoint.sh

# Mopidy configuration (and LDAP certificate if exists)
COPY mopidy.conf ldapcert* /config/

# Copy the pulse-client configuratrion.
COPY pulse-client.conf /etc/pulse/client.conf

# Allows any user to run mopidy, but runs by default as a randomly generated UID/GID.
ENV HOME=/var/lib/mopidy
RUN set -ex \
 && usermod -u 84044 mopidy \
 && groupmod -g 84044 audio \
 && chown mopidy:audio -R $HOME /entrypoint.sh \
 && chmod go+rwX -R $HOME /entrypoint.sh

RUN mkdir -p /var/lib/mopidy/media

# Runs as mopidy user by default.
RUN adduser mopidy sudo
RUN echo "mopidy ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER mopidy

VOLUME ["/var/lib/mopidy/mopidy_bamp", "/var/lib/mopidy/.config/pulse", "/var/lib/mopidy/database", "/var/lib/mopidy/media"]

EXPOSE 6680

ENTRYPOINT ["/usr/bin/dumb-init", "/entrypoint.sh"]
CMD ["/usr/bin/mopidy"]

HEALTHCHECK --interval=5s --timeout=2s --retries=20 \
    CMD curl --connect-timeout 5 --silent --show-error --fail http://localhost:6680/ || exit 1
