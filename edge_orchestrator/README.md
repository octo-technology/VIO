# edge_orchestrator

The edge_orchestrator orchestrates the following steps as soon as it is triggered:

1. image capture
2. image backup
3. metadata backup
4. model inference on images
5. saving results


## Common errors

# Error: pg_config executable not found.

Check if pg_config is installed on your system.

```bash
pg_config --version
```

If not, install it using the following command:

MacOS:
```bash
brew install postgresql
```
MAC : 172.23.26.18
ipconfig getifaddr en0

Intel : 192.168.1.25
ip a | grep -A 2 'wlx' | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
