# from modeldetection import ModelDetection
from pathlib import Path
import torch
from torchvision import transforms
from PIL import Image
import numpy as np

from modeldetection import ModelDetection


class ModelHandler(ModelDetection):
    
    def __init__(self, checkpoint_pth: Path):
        super().__init__(checkpoint_pth=checkpoint_pth)
        self.min_score = 0.2
        self.max_overlap = 0.5
        self.top_k = 50
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        
    def preprocess(self, data):
        
        orig_frame = np.asarray(data)
        print(f"Entering preprocess {type(orig_frame)} {len(orig_frame)} {orig_frame.shape}")
        # orig_frame = cv2.cvtColor(np.asarray(orig_frame), cv2.COLOR_BGR2RGB)
        orig_frame = orig_frame[:, :, ::-1]
        orig_frame = Image.fromarray(orig_frame, 'RGB')

        res = transforms.Resize((300, 300))
        to_tensor = transforms.ToTensor()
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])

        frame = normalize(to_tensor(res(orig_frame)))
        frame = frame.to(self.device)
        return frame.unsqueeze(0)
    
    def inference(self, data):
        print(f"Entering inference {type(data)} {len(data)} {list(data.size())}")
        predicted_locs, predicted_scores = self.model(data)
        
        return predicted_locs, predicted_scores
    
    def postprocess(self, data):
        
        predicted_locs, predicted_scores = data
        
        print(f"Entering postprocess {list(predicted_locs.size())} {list(predicted_scores.size())}")
        
        det_boxes, det_labels, det_scores = self.model.detect_objects(predicted_locs, predicted_scores,
                                                                      min_score=self.min_score, max_overlap=self.max_overlap,
                                                                      top_k=self.top_k)
        
        # orig_frame = x
        response = {}
        print(f"Entering postprocess {det_boxes}")
        # original_dims = torch.FloatTensor(
        #     [orig_frame.width, orig_frame.height, orig_frame.width, orig_frame.height]).unsqueeze(0)
        # det_boxes = det_boxes * original_dims
        
        det_boxes = det_boxes[0].to('cpu').tolist()
        det_labels = det_labels[0].to('cpu').tolist()
        det_scores = det_scores[0].to('cpu').tolist()
        
        print(f"Entering postprocess {len(det_boxes)}")
        
        # for i, box in enumerate(det_boxes):
        #     key = f"object_{i}"
        #     response[key] = {'label': det_labels[i], 'location': det_boxes[i], 'score': det_scores[i]}
            
        return det_boxes, det_labels, det_scores
    
    def handle(self, data):
        data = self.preprocess(data)
        data = self.inference(data)
        data = self.postprocess(data)
        return data
    
if __name__ == "__main__":
    weight_path = Path.cwd() / "trained_models" / "checkpoint_ssd300.pth.tar"
    image_path = Path.cwd() / "example_images_OLS" / "MicrosoftTeams-image_1.png"
    im = Image.open(image_path)
    model_handler = ModelHandler(checkpoint_pth=weight_path)
    model_handler.load_model(cpu=True)
    response = model_handler.handle(data=im)
    print(f"RESPONSE: {response}")