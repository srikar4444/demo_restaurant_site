from .base import *

#from .local import *

# this is just for an example to show how to create a local database server
# from .local_srikar import *

from .production import *

try:
    from .local import *
except:
    pass

#try:
#    from .local_srikar import *
#except:
#    pass

# in this first everything will be imported from .base and then overridden by
# local which is overridden by local_justin and then by production

# to work on a specific thing comment other things