import inspect
from tomondt import plugins

class Plugin:
    def __init__(self, obj, isclass=False):
        self.obj = obj
        self.isclass =  isclass
        self.widget = None 
    
class PluginManager:
    __instance=None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.plugins = {}
            cls.__instance.register()
        return cls.__instance
    
    def register(self):
        for name, obj in inspect.getmembers(plugins):
            if inspect.isfunction(obj):
                if hasattr(obj, '__annotations__'):
                    if 'NDtFunc' in obj.__annotations__:
                        htype  = obj.__annotations__['NDtFunc']['htype']
                        name = obj.__annotations__['NDtFunc']['name']
                        if htype not in self.plugins:
                            self.plugins[htype] = {}
                        if name not in self.plugins[htype]:
                            self.plugins[htype][name] = Plugin(obj)
                        else:
                            raise ValueError(f"Plugin {name} already exists do not override")
        
            if inspect.isclass(obj):
                if hasattr(obj, 'NDtClass'):
                    htype = obj.NDtClass['htype']
                    name = obj.NDtClass['name']
                    if htype not in self.plugins:
                        self.plugins[htype] = {}
                    if name not in self.plugins[htype]:
                        self.plugins[htype][name] = Plugin(obj, True)
                    else:
                        raise ValueError(f"Plugin {name} already exists do not override")
        
        for name, obj in inspect.getmembers(plugins):
            if inspect.isclass(obj):
                if hasattr(obj, 'NDtWidget'):
                    htype = obj.NDtWidget['htype']
                    name = obj.NDtWidget['name']
                    if htype not in self.plugins:
                            raise Exception(f"Plugin {htype} does not exist")
                    if name not in self.plugins[htype]:
                            raise Exception(f"Plugin {name} does not exist")
                    self.plugins[htype][name].widget = obj
                    
                    
plugin_manager = PluginManager() 
