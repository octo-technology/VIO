.PHONY: ping-edge
ping-edge:
	ansible all -i inventory.ini -m ping

deploy-vio-on-edge:
	ansible-playbook -v -i inventory.ini deploy_vio_on_edge.yml

register-edge-on-gcp-hub:
	ansible-playbook -vv -i inventory.ini register_edge_on_gcp_hub.yml