# Ansible repo to setup remote devices

## Setup the remote devices passwordless using SSH

- Set the different host devices inside the [inventory.ini](inventory.ini) providing user and password.
- Generate a public and private SSH key if you don't already have one using `ssh-keygen -t rsa -b 4096 -C "comment|email"` command.
- Define the `SSH_PUB_KEY_PATH` environment variable as the path to your SSH public key
- Run the following playbook:
```shell
ansible-playbook -i inventory.ini playbook/setup_ssh_key.yml
```

## Define local vio directory

Before launching ansible export a env to specify your local vio directory
```
export LOCAL_VIO_DIR=
```


### Install sshpass
https://stackoverflow.com/questions/42835626/ansible-to-use-the-ssh-connection-type-with-passwords-you-must-install-the-s

```
pip install -r requirements.txt
```

## docker-compose devices

We are adding those devices to be able to trigger capture from 2 cameras connected on the usb port of your edge.

devices:
    - /dev/video0:/dev/video0
    - /dev/video2:/dev/video2