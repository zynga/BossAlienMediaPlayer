FROM debian:bullseye

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
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev \
        pkg-config \
        git \
 && ( curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y ) \
 && curl http://ftp.us.debian.org/debian/pool/main/libs/libshout/libshout3_2.4.1-2_amd64.deb > libshout3_2.4.1-2_amd64.deb \
 && dpkg -i libshout3_2.4.1-2_amd64.deb \
 && DEBIAN_FRONTEND=noninteractive apt-mark hold libshout3 \
 && mkdir -p /etc/apt/keyrings \
 && curl -L -o /etc/apt/keyrings/mopidy-archive-keyring.gpg https://apt.mopidy.com/mopidy.gpg \
 && curl -L https://apt.mopidy.com/bullseye.list -o /etc/apt/sources.list.d/mopidy.list \
 && apt-get update \ 
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        mopidy \
        mopidy-local \
 && git clone --depth 1 https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs \
 && cd gst-plugins-rs \
 && . "$HOME/.cargo/env" \
 && cargo build --package gst-plugin-spotify --release \
 && install -m 644 target/release/libgstspotify.so $(pkg-config --variable=pluginsdir gstreamer-1.0)/ \
 && gst-inspect-1.0 spotify \
 && apt-get install -y python3-pip \
 && pip3 install -U six \
 && pip3 install \
        cryptography \
        pyasn1 \
        pyopenssl \
        requests[security] \
        python-ldap \
 && python3 -m pip install https://github.com/mopidy/mopidy-spotify/archive/master.zip \
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
