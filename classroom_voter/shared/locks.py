# https://blog.majid.info/a-reader-writer-lock-for-python/
import threading

class RWLock:

    def __init__(self):
        self.rwlock = 0
        self.writers_waiting = 0
        self.database_lock = threading.Lock()
        self.database_readers_ok = threading.Condition(self.database_lock)
        self.database_writers_ok = threading.Condition(self.database_lock)
        
    def acquire_read(self):
        """Acquire a read lock. Several threads can hold this typeof lock.
        It is exclusive with write locks."""
        self.database_lock.acquire()
        while self.rwlock < 0 or self.writers_waiting:
            self.database_readers_ok.wait()
        self.rwlock += 1
        self.database_lock.release()
    
    def acquire_write(self):
        """Acquire a write lock. Only one thread can hold this lock, and
        only when no read locks are also held."""
        self.database_lock.acquire()
        while self.rwlock != 0:
            self.writers_waiting += 1
            self.database_writers_ok.wait()
            self.writers_waiting -= 1
        self.rwlock = -1
        self.database_lock.release()
    
    def release(self):
        self.database_lock.acquire()
        if self.rwlock < 0:
            self.rwlock = 0
        else:
            self.rwlock -= 1
      
        wake_writers = self.writers_waiting and self.rwlock == 0
        wake_readers = self.writers_waiting == 0
        self.database_lock.release()
    
        if wake_writers:
            self.database_writers_ok.acquire()
            self.database_writers_ok.notify()
            self.database_writers_ok.release()
        elif wake_readers:
            self.database_readers_ok.acquire()
            self.database_readers_ok.notifyAll()
            self.database_readers_ok.release()

