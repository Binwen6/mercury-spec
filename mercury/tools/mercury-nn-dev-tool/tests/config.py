from pathlib import Path


class Config:
    dataRootDir = Path(__file__).absolute().resolve().parent.joinpath('data')
    manifestsRootDir = dataRootDir.joinpath('manifests')
    filterCasesRootDir = dataRootDir.joinpath('filters')
    stdoutBufferFile = dataRootDir.joinpath('stdout.tmp')
    stderrBufferFile = dataRootDir.joinpath('stderr.tmp')

    mainPyExecutable = dataRootDir.parent.parent.joinpath('src/main.py')
