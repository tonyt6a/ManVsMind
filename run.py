from multiprocessing import Process, Array, Lock
from game import main as game_main
from ManVsMind import main as MVM_main

def run_test(arr, lock):
    game_main(arr, lock)   # Ensure script1 has no execution code at the top level

def run_MVM(arr, lock):
    int()

if __name__ == '__main__':
    arr = Array('i', 3)
    lock = Lock()
    process1 = Process(target=run_test, args=(arr, lock))
    process2 = Process(target=run_MVM, args=(arr, lock))

    process1.start()
    process2.start()

    process1.join()
    process2.join()