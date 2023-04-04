FROM netboxcommunity/netbox:v3.4.4

# Copy Opticore Logos to Static Content
COPY ./docker/data/netbox/static/ /opt/netbox/netbox/static/

# -------------------------------------------------------------------------------------
# Install Source Files
# -------------------------------------------------------------------------------------
COPY ../ /source/
RUN chmod +x /source/docker/configuration/docker-entrypoint.sh

# -------------------------------------------------------------------------------------
# Copy Config File & Scripts
# -------------------------------------------------------------------------------------
RUN cp /source/docker/configuration/configuration.py /etc/netbox/config/configuration.py

# Install and Configure Poetry
RUN pip install poetry

RUN poetry config virtualenvs.create false

# Install the Source Project Dependencies
RUN cd /source && \
    poetry install --no-interaction --no-ansi && \
    mkdir /tmp/dist && \
    poetry export --without-hashes -o /tmp/dist/requirements.txt

# Override the default entrypoint
ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD ["/source/docker/configuration/docker-entrypoint.sh"]
