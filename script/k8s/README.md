# What is this?

This folder contains k8s manifests for building a local minikube cluster for testing

To see the production k8s manifests, check out the `terraform\k8s\modules\containers\errbot` folder

After successfully running `make kube` from the root of this repo you effectively have two options for deploying the observability stack:

1. Run `./setup` (in this directory) to setup all the parts to the Promtail, Loki, and Grafana stack inside of your local minikube instance
2. Use `kubectl apply -f <promtail-config.yaml && promtail.yaml>` to only deploy a single promtail daemonset to your local minikube cluster. This daemonset will scrape logs from your errbot container and push them to Grafana cloud. This is what the prod instance of errbot does. Make sure to edit and add your Loki push URL (with api key and account id) to the `promtail-config.yaml` file
