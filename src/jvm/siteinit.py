import sys

from .import_hook.finder import JavaFinder

# import hook設定
if not any(isinstance(f, JavaFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, JavaFinder())
