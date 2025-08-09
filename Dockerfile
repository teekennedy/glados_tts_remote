# syntax=docker/dockerfile:experimental
ARG package_name=cpu-http

FROM nixos/nix:latest AS builder

ARG package_name

# Copy our source and setup our working dir.
COPY flake.nix flake.lock /src/
WORKDIR /src

# Build the base python package first (for better layer caching)
RUN nix \
    --extra-experimental-features "nix-command flakes" \
    --option filter-syscalls false \
    --accept-flake-config \
    build .#python

# Copy the model json configs while ignoring model files
COPY models/TTS/*.json /src/models/TTS/
COPY uv.lock pyproject.toml /src/
COPY glados_tts/ /src/glados_tts/

# Build glados-tts and copy its Nix store closure into a directory.
# The Nix store closure is the entire set of Nix store values that we need for our build.
RUN nix \
    --extra-experimental-features "nix-command flakes" \
    --option filter-syscalls false \
    --accept-flake-config \
    build .#${package_name} && \
    mkdir /tmp/nix-store-closure && \
    cp -R $(nix-store -qR result/) /tmp/nix-store-closure

# Final image is based on scratch. We copy a bunch of Nix dependencies
# but they're fully self-contained so we don't need Nix anymore.
FROM scratch

ARG package_name

WORKDIR /app

EXPOSE 8124

# Copy /nix/store
COPY --from=builder /tmp/nix-store-closure /nix/store
COPY --from=builder /src/result /${package_name}
ENV PATH="/${package_name}/bin:${PATH}"
CMD ["/${package_name}/bin/glados-tts"]
