import unittest
from types import ModuleType

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(str(Path(__file__).resolve().parent))

from src.mercury_nn.utils import moduleFromPath
from src.mercury_nn.exceptions import InvalidModulePathException

from config import Config


class TestModuleFromPath(unittest.TestCase):
    
    def test_File_NoOverride(self):
        module_path = Config.modulesDir / 'no_override.py'
        module = moduleFromPath(module_path)

        self.assertEqual(Path(module.__file__).absolute().resolve(), module_path.absolute().resolve())

    def test_File_Override(self):
        module_path = Config.modulesDir / 'os.py'
        module = moduleFromPath(module_path)
        
        self.assertEqual(Path(module.__file__).absolute().resolve(), module_path.absolute().resolve())
        self.assertEqual(module.test(), 'test')
    
    def test_File_NonExistent(self):
        module_path = Config.modulesDir / 'non_existent.py'
        
        with self.assertRaises(InvalidModulePathException):
            module = moduleFromPath(module_path)
        
    def test_Dir_NoOverride(self):
        module_path = Config.modulesDir / 'no_override'
        module = moduleFromPath(module_path)
        
        self.assertEqual(Path(module.__file__).absolute().resolve(), module_path.absolute().resolve() / '__init__.py')
        self.assertEqual(module.test(), 'test')
    
    def test_Dir_Override(self):
        module_path = Config.modulesDir / 'os'
        module = moduleFromPath(module_path)
        
        self.assertEqual(Path(module.__file__).absolute().resolve(), module_path.absolute().resolve() / '__init__.py')
        self.assertEqual(module.test(), 'test')
    
    def test_Dir_NonExistent(self):
        module_path = Config.modulesDir / 'non_existent'
        
        with self.assertRaises(InvalidModulePathException):
            module = moduleFromPath(module_path)

if __name__ == '__main__':
    unittest.main()
