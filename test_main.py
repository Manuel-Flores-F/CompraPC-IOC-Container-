from expects import equal, expect
from cj import Container
# para Intefaz web
from flask import Flask, jsonify, request, redirect, url_for
from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__)

class IVideo:
    def get_name(self, msg):
        pass

class VideoIntegrado (IVideo):
    def get_name(self, msg):
        print("Motor Electrico")
        return "Motor Electrico"

class VideoDedicado (IVideo):
    def get_name(self, msg):
        print("Motor Gas")
        return "Motor Gas"
class IDisco:
    def get_name(self):
        pass

class DiscoHD(IDisco):
    def get_name(self):
        return "Ruedas tipo A"

class PC:
    def __init__(self, motor:IVideo, ruedas: IDisco):
        self.motor=motor
        self.ruedas=ruedas

    def get_description(self):
        print("PC con "+self.motor.get_name("")+' y '+self.ruedas.get_name())

def test_of_dependencies():        
    container = Container()
    container.register(IVideo, VideoIntegrado)
    container.register(IDisco, DiscoHD)
    container.register(PC)


    instance = container.resolve(IVideo)
    instance.get_name("beep")
    PC1 = container.resolve(PC)
    PC1.get_description()

# Funciones de rutas
@app.route('/')
def home():
    return render_template('layout.html')


# Funcion Principal   
if __name__ == "__main__":
    test_of_dependencies()
    app.run(debug=True, host='0.0.0.0')
