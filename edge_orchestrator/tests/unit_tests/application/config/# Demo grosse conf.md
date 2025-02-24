# Demo grosse conf

1. Connect to edge
2. Go to Teachable machine
3. Train a 2 classes model (normal, missing wing)

4. Back on the hub
5. SCP the model from the edge to the hub
6. Deploy the model on the edges
```bash
export LOCAL_VIO_DIR=/Users/gireg.roussel/Desktop/octo/VIO/
cd deployment/edge/ansible
make deploy-vio-on-inventory
```

7. Back on the edge
8. Trigger the model through UI

9. Go to the hub
10. Visualize the results




VIO

- [ ] Auto refresh with dynamic
- [ ] Modèle à entrainer
    - [x] TeachbleMachine (manque une aile)
    - [ ] Entrainement à 2 classes
    - [ ] Export du model
        - [ ] SCP sur hub ?
        - [ ] Publication dans GCP (command line)
    - [ ] Depuis le Hub vers les edges
        - [ ] Redéploiement sur les deux edges depuis le hub (ansible)
            - [ ] Download les poids et tu les stocks sur le volume ?
            - [ ] Repackage l’image Dockerfile ?
    - [ ] Que se passe t il avec des canard colorés
    - [ ] Entrainement à 3 classes
- [ ] Clean GCP bucket



MAC : 172.23.26.18
ipconfig getifaddr en0

Intel : 192.168.1.25
ip a | grep -A 2 'wlx' | grep 'inet ' | awk '{print $2}' | cut -d/ -f1
