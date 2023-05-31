.PHONY: ping-edge
ping-edge:
	ansible localhost -i inventory.ini -m ping

setup-ansible:
	ansible-galaxy collection install kubernetes.core

setup-edge:
	ansible-playbook -v -i inventory.ini setup_edge.yml

deploy-vio-on-edge:
	ansible-playbook -v -i inventory.ini deploy_vio_on_edge.yml
