import queue
import threading

task_queue = queue.Queue()


# Usage:
"""
task_queue.put(lambda: print("long running task"))
"""


def fifo_queue():
    def worker():
        while True:
            item = task_queue.get()
            print("Working on task from task_queue")
            try:
                item()  # Execute task
                task_queue.task_done()
                print("Finished working on task from task_queue")
            except Exception as e:
                print(f"Error running task: {e}")

    # turn-on the worker thread
    threading.Thread(target=worker, daemon=True).start()

    # block until all tasks are done
    task_queue.join()


thread = threading.Thread(target=fifo_queue)
thread.start()
