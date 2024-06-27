# mypy: disable-error-code="has-type"

from typing import Callable, List, Dict

from robot_war.api import model0, time, thread
from robot_war.vm.source_module import Module

ROBOT_MODULE = Module("robot_war")
ROBOT_CLASSES: List[Callable] = [model0.Robot]
MODELS: Dict[str, Module] = {"model0": model0.MODEL0_MODULE}  # ignore: type
MODULES: Dict[str, Module] = {"time": time.TIME_MODULE, "thread": thread.THREAD_MODULE}  # ignore: type[has-type]
API_CLASSES = [thread.Thread]
