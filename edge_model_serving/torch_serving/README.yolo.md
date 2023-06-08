# Object Detection using Yolov5 model.

* You must create an env with torch nightly versions
    ```bash
    python -m venv .env
    source .env/bin/activate
    pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
    pip install -r requirements.txt
    ```

* Turn your pt model into a torchscript one (on Yolov5 repo)
    ```bash
    python export.py --weights model_path.pt --include torchscript
    mv model_path.torchscript model_path.torchscript.pt
    ```

* Create a model archive file and serve the fastrcnn model in TorchServe using below commands

    ```bash
	  torch-model-archiver \
	  --model-name yolo5 \
	  --version 2.1 \
	  --serialized-file model_path.torchscript.pt \
	  --handler ./torchserve_handler.py \
	  --extra-files ../models/torch/index_to_name.json,./torchserve_handler.py
    mkdir model_store
    mv model_name.mar model_store/
    torchserve --start --model-store model_store --models yolo5=model_name.mar --ts-config ./config.properties --foreground
    curl http://127.0.0.1:8080/predictions/yolo5 -T examples/object_detector/persons.jpg
    ```

* Note : The objects detected have scores greater than "0.5". This threshold value is set in object_detector handler. 
