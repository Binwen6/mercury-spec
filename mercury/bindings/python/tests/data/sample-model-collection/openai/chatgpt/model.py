from typing import Tuple, Sequence

import sys
sys.path.append('../../../../..')

import mercury as mc

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")


class Model(mc.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def call(self, inputs: Sequence[Tuple[str, bool]]) -> str:
        messages = [{"role": "user" if user_sent else "assistant", "content": text}
                    for text, user_sent in inputs]
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages)
        return response['choices'][0]['message']['content']
