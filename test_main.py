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
list_items={}
PC1=''
# Interfaces ##############################################################
class IVideo:
    def get_name(self, msg):
        pass
class IDisco:
    def get_name(self):
        pass
class IMemoria:
    def get_name(self):
        pass
# Implementaciones de Dependencias ########################################
class VideoIntegrado (IVideo):
    def __init__(self):
        self.price=100
    def get_name(self):
        return "Video Integrado"

class VideoDedicado (IVideo):
    def __init__(self):
        self.price=200
    def get_name(self):
        return "Video Dedicado"

class DiscoHDD(IDisco):
    def __init__(self):
        self.price=50
    def get_name(self):
        return "Disco Mecánico"

class DiscoSSD(IDisco):
    def __init__(self):
        self.price=100
    def get_name(self):
        return "Disco Estado Solido"

class MemoriaDDR3(IMemoria):
    def __init__(self):
        self.price=40
    def get_name(self):
        return "Memoria DDR3"

class MemoriaDDR4(IMemoria):
    def __init__(self):
        self.price=80
    def get_name(self):
        return "Memoria DDR4"

# Implementacion de la clase dependiente ###################################
class PC:
    list={}
    def __init__(self, memoria: IMemoria, video:IVideo, disco: IDisco):
        self.memoria=memoria
        self.disco=disco
        self.video=video                
    def get_price(self):
        return self.memoria.price+self.disco.price+self.video.price
    def get_description(self):
        self.list={self.memoria.get_name():self.memoria.price, self.disco.get_name(): self.disco.price, self.video.get_name():self.video.price}
        print("Descripcion PC:"+'\n\t - '+self.memoria.get_name()+'\n\t - '+self.disco.get_name()+'\n\t - '+self.video.get_name())

def inject_dependencies(list_items):
    global PC1
    container = Container()
    container.register(PC)

    for key, value in list_items.items():
        if key == 'memoria':
            if value == 'mem_op1':
                container.register(IMemoria, MemoriaDDR3)
            else:
                container.register(IMemoria, MemoriaDDR4)

        if key == 'disco':
            if value == 'disk_op1':
                container.register(IDisco, DiscoHDD)
            else:
                container.register(IDisco, DiscoSSD)
        if key == 'video':
            if value == 'video_op1':
                container.register(IVideo, VideoIntegrado)
            else:
                container.register(IVideo, VideoDedicado)
    
    PC1 = container.resolve(PC)
    PC1.get_description()

# Funciones de rutas #####################################################
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('base.html', title='UNI', img = 1)

@app.route('/Buy/',methods=['GET', 'POST'])
def buy():
    global list_items
    form_pc = ff.pc_form()
    list_items['memoria'] = form_pc.radio_group_memory.data
    list_items['disco'] = form_pc.radio_group_disk.data
    list_items['video'] = form_pc.radio_group_video.data
    print(list_items)
    if list_items['memoria']=='None' or list_items['disco']=='None' or list_items['video']=='None':
        return render_template('form.html',title='Comprar',usr_name='Usuario', form=form_pc)
    else:
        inject_dependencies(list_items)
        return redirect(url_for('show_result'))

@app.route('/Result/', methods=['GET', 'POST'])
def show_result():
    global PC1
    result = PC1.get_price()
    list=PC1.list
    return render_template('result.html',title='Resultado',result=result, usr_name='Usuario', list_items=list)

# Funcion Principal  #################################################
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1')##
