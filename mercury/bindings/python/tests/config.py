from pathlib import Path


class Config:
    dataRootDir = Path(__file__).absolute().resolve().parent / 'data'
    modulesDir = dataRootDir / 'modules'
