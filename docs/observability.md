# Observability

This section will describe the observability components that this project uses out of the bot to track things like command usage, central logging, and more.

## Tech Stack

The tech stack used for log collection is as follows:

- [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/)
- [Loki](https://github.com/grafana/loki)
- [Grafana](https://grafana.com/)

If you are unfamiliar with how a Grafana stack works I would highly suggest reading up about it because it can be a very powerful tool and all the components used are open-source.

A very short description of how this project uses the stack (listed above) is as follows:

1. Promtail scrapes the logs from the bot and pushes them to a Loki instance
2. Loki aggregates the log streams and tags them
3. Grafana uses Loki as a data source to graph, visualize, and query the logs that the bot generates

## Using the Log Stack

Since this bot can be built and tested in a variety of ways, the logging tech stack also can be setup in a variety of ways.

Here is a description of how the logging tech stack can be setup in the different environments:

- `make local`: Uses no logging stack at all
- `make run`: Starts the bot using docker-compose. Builds the full stack as seperate containers running on the same docker network
- `make kube`: Starts the bot in minikube with no logging stack initially. After the minikube cluster has been started, you have two options for starting your logging stack:
      - `script/k8s/obervability/setup`: Starts the logging stack inside of your minikube cluster (`make kube` must be run first)
      - Manually apply the `script/k8s/obervability/*.yaml.example` files to your minikube cluster and make sure to edit them as needed. This option is more complex and allows you to point your minikube cluster to a different Loki instance such as Grafana cloud. In production, the bot ships logs to Grafana cloud (`make kube` must be run first)
