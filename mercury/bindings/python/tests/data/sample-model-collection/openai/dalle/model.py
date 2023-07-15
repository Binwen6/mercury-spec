import requests
from PIL import Image
from io import BytesIO

import mercury_nn as mc
import numpy as np
import openai


class Model(mc.Model):
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
    
    def call(self, inputs: str) -> np.array:
        """
        The returned array has shape (1024, 1024, 3), as specified in the manifest.
        """

        response = openai.Image.create(
            prompt=inputs,
            n=1,
            size="1024x1024"
        )
        
        image_url = response['data'][0]['url']
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        
        return np.asarray(img)
