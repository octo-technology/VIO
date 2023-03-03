## Face recognition with VIO

The aim of this module is to play with VIO by adding a facerecognition module.
For example: if we want to tell if a face is an avenger or not.

### HOW TO:

Add samples of faces to the folder :

    edge_facerec_serving/allowed_photos 

This folder will contain the faces that you want to positively id.

The module will load them at start, and when a new query image with a face is fed to
VIO, it will tell if the face belongs to faces that are in "allowed_photos"