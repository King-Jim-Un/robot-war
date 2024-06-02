from robot_war.vm.source_class import SourceClass
from robot_war.vm.source_module import Module


def api_go(obj):
    print(f"api_go(obj)")


MODEL0_ROBOT = SourceClass({"api_go": api_go})
MODEL0_MODULE = Module("model0", name_dict={"Robot": MODEL0_ROBOT})
