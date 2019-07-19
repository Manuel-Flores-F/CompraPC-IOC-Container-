from expects import equal, expect
from cj import Container
# para Intefaz web
from flask import Flask, jsonify, request, redirect, url_for
from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__)

# Interfaces ---------------------------------
class IVideo:
    def get_name(self, msg):
        pass
class IDisco:
    def get_name(self):
        pass

# Implementaciones de Dependencias -----------
class VideoIntegrado (IVideo):
    def get_name(self, msg):
        print("Video Integrado")
        return "Video Integrado"

class VideoDedicado (IVideo):
    def get_name(self, msg):
        print("Video Dedicado")
        return "Video Dedicado"

class DiscoHDD(IDisco):
    def get_name(self):
        return "Disco Mecánico"

class DiscoSSD(IDisco):
    def get_name(self):
        return "Disco Estado Solido"

# Implementacion de la clase dependiente --------
class PC:
    def __init__(self, video:IVideo, disco: IDisco):
        self.video=video
        self.disco=disco

    def get_description(self):
        print("PC con "+self.video.get_name("")+' y '+self.disco.get_name())

def test_of_dependencies():        
    container = Container()
    container.register(IVideo, VideoIntegrado)
    container.register(IDisco, DiscoHDD)
    container.register(PC)


    instance = container.resolve(IVideo)
    instance.get_name("")
    
    PC1 = container.resolve(PC)
    PC1.get_description()


@app.route('/')
def home():
    return render_template('layout.html')
if __name__ == "__main__":
    test_of_dependencies()
    app.run(debug=True, host='0.0.0.0')
