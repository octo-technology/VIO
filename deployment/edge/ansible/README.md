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