from dataclasses import dataclass
import logging
from typing import List, Tuple, Optional

from robot_war.vm.instructions import CodeLine

try:
    from robot_war.vm.exec_context import SandBox
    from robot_war.vm.get_name import GetName
    from robot_war.vm.source_functions import Function
except ImportError:
    SandBox = Function = GetName = None  # type: ignore

# Constants:
LOG = logging.getLogger(__name__)

"""
>>> try:
  2           0 SETUP_FINALLY           10 (to 12)
>>> (code)
              8 POP_BLOCK                                falling out of a block
             10 JUMP_FORWARD            18 (to 30)
>>> except:
  4     >>   12 POP_TOP
             14 POP_TOP
             16 POP_TOP
>>> (code)
             24 POP_EXCEPT                               handler consumes the error
             26 JUMP_FORWARD             2 (to 30)
>>> raise
  6          24 RAISE_VARARGS            0
             26 POP_EXCEPT
>>> except (IndexError, IOError) as err:
  4     >>   12 DUP_TOP                                 error x 2
             14 LOAD_NAME                1 (IndexError)
             16 LOAD_NAME                2 (IOError)
             18 BUILD_TUPLE              2
             20 JUMP_IF_NOT_EXC_MATCH    58             pops exc type, test type
             22 POP_TOP                                 exc type
             24 STORE_NAME               3 (err)        exc instance
             26 POP_TOP                                 tb?
             28 SETUP_FINALLY           20 (to 50)
except IOError:
  4     >>   12 DUP_TOP
             14 LOAD_NAME                1 (IOError)
             16 JUMP_IF_NOT_EXC_MATCH    36
             18 POP_TOP
             20 POP_TOP
             22 POP_TOP
finally:
  5          10 LOAD_NAME                1 (b)
             12 CALL_FUNCTION            0
             14 POP_TOP
             16 JUMP_FORWARD             8 (to 26)
        >>   18 LOAD_NAME                1 (b)
             20 CALL_FUNCTION            0
             22 POP_TOP
             24 RERAISE
>>> with a() as b:
  2           0 LOAD_NAME                0 (a)
              2 CALL_FUNCTION            0
              4 SETUP_WITH              24 (to 30)
              6 STORE_NAME               1 (b)
>>>     b.c()
  3           8 LOAD_NAME                1 (b)
             10 LOAD_METHOD              2 (c)
             12 CALL_METHOD              0
             14 POP_TOP
             16 POP_BLOCK
             18 LOAD_CONST               0 (None)
             20 DUP_TOP
             22 DUP_TOP
             24 CALL_FUNCTION            3
             26 POP_TOP
             28 JUMP_FORWARD            16 (to 46)
        >>   30 WITH_EXCEPT_START
             32 POP_JUMP_IF_TRUE        36
             34 RERAISE
        >>   36 POP_TOP
             38 POP_TOP
             40 POP_TOP
             42 POP_EXCEPT
             44 POP_TOP
>>> d()
  4     >>   46 LOAD_NAME                3 (d)
             48 CALL_FUNCTION            0
             50 POP_TOP

"""


@dataclass
class TryOffset:
    offset: int
    stack_depth: int


@dataclass
class WithOffset:
    offset: int
    stack_depth: int
    instance: GetName


@dataclass
class VMException(Exception):
    exception: Exception
    traceback: List[Tuple["Function", int]]
    except_in_handler: Optional[Exception] = None


class JumpIfNotExcMatch(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        compare_type = sandbox.pop()
        except_type = sandbox.pop()
        if isinstance(compare_type, tuple):
            if not any(isinstance(except_type, error) for error in compare_type):
                sandbox.context.pc = self.operand
        elif not isinstance(except_type, compare_type):
            sandbox.context.pc = self.operand


class LoadAssertionError(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.push(AssertionError)


class PopBlock(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        with_offset = sandbox.context.try_stack.pop()
        if isinstance(with_offset, WithOffset):
            sandbox.push(with_offset.instance.get_name("__exit__"))


class PopExcept(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.try_stack.pop()


class RaiseVarArgs(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        if self.operand == 0:
            # re-raise
            sandbox.context.try_stack.pop()
            sandbox.next_except_handler()
        else:
            assert self.operand != 2, "TODO: raise with cause"
            raise sandbox.pop()


class Reraise(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        sandbox.context.try_stack.pop()
        sandbox.next_except_handler()


class SetupFinally(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        try_offset = TryOffset(sandbox.context.pc + self.operand, len(sandbox.context.data_stack))
        sandbox.context.try_stack.append(try_offset)


class SetupWith(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        instance = sandbox.pop()
        with_offset = WithOffset(sandbox.context.pc + self.operand, len(sandbox.context.data_stack), instance)
        sandbox.context.try_stack.append(with_offset)
        sandbox.call_function(instance.get_name("__enter__"), instance)


class WithExceptStart(CodeLine):
    def exec(self, sandbox: SandBox):
        super().exec(sandbox)
        try_offset = sandbox.context.try_stack[-1]
        assert isinstance(try_offset, WithOffset)
        sandbox.push(try_offset.instance)
        sandbox.call_function(try_offset.instance.get_name("__exit__"), sandbox.peek(-1), sandbox.peek(-2), sandbox.peek(-3))
