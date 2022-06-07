# Bixi server Dockerfile
# Copyright Jean-Olivier Dalphond
FROM debian:stable AS compile

# Installing dependencies
# Would give errors if curl wasn't installed "separately" first
RUN apt update && apt install -y curl

# Other dependencies
RUN apt install -y build-essential \
        pkg-config      \
        openssl         \
        libssl-dev      \
        lua5.3          \
        bison           \
        flex            \
        parallel        \
        gcovr           \
        yajl-tools

# Compiling server binaries
COPY . .
RUN make

# Running the server
FROM debian:stable

RUN apt update && apt install -y openssl && rm -rf /var/lib/apt/lists/*

# Copy binary file
COPY --from=compile /tmp/bixi-server/bin/bixi-server /usr/bin

# Opening port 80 internally
EXPOSE 80

# Starting the server
CMD ["bixi-server", "-no-loop", "-no-tls", "-port", "80", "-wd", "/srv/www"]
