import logging
import queue
import threading

log = logging.getLogger(__name__)

task_queue = queue.Queue()


# Usage:
"""
task_queue.put(lambda: print("long running task"))
"""


def fifo_queue():
    def worker():
        while True:
            item = task_queue.get()
            log.info("Working on task from task_queue")
            try:
                item()  # Execute task
                task_queue.task_done()
                log.info("Finished working on task from task_queue")
            except Exception as e:
                log.error(f"Error running task: {e}")

    # turn-on the worker thread
    threading.Thread(target=worker, daemon=True).start()

    # block until all tasks are done
    task_queue.join()


thread = threading.Thread(target=fifo_queue)
thread.start()
