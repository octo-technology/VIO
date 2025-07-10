import pytest
from fastapi.testclient import TestClient
import sys
import os
import asyncio
import numpy as np
from PIL import Image



os.environ["MODELS_PATH"] = "../models"

# sys.path.append() ajoute src/ aux chemins où Python cherche les modules.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from onnx_server import app  


@pytest.fixture(scope="session", autouse=True)
def startup_and_shutdown():
    """✅ Force l'exécution de l'événement `startup` dans les tests"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())


# Créer un client de test
client = TestClient(app)

class TestOnnxServing:
    """Tests pour l'API ONNX Serving"""

    def test_homepage(self):
        """Test de la page d'accueil"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Welcome to the onnx-server" in response.text  

    def test_get_models(self):
        """Test pour récupérer la liste des modèles chargés"""
        response = client.get("/models") 
        assert response.status_code == 200 # check endpoint /models
        models_list = response.json()
        assert isinstance(models_list, list)  # Verifie que c'est bien une liste
        assert "yolo11n" in models_list  # Verifie que yolo11n est dans liste

    def test_get_model_metadata(self):
        """Test pour récupérer la résolution d’un modèle"""
        response = client.get("/models/yolo11n/versions/1/resolution")
        assert response.status_code == 200
        assert "inputs_shape" in response.json()  # Verifie que la réponse contient la forme d'entrée


    def test_predict(self):
        """Test d'inférence sur une image avec le modèle YOLOv11n"""

        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data/test_img.jpg"))

        # vrifier que l’image existe
        assert os.path.exists(image_path), f"❌ L'image de test {image_path} n'existe pas !"

        # Prep image
        image = Image.open(image_path).convert("RGB")  
        image = image.resize((640, 640))  
        image_array = np.array(image).astype(np.float32) / 255.0  
        image_array = np.transpose(image_array, (2, 0, 1))  
        image_array = np.expand_dims(image_array, axis=0)


        payload = {
            "inputs": image_array.tolist(),  
            "model_type": "yolo"
        }
        response = client.post("/models/yolo11n/versions/1:predict", json=payload)

        # Verif reponse
        assert response.status_code == 200, f"Erreur {response.status_code}: {response.text}"
        response_json = response.json()
        
        # Verifier que la sortie contient des résultats de détection
        assert "outputs" in response_json, "Pas de clé 'outputs' dans la réponse"
        assert "detection_boxes" in response_json["outputs"], "Pas de détection de boîtes"
        assert "detection_classes" in response_json["outputs"], "Pas de classes détectées"
        assert "detection_scores" in response_json["outputs"], "Pas de scores détectés"

        print(f"Inférence réussie ! Résultat : {response_json['outputs']}")



        



        


















