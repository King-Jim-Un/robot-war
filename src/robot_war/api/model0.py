from robot_war.source_module import Module
from robot_war.source_class import SourceClass


def api_go(obj):
    print(f"api_go(obj)")


MODEL0_ROBOT = SourceClass({"api_go": api_go})
MODEL0_MODULE = Module("model0", name_dict={"Robot": MODEL0_ROBOT})
