from multiprocessing import Process, Queue
from test import main as test_main
from ManVsMind import main as MVM_main

def run_test(queue:Queue):
    test_main(queue)   # Ensure script1 has no execution code at the top level

def run_MVM(queue:Queue):
      # Ensure script2 has no execution code at the top level
      MVM_main(queue)

if __name__ == '__main__':
    queue = Queue()
    process1 = Process(target=run_test, args=(queue,))
    process2 = Process(target=run_MVM, args=(queue,))

    process1.start()
    process2.start()

    process1.join()
    process2.join()