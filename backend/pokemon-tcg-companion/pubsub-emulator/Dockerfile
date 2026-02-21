FROM google/cloud-sdk:slim

ENV DEBIAN_FRONTEND=noninteractive

# Install a lightweight JRE required by the Pub/Sub emulator
RUN apt-get update \
  && apt-get install -y --no-install-recommends google-cloud-cli-pubsub-emulator default-jre-headless ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

EXPOSE 8085

# Start the Pub/Sub emulator on container start
CMD ["gcloud", "beta", "emulators", "pubsub", "start", "--host-port=0.0.0.0:8085"]
