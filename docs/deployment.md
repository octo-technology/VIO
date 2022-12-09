# Deployment

## Cloud - Infrastructure deployment on Azure

This section allows you to create all the Azure infrastructure for VIO:
- Storage resources (Storage Account + PostgreSQL)
- The IoT Hub
- An Azure function (`telemetry_saver`) to save Device-to-Cloud telemetry data in PostgreSQL
- An Event Grid Topic to connect IoT Hub with the `telemetry_saver` Azure function

### Prerequisites

Before getting started, you need to install Ansible and its dependencies for Azure and PostgreSQL.

```shell
$ cd ./deployment/
$ conda create -n ansible python=3
$ conda activate ansible
$ pip install -r requirements.txt
$ ansible-galaxy collection install azure.azcollection
$ ansible-galaxy collection install community.grafana
```


You'll also need :
- The [Azure CLI](https://docs.microsoft.com/fr-fr/cli/azure/install-azure-cli)
- The [Azure CLI IoT extension](https://github.com/Azure/azure-iot-cli-extension) extension
- The [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools)

On MacOS, these can be installed as follows:

```shell
$ brew update
$ brew install azure-cli
$ az extension add --name azure-iot
$ brew tap azure/functions
$ brew install azure-functions-core-tools@3
```

Once you have installed `azure-cli`, you can login to Azure using your Accenture account:

```shell
$ az login
```

Make sure you are using the Azure subscription `IX-Visual-Inspection-MDI`. You can check that with:
```shell
$ az account list --output table
```

If `IX-Visual-Inspection-MDI` is not the default subscription, you can switch to it with the following command:
```shell
$ az account set --subscription "IX-Visual-Inspection-MDI"
```

### Define the mandatory environment variables

In order to create and configure all the Azure infrastructure, we need to define some environment variables: 

```shell
$ export REGISTRY_USERNAME=<your_gitlab_username>
$ export REGISTRY_PASSWORD=<your_gitlab_container_registry_token>
$ export POSTGRES_USERNAME=<postgres_admin_username>
$ export POSTGRES_PASSWORD=<postgres_admin_password>
$ export AZURE_STORAGE_CONNECTION_STRING=<azure_storage_connection_string>
```

#### Registry Username 
firstname.lastname (i.e nicolas.dupont)

#### Registry Password 
You can find it on gitlab, click on your profil picture (top right corner) --> preferences. 
On the ```Access Tokens``` category, you can generate a token. I suggest no expiration date, and you select all the scopes.
Keep this token safe, once it's generated you cannot retrieve it on gitlab anymore.

#### Postgres Username and Password.
- To Get the Postgres username, go the Azure Portal, our subscription ```IX-Visual-Inspection-MDI``` --> our resource group ```vio-rg-dev``` --> the ``` vio-function-app-dev ``` function app.
On the left side bar menu, click on ```Configuration``` and unhide the POSTGRES_USER field. You only need what's before the @. Here it's ```vioadmin```
- To Ge the Postgres password, it's on the same page but unhide the POSTGRES_PASSWORD field.

![postgres_username_password.png](images/postgres_username_password.png)


### Create Azure Infrastructure

The following command creates all the Azure IoT infrastructure for VIO.

```shell
$ ansible-playbook ansible/create_azure_cloud_infrastructure.yml -e 'ansible_python_interpreter=<path_to_your_conda_env_python_interpreter>'
```

## Cloud - Deploy Grafana dashboard and data-sources

To deploy Grafana [dashboard](../monitoring/dashboards) and [data-sources](../monitoring/provisioning), run the following playbook :
```shell
$ ansible-playbook -i ansible/inventory/production.ini ansible/update_grafana_dashboard.yml --ask-pass
```

This will copy the files on the Grafana resource deployed in Azure and relaunch the grafana service to take into account the brand uploaded files. 


## Edge - Raspberry Setup (Raspbian installation)
The Raspberry can be set up thanks to this [Makefile](Makefile).

First thing first, insert the SD card in your computer to mount it. **Before typing any command**, check that the SD card is effectively mounted on `/dev/disk2`, by typing:
```shell
$ diskutil list 
```

Checklist before continuing:
- If the SD card is mount on another disk, edit the Makefile by replacing `MOUNTING_DIR := /dev/disk2` by the disk seen thanks to `diskutil` command.
- If you flash a Raspbian image **WITHOUT Desktop ONLY** you will need to connect on ssh on the Raspberry. To be able to connect, you need the Raspberry to be in the same local network than your computer. Therefore, setup your WIFI credentials on the Raspberry by editing the [wpa_supplicant.conf.template](wpa_supplicant.conf.template) replacing `ssid="YOUR-NETWORK-SSID"` and `psk="YOUR-NETWORK-PASSWORD"` values.
- If you want to flash a Rasbian image with Desktop, edit the Makefile by replacing:
  - `RASPIOS := raspios_lite_armhf` by `raspios_armhf` (Raspbian Desktop) or `raspios_full_armhf` (Raspbian Desktop + recommended Software) and
  - `RASPIOS_IMAGE_NAME := 2021-05-07-raspios-buster-armhf-lite` by an existing image from [here](https://downloads.raspberrypi.org/raspios_armhf/images/) or [here](https://downloads.raspberrypi.org/raspios_full_armhf/images/).

Then, type:
```shell
$ make raspbian
```
This command will **request information from you** and last about **10 minutes**. Stay close to your computer until you gave your sudo password (at the beginning of the execution).

Then you are all set! With the last command, you just :
1. Formatted the SD card,
2. Downloaded the Raspbian Buster lite image from 2021-05-07,
3. Flashed the image on the SD card,
4. Enabled SSH connection after boot,
5. Setup WIFI credentials and eventually
6. Ejected the SD card.

You are now done and can insert the SD card in the Raspberry and make it boot.

For more details on what you just have done, see the following parts.

### [OPTIONAL] Step-by-step Raspberry Setup
#### Identify SD card
In Terminal, type the following command:
```shell
$ diskutil list
```
You should see something like:
![diskutil-list-SDCARD](images/diskutil-list-SDCARD.png)
In this case `/dev/disk2` is my SD card.

#### Format SD card
To reformat the SD card, go in the deployment directory and type:
```shell
$ make format-sd-card
```
Or:
```shell
$ diskutil unmountDisk $(MOUNTING_DIR)
$ diskutil eraseDisk FAT32 $(SD_CARD_NAME) MBRFormat $(MOUNTING_PATH)
```
The SD card will be formatted in *FAT32* format under the name *SDCARD* with a Master Boot Record (*MBRFormat*).

#### Verify formatting
To check if the formatting was successful, use above command again:
```shell
$ diskutil list
```
Look for a disk named `SDCARD` like in the following picture:
![diskutil-list-SDCARD](images/diskutil-list-SDCARD.png)

#### Download the Raspbian image
It exists a lot of Raspbian images able to run on Raspberry. Here is an non exhaustive list:
- Raspberry Pi OS with desktop and recommended software available [here](https://downloads.raspberrypi.org/raspios_full_armhf/)
- Raspberry Pi OS with desktop available [here](https://downloads.raspberrypi.org/raspios_armhf/)
- Raspberry Pi OS Lite available [here](https://downloads.raspberrypi.org/raspios_lite_armhf/)

By default, you can download the Raspberry Pi OS Lite from 2021-05-07 by typing:
```shell
$ make download-raspbian-image
```
Or:
```shell
$ wget https://downloads.raspberrypi.org/$(RASPIOS)/images/$(RASPIOS)-2021-05-28/$(RASPIOS_IMAGE_NAME).zip -O $(IMAGES_DIR)/$(RASPIOS_IMAGE_NAME).zip
$ unzip $(IMAGES_DIR)/$(RASPIOS_IMAGE_NAME).zip -d $(IMAGES_DIR)/
```

#### Flash an image
Choose an image and then flash it on the SD card as followed:
```shell
$ make flash-raspbian-image-on-sd-card
```
Or:
```shell
$ diskutil unmountDisk $(MOUNTING_DIR)
$ sudo dd if=$(IMAGES_DIR)/$(RASPIOS_IMAGE_NAME).img of=$(MOUNTING_PATH) bs=1024
```

To check if the flashing was successful, use above command again:
```shell
$ diskutil list
```
Look for a disk named `SDCARD` like in the following picture:
![diskutil-list-SDCARD](images/diskutil-list-SDCARD.png)


#### Enable SSH and set WIFI credentials
Once formatted, to enable *ssh* and set your WIFI credentials, first edit `ssid="YOUR-NETWORK-SSID"` and `psk="YOUR-NETWORK-PASSWORD"` values in the [wpa_supplicant.conf.template](wpa_supplicant.conf.template).

Then, type:
```shell
$ make setup-wifi-credentials
```
It will copy the file named `wpa_supplicant.conf.template` with the following content (network parameters) on the SD card as `wpa_supplicant.conf`:
```shell
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
network={
    ssid="<YOUR-NETWORK-SSID>"
    psk="<YOUR-NETWORK-PASSWORD>"
    key_mgmt=WPA-PSK
}
```

To enable SSH connection after boot, you just need to create an empty file named `ssh` on your SD card by typing:
```shell
$ make enable-ssh
```
Or:
```shell
$ touch /Volumes/boot/ssh
```

#### Eject the SD card
To eject the mounted SD card, type:
```shell
$ make eject-sd-card
```
Or:
```shell
$ diskutil unmountDisk $(MOUNTING_DIR)
$ diskutil eject $(MOUNTING_DIR)
```

## Edge - Install and configure the IoT Edge Agent on RaspberryPI

In order to be managed by Azure IoT Hub, each edge device must install an IoT Edge Agent and _connect_ to the Hub. 

We use Ansible to automate the setup of the IoT Edge Agent.

### Install Ansible on the RaspberryPI
```shell
$ pip3 install ansible
```

### Check Ansible is correctly installed
```shell
$ ansible --version
```

If `ansible` command is not found, add `/home/pi/.local/bin` to the PATH.

### Define environment variables

For The moment, the RaspberryPI connects to the Azure IoT Hub using the connection string of the IoT Edge device identity.

We need to provide this connection string through an environment variable.

```shell
$ export CONNECTION_STRING="<primary_connection_string_from_iot_edge_device_on_azure_portal>"
```


### Execute the playbook

The following command installs the necessary dependencies, creates the configuration file for the connection to IoT Hub, and applies the configuration.

```shell
$ cd <path_to_vio_edge_repo>/
$ ansible-playbook deployment/ansible/install_iot_edge_agent_on_raspberry.yml
```
