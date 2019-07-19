from expects import equal, expect
from cj import Container
# para Intefaz web
import formsFunc as ff
from flask import Flask, jsonify, request, redirect, url_for
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_key'
bootstrap = Bootstrap(app)

result=''
list_items=[]

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

# Funciones de rutas
@app.route('/', methods=('GET','POST'))
def home():
    return render_template('base.html', title='UNI')

@app.route('/Buy/',methods=('GET','POST'))
def buy():
    form_pc = ff.pc_form()
    if form_pc.validate_on_submit():
        try:
            return render_template('form.html',title='Comprar',usr_name='Usuario', form=form_pc)
        except:
            return render_template('404.html',title=Error)
    
    return render_template('form.html',title='Comprar',usr_name='Usuario', form=form_pc)

@app.route('/Result/', methods=('GET','POST'))
def show_result():
    result='S/. '+ str(1000)
    list_items={'memoria':10,'disco':20,'video':30}
    return render_template('result.html',title='Resultado',result=result, usr_name='Usuario', list_items=list_items)

# Funcion Principal   
if __name__ == "__main__":
    test_of_dependencies()
    app.run(debug=True, host='0.0.0.0')
