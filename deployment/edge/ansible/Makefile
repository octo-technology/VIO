.PHONY: ping-edge
ping-edge:
	ansible all -i inventory.ini -m ping

deploy-vio-on-edge:
	ansible-playbook -v -i inventory.ini deploy_vio_on_edge.yml
