from services.docs import handlers as docs_handlers
from home import handlers as home_handlers

handlers = []
handlers.extend(docs_handlers)
handlers.extend(home_handlers)
