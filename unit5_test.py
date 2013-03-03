__author__ = 'Artiom'

import time

# complex_computation() simulates a slow function. time.sleep(n) causes the
# program to pause for n seconds. In real life, this might be a call to a
# database, or a request to another web service.
def complex_computation(a, b):
    time.sleep(.5)
    return a + b

# QUIZ - Improve the cached_computation() function below so that it caches
# results after computing them for the first time so future calls are faster
cache = {}
def cached_computation(a, b):
    global cache
    key="%s,%s" % (a,b)
    if key not in cache:
        cache[key]=complex_computation(a, b)
    return cache[key]
    ###Your code here.

start_time = time.time()
print cached_computation(5, 3)
print "the first computation took %f seconds" % (time.time() - start_time)

start_time2 = time.time()
print cached_computation(5, 3)
print "the second computation took %f seconds" % (time.time() - start_time2)



CACHE = {}

#return True after setting the data
def set(key, value):
    CACHE[key] = value
    return True

#return the value for key
def get(key):
    return CACHE.get(key)

#delete key from the cache
def delete(key):
    if key in CACHE:
        del CACHE[key]

#clear the entire cache
def flush():
    CACHE.clear()

# QUIZ - implement gets() and cas() below
#return a tuple of (value, h), where h is hash of the value. a simple hash
#we can use here is hash(repr(val))
def gets(key):
    if get(key):
        return (get(key),hash(repr(get(key))))
    else:
        return None
        ###Your gets code here.

# set key = value and return True if cas_unique matches the hash of the value
# already in the cache. if cas_unique does not match the hash of the value in
# the cache, don't set anything and return False.
def cas(key, value, cas_unique):
###Your cas code here.
    #k_h = gets(key)
    if gets(key)[1]==cas_unique:
        set(key,value)
        return True
    else:
        return False

print set('x', 1)
#>>> True
#
print get('x')
#>>> 1
#
print get('y')
#>>> None
#
delete('x')
print get('x')
#>>> None
#
set('x', 2)
print gets('x')
#>>> 2, HASH
#
print "cas"
print cas('x', 3, 0)
#>>> False
#
print "cas"
print cas('x', 4, 2105051955)
#>>> True
#
#print get('x')
#>>> 4
