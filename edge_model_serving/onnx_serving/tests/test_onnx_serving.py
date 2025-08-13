import os
import sys
import asyncio

import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

# Configurer environment et paths
os.environ["MODELS_PATH"] = "../models"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from onnx_server import app


@pytest.fixture(scope="session", autouse=True)
def startup_and_shutdown():
    """Force l'exécution de l'événement `startup` dans les tests"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())


@pytest.fixture(scope="session")
def client():
    """Créer un client de test qui sera réutilisé pour tous les tests"""
    return TestClient(app)


class TestOnnxServing:
    """Tests pour l'API ONNX Serving"""

    def test_homepage(self, client):
        """Test de la page d'accueil"""
        # Given
        # Le serveur est démarré (géré par la fixture startup_and_shutdown)

        # When
        response = client.get("/")

        # Then
        assert response.status_code == 200
        assert "Welcome to the onnx-server" in response.text

    def test_get_models(self, client):
        """Test pour récupérer la liste des modèles chargés"""
        # Given
        # Les modèles sont chargés (géré par la fixture startup_and_shutdown)

        # When
        response = client.get("/models")

        # Then
        assert response.status_code == 200
        models_list = response.json()
        assert isinstance(models_list, list)
        assert "yolo11n" in models_list  # Vérifie la présence du modèle attendu

    def test_get_model_metadata(self, client):
        """Test pour récupérer la résolution d’un modèle"""
        response = client.get("/models/yolo11n/versions/1/resolution")
        assert response.status_code == 200
        assert (
            "inputs_shape" in response.json()
        )  # Verifie que la réponse contient la forme d'entrée

    def test_predict(self, client):
        """Test d'inférence sur une image avec le modèle YOLOv11n"""
        # Given
        image_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "data/test_img.jpg")
        )
        assert os.path.exists(
            image_path
        ), f"L'image de test {image_path} n'existe pas !"

        # Préparation de l'image
        image = Image.open(image_path).convert("RGB")
        image = image.resize((640, 640))
        image_array = np.array(image).astype(np.float32) / 255.0
        image_array = np.transpose(image_array, (2, 0, 1))
        image_array = np.expand_dims(image_array, axis=0)
        payload = {"inputs": image_array.tolist(), "model_type": "yolo"}

        # When
        response = client.post("/models/yolo11n/versions/1:predict", json=payload)

        # Then
        assert (
            response.status_code == 200
        ), f"Erreur {response.status_code}: {response.text}"
        response_json = response.json()

        # Vérification des résultats de détection
        assert "outputs" in response_json, "Pas de clé 'outputs' dans la réponse"
        assert (
            "detection_boxes" in response_json["outputs"]
        ), "Pas de détection de boîtes"
        assert (
            "detection_classes" in response_json["outputs"]
        ), "Pas de classes détectées"
        assert "detection_scores" in response_json["outputs"], "Pas de scores détectés"

        print(f"Inférence réussie ! Résultat : {response_json['outputs']}")
