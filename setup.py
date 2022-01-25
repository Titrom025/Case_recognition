from cx_Freeze import setup, Executable

includefiles = ['model.tar', 'vocab.tar', 'Arsenal-Regular.otf', 'config.json']
includes = []
excludes = []
packages = []

executables = [Executable('Analyzer_module.py')]

setup(name='Recognition of court orders',
      version='1',
      description='Analyzer module',
      options = {'build_exe': {'include_files':includefiles}},
      executables=executables
)