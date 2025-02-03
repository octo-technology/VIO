Before launching ansible export a env to specify your local vio directory
```
export LOCAL_VIO_DIR=
```
### Setup the edge

Install openssh-server on the edge:
```bash
 sudo apt-get install openssh-server
```

Do not forget to install the google-cloud-storage package:
```bash
pip install google-cloud-storage==3.0.0
```

Then, try to connect through:
```bash
 ssh localhost
```

Install Docker on the edge help you with [this link](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
Don't forget [post-installation](https://docs.docker.com/engine/install/linux-postinstall/) steps to run docker as a non-root user.

Install *make* on the edge:
```bash
sudo apt-get install build-essential
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

## docker compose devices

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
Uncomment the *localhost* lines in the inventory file.

Then run the following command:
```bash
make test-registering-localhost-on-gcp-hub
```
