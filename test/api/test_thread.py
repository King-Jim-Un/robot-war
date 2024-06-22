import logging

from test.api import run_in_vm

# Constants:
LOG = logging.getLogger(__name__)


@run_in_vm
def test_thread():
    from time import sleep
    from thread import Thread

    log = ["starting in main thread"]

    def func1(arg: str):
        log.append("in func1 arg=" + arg)
        sleep(0.030)
        log.append("func1 done")
        return 1

    def func2():
        sleep(0.015)
        log.append("in func2 and done")
        return 2

    thread1 = Thread().start(func1, "ARRGH")
    thread2 = Thread().start(func2)

    assert thread1.join() == 1
    assert thread2.join() == 2
    assert log == ["starting in main thread", "in func1 arg=ARRGH", "in func2 and done", "func1 done"]


@run_in_vm
def test_thread_subclass():
    from thread import Thread

    class MyThread(Thread):
        const = 10

        def thread(self, arg1, arg2):
            return self.const + arg1 + arg2

        def run(self):
            self.start(self.thread, 15, 20)
            assert self.join() == 45

    MyThread().run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_thread_subclass()
