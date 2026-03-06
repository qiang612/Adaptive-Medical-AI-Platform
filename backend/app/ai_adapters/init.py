import importlib

def get_adapter(adapter_class_path):
    module_path, class_name = adapter_class_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    adapter_class = getattr(module, class_name)
    return adapter_class()