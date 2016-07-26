import threading

class Queue(object):

    def __init__(self):
        self.lock=threading.Lock()
        self.list=[]

    def poll(self):
        self.lock.acquire()
        if len(self.list)>0:
            return self.list.pop(0)
        self.lock.release()
        return None

    def queue(self, obj):
        self.lock.acquire()
        self.list.append(obj)
        self.lock.release()

    def set_list(self, l):
        self.lock.acquire()
        self.list=l
        self.lock.release()

    def get_list_copy(self, l):
        self.lock.acquire()
        result = list(self.list)
        self.lock.release()
        return result
        

    
            
