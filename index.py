import cherrypy,os
from my_classes import Update,Callback


WEBHOOK_LISTEN = '0.0.0.0'

class Halo(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
        MsgUpdate=cherrypy.request.json
        print(MsgUpdate)
        if MsgUpdate.get('callback_query') is None:
            upd = Update(MsgUpdate)
            upd.main()
        else:
            callback=Callback(MsgUpdate)
            callback.main()
port=os.environ['PORT']
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port':int(port)
    })
cherrypy.quickstart(Halo())
