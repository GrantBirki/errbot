FROM localstack/localstack-light:0.13.3

# copy our custom startup script
COPY localstack-startup .

# start the container by running our startup script
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["./localstack-startup"]
