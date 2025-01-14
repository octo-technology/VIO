Before launching ansible export a env to specify your local vio directory
```
export LOCAL_VIO_DIR=
```


### Install sshpass and the requirements

On MacOS, you can install sshpass using brew:
```bash
brew install sshpass
```

Then install requirements:
```bash
pip install -r requirements.txt
```

### Find the IP of the edge

Under Ubuntu, you can use the following command to find the IP of the edge
```bash
ip a | grep -A 2 'wlx' | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
```

Then change the IP addresses on the inventory file

## docker-compose devices

We are adding those devices to be able to trigger capture from 2 cameras connected on the usb port of your edge.

devices:
    - /dev/video0:/dev/video0
    - /dev/video2:/dev/video2

### Test locally

Set up the python venv:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Change the *REMOTE_VIO_DIR* to the local path to the vio directory.
Uncomment the *edge_3* lines in the inventory file.

Then run the following command:
```bash
make register-edge-on-gcp-hub-locally