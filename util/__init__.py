import os

class FileExistsError(ValueError):
  pass

def mkdir_recursive(dir_path):
  if dir_path == '':
    return
  if os.path.exists(dir_path):
    if os.path.isfile(dir_path):
      raise ValueError(dir_path, "There is a file here")
  else:
    mkdir_recursive(os.path.dirname(dir_path))
    os.mkdir(dir_path)
