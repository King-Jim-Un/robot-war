from robot_war.api import model0, time, thread
from robot_war.vm.source_module import Module

ROBOT_MODULE = Module("robot_war")
ROBOT_CLASSES = [model0.Robot]
MODELS = {"model0": model0.MODEL0_MODULE}
MODULES = {"time": time.TIME_MODULE, "thread": thread.THREAD_MODULE}
API_CLASSES = [thread.Thread]
