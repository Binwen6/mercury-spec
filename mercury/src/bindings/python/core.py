from typing import Any
import importlib.machinery
import importlib.util
import os
import json


# TODO: use code generation to avoid hardcoding json structure
MODEL_MANIFEST_FILENAME = "manifest.json"
MODEL_SPECS_KEY_NAME = 'model-specs'
IMPLEMENTATIONS_KEY_NAME = 'implementations'
PYTHON_IMPLEMENTATION_IDENTIFIER = 'python'
ENTRY_FILE_KEY_NAME = 'entry-file'
ENTRY_CLASS_KEY_NAME = 'entry-class'
CALL_MODEL_METHOD_NAME = 'call'


class Model:
    
    def __init__(self, instance: Any, info: Any):
        # TODO: check for instance & info validity
        if CALL_MODEL_METHOD_NAME not in dir(instance):
            raise Exception(f'Instance is invalid, as it does not have a {CALL_MODEL_METHOD_NAME} method!')

        self._instance = instance
        self._info = info

    def call(self, input: Any) -> Any:
        """Call this model.

        Args:
            input (Any): Inputs.

        Returns:
            Any: Outputs.
        """
        
        # TODO: check for input validity
        
        return getattr(self._instance, CALL_MODEL_METHOD_NAME)(input)


def instantiate(model_dir: str):
    """Instantiate a model (i.e., logical device creation).

    Args:
        model_dir (str): The directory to the model.
            The directory should contain the manifest file (manifest.json) and a startup script (model.py)
    """

    with open(os.path.join(model_dir, MODEL_MANIFEST_FILENAME), 'r') as f:
        manifest_data = json.load(f)
        info = manifest_data[MODEL_SPECS_KEY_NAME]
        implementation_specs = manifest_data[IMPLEMENTATIONS_KEY_NAME][PYTHON_IMPLEMENTATION_IDENTIFIER]
        implementation_filename = implementation_specs[ENTRY_FILE_KEY_NAME]
        entry_class_name = implementation_specs[ENTRY_CLASS_KEY_NAME]
    
    loader = importlib.machinery.SourceFileLoader('module', os.path.join(model_dir, implementation_filename))
    spec = importlib.util.spec_from_loader('module', loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)

    entry_class = getattr(module, entry_class_name)

    instance = entry_class()

    return Model(instance=instance, info=info)
    