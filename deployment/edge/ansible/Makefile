.PHONY: ping-edge
ping-edge:
	ansible all -i inventory.ini -m ping

setup-edge:
	ansible-playbook -v -i inventory.ini setup_edge.yml

deploy-vio-on-edge:
	ansible-playbook -v -i inventory.ini deploy_vio_on_edge.yml
