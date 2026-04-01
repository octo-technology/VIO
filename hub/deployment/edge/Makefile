ifneq (,$(wildcard .env))
	include .env
endif

SHELL := /bin/bash
.SHELLFLAGS = -ec
.ONESHELL:
.SILENT:
.DEFAULT_GOAL: help

.EXPORT_ALL_VARIABLES:

ROOT_DIR := $(shell pwd)
IMAGES_DIR := $(ROOT_DIR)/images
MOUNTING_DIR := disk2
MOUNTING_PATH := /dev/$(MOUNTING_DIR)
RASPIOS := raspios_lite_armhf
RASPIOS_IMAGE_NAME := 2021-05-07-raspios-buster-armhf-lite
RASPIOS_DOWNLOAD_URL := https://downloads.raspberrypi.org/$(RASPIOS)/images/$(RASPIOS)-2021-05-28/$(RASPIOS_IMAGE_NAME).zip
SD_CARD_NAME := RASP_SD
PATH_TO_SD_CARD_MOUNTED_VOLUME := /Volumes/boot

CLOUD=azure/

.PHONY: help
help:
	echo "❓ Use \`make <target>'"
	grep -E '^\.PHONY: [a-zA-Z0-9_-]+ .*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: setup-edge-for-vio  ## ⚙️ Setup edge for VIO
setup-edge-for-vio:
	@read -p "You have a running Raspberry Pi [yes|no]: " yes_or_no; \
	if [ $$yes_or_no != "yes" ]; then echo "Please setup the Raspberry Pi OS first: make setup-raspberry-pi-os"; exit 1 ; fi
	ansible-playbook $(CLOUD)/ansible/install_iot_edge_agent_on_raspberry.yml

.PHONY: setup-raspberry-pi-os  ## ⚙️ Format SD card, download Raspberry Pi OS image, flash it, enable SSH after boot, setup WIFI credentials and eject SD card
setup-raspberry-pi-os : format-sd-card download-raspbian-image flash-raspbian-image-on-sd-card enable-ssh setup-wifi-credentials eject-sd-card

format-sd-card:
	@read -p "You checked with 'diskutil list' that SD card is effectively mounted on '$(MOUNTING_DIR)' [yes|no]: " yes_or_no; \
	if [ $$yes_or_no != "yes" ]; then echo "Please revise the mounting point before running this command."; exit 1 ; fi
	@diskutil unmountDisk $(MOUNTING_DIR)
	@diskutil eraseDisk FAT32 $(SD_CARD_NAME) MBRFormat $(MOUNTING_PATH)

download-raspbian-image:
	@mkdir -p $(IMAGES_DIR)
	@wget $(RASPIOS_DOWNLOAD_URL) -O $(IMAGES_DIR)/$(RASPIOS_IMAGE_NAME).zip
	@unzip $(IMAGES_DIR)/$(RASPIOS_IMAGE_NAME).zip -d $(IMAGES_DIR)/

flash-raspbian-image-on-sd-card:
	@diskutil unmountDisk $(MOUNTING_DIR)
	@sudo dd if=$(IMAGES_DIR)/$(RASPIOS_IMAGE_NAME).img of=$(MOUNTING_PATH) bs=1024
	@sleep 5

enable-ssh:
	@diskutil mountDisk $(MOUNTING_DIR)
	@touch $(PATH_TO_SD_CARD_MOUNTED_VOLUME)/ssh
	@ls $(PATH_TO_SD_CARD_MOUNTED_VOLUME) | grep ssh | if [ $(wc -l)==1 ]; then echo "All good!"; exit 0 ; fi

setup-wifi-credentials:
	@read -p "Do you need to setup your WIFI credentials (headless Raspbian only) [yes|no]: " yes_or_no; \
	if [[ $$yes_or_no == "yes" && $$(cat wpa_supplicant.conf.template | grep -E 'YOUR-NETWORK-SSID|YOUR-NETWORK-PASSWORD' | wc -l) -eq 2 ]]; then echo "Please set your WIFI credentials (WIFI_NAME/WIFI_PASSWORD) in wpa_supplicant.conf.template."; exit 1 ; fi
	@diskutil mountDisk $(MOUNTING_DIR)
	@cp wpa_supplicant.conf.template $(PATH_TO_SD_CARD_MOUNTED_VOLUME)/wpa_supplicant.conf
	@ls $(PATH_TO_SD_CARD_MOUNTED_VOLUME) | grep wpa_supplicant.conf | if [ $(wc -l)==1 ]; then echo "All good!"; exit 0 ; fi

eject-sd-card:
	@diskutil unmountDisk $(MOUNTING_DIR)
	@diskutil eject $(MOUNTING_DIR)
