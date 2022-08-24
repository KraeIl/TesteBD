from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import banco
import os, sys, win32print, win32api
import time as t
from datetime import *
    
def calcPagamento(horaSaida, horaEntrada):
    hE = datetime.strptime(horaEntrada, '%d/%m/%Y %H:%M:%S') 
    permanencia = horaSaida - hE

    diaria = False
    if permanencia.days == 0:
        tempoPermanencia = datetime.strptime(str(permanencia), '%H:%M:%S.%f')
    if permanencia.days == 1:
        tempoPermanencia = datetime.strptime(str(permanencia), '%d day, %H:%M:%S.%f')
        diaria = True
    if permanencia.days > 1:
        tempoPermanencia = datetime.strptime(str(permanencia), '%d days, %H:%M:%S.%f')
        diaria = True

    if (diaria):
        totalminutos = (tempoPermanencia.day*24*60) + (tempoPermanencia.hour*60) + tempoPermanencia.minute
    else:
        totalminutos = (tempoPermanencia.hour*60) + tempoPermanencia.minute

    if totalminutos < 5:
        return 0
    elif totalminutos < 65:
        return 6.00
    elif totalminutos > 185:
        períodos = (totalminutos//720)
        tarifa = 15 + (períodos*15)
        return tarifa
    else:
        horas = ((totalminutos-60)//60)
        tarifa = 9+(3*horas)
        return tarifa

def popular():
    tv.delete(*tv.get_children())
    carros_no_patio.clear()
    vquery= "SELECT * FROM tb_carros order by T_HORARIOENT"
    linhas= banco.dql(vquery)
    for i in linhas:
        if i[3] != None:
            continue
        else:
            horaSaida = datetime.now()
            tarifa = calcPagamento(horaEntrada=i[2], horaSaida= horaSaida)
            tv.insert("", "end", values= (i[0], i[1], i[2], str(tarifa)))
            carros_no_patio.append(i)

def autocompletar(e):
    cplaca.delete(0, END)
    cmodelo.delete(0, END)

    carro= tv.item(tv.selection()[0], "values")
    valorPlaca = carro[0]
    valorModelo = carro[1]
    cplaca.insert(0, valorPlaca)
    cmodelo.insert(0, valorModelo)
    cmodelo.focus()

def atualizar(dados):
    t.sleep(0.1)
    tv.delete(*tv.get_children())
    for i in dados:
        if i[3] != None:
            continue
        else:
            horaSaida = datetime.now()
            tarifa = calcPagamento(horaEntrada=i[2], horaSaida= horaSaida)
            tv.insert("", "end", values= (i[0], i[1], i[2], "R$: " + str(tarifa)))
    
    try:
        valorModelo = dados[0][1]
        valorPlaca = dados[0][0]
    except: 
        valorModelo = ''
        valorPlaca = ''

    tamDigitado = len(cplaca.get())

    if cplaca.get() == '':
        cmodelo.delete(0, END)
    else:    
        digitado = cplaca.get().lower()
        placaInserir = valorPlaca.lower()
        
        for char in digitado:
            placaInserir = placaInserir.replace(char, '', 1)

        cmodelo.delete(0, END)
        cmodelo.insert(0, valorModelo)
        cplaca.insert(tamDigitado, placaInserir.upper())
        cplaca.selection_range(tamDigitado, END)

def autocompletar(e):
    cplaca.delete(0, END)
    cmodelo.delete(0, END)

    carro= tv.item(tv.selection()[0], "values")
    valorPlaca = carro[0]
    valorModelo = carro[1]
    cplaca.insert(0, valorPlaca)
    cmodelo.insert(0, valorModelo)
    cmodelo.focus()

def checarM(e):
    vquery= "SELECT * FROM tb_carros order by T_HORARIOENT"
    carros= banco.dql(vquery)
    digitadoM = cmodelo.get()
    cmodelo.delete(0, END)
    cmodelo.insert(0, digitadoM.upper())
    
    if digitadoM != '':
        if e.keysym != "BackSpace" and e.keysym != "Delete":
            dados = []
            for item in carros:
                modelo = item[1]
                if digitadoM.lower() in modelo.lower():
                    if modelo not in dados:
                        dados.append(item)
        else:
            return
    else: 
        return
    
    try:
        valorModelo = dados[0][1]
    except: 
        valorModelo = ''

    t.sleep(0.1)
    tamDigitado = len(cmodelo.get())
    digitado = cmodelo.get().lower()
    modeloInserir = valorModelo.lower()
        
    for char in digitado:
        modeloInserir = modeloInserir.replace(char, '', 1)

    cmodelo.insert(tamDigitado, modeloInserir.upper())
    cmodelo.selection_range(tamDigitado, END)

def checar(e):
    vquery= "SELECT * FROM tb_carros order by T_HORARIOENT"
    carros= banco.dql(vquery)
    digitadoP = cplaca.get()
    tamDigitado = len(cplaca.get())
    cplaca.delete(0, END)
    cplaca.insert(0, digitadoP.upper())

    if tamDigitado > 7:
        messagebox.showerror("ERRO!", "Limite máximo de caracteres excedido!")
        cplaca.delete(7, END)

    if tamDigitado <= 3:
        nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        if e.keysym in nums:
            messagebox.showerror("ERRO!", "Caractere Inválido!")
            cplaca.delete(0, END)
            return
    
    if tamDigitado > 3:
        nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        if e.keysym not in nums:
            if e.keysym != "Return" and e.keysym != "BackSpace" and e.keysym != "Delete": 
                messagebox.showerror("ERRO!", "Caractere Inválido!")
                cplaca.delete(0, END)
                cmodelo.delete(0, END)
                return

    if e.keysym != "BackSpace" and e.keysym != "Delete":
        
        if digitadoP == '': 
            dados= carros

        else:
            dados = []
            for item in carros:
                placa = item[0]
                if digitadoP.lower() in placa.lower():
                    if placa not in dados:
                        dados.append(item)
        
        atualizar(dados)
    else:
        cmodelo.delete(0, END)
        if cplaca.get() == '':
            popular()

    
def fococModelo():
    try:
        vquery= "SELECT * FROM tb_carros WHERE T_PLACA LIKE '%" + cplaca.get()+ "%'"
        carros = banco.dql(vquery)
    
        for carro in carros:
            if carro[3] == None:
                inserir()
                return
        
        cmodelo.focus()
    except:
        cmodelo.focus()

def imprimir(horaEnt, vPlaca, vModelo):
    impressora = win32print.EnumPrinters(2)[3]
    win32print.SetDefaultPrinter(impressora[2])
    pasta = os.path.dirname(__file__)
    caminho = pasta + "\\impressão\\impressão.txt"
    with open(caminho, 'w') as f: 
        texto = "***CESAR PARK*** \n HORARIO DE ENTRADA: {} \n PLACA: {}, MODELO: {} \n".format(horaEnt, vPlaca, vModelo)  
        f.write(texto)
        f.close()
    
    os.startfile(caminho, "print")

def inserir():
    if cplaca.get()== "" or cmodelo.get()== "":
        messagebox.showerror(title= "ERRO", message= "Preencha todos os campos!!")
        cplaca.focus()
        return
    
    e = datetime.now()
    horaEnt = "%s/%s/%s " % (e.day, e.month, e.year)
    horaEnt += "%s:%s:%s" % (e.hour, e.minute, e.second)

    try:
        vquery= "SELECT * FROM tb_carros WHERE T_PLACA LIKE '%" + cplaca.get() + "%'"
        carros= banco.dql(vquery)
        
        for c in carros:
            vPlaca= c[0]
            vSaida= c[3]
            vEntrada= c[2]
       
        if vSaida == None:
            saida(vPlaca, vEntrada)

        else:
            print("aaa")
            vquery= "INSERT INTO tb_carros (T_PLACA, T_MODELO, T_HORARIOENT, C_TIPO) VALUES ('"+cplaca.get().upper()+"','"+cmodelo.get().upper()+"','"+horaEnt+"','A')"
            banco.dml(vquery)
            #imprimir(horaEnt= horaEnt, vPlaca= cplaca.get().upper(), vModelo= cmodelo.get().upper())
                
    except Exception as e:
        vquery= "INSERT INTO tb_carros (T_PLACA, T_MODELO, T_HORARIOENT, C_TIPO) VALUES ('"+cplaca.get().upper()+"','"+cmodelo.get().upper()+"','"+horaEnt+"','A')"
        banco.dml(vquery)
        #imprimir(horaEnt= horaEnt, vPlaca= cplaca.get().upper(), vModelo= cmodelo.get().upper())

    popular()
    cplaca.delete(0, END)
    cmodelo.delete(0, END)    
    cplaca.focus()

def saida(vPlaca, horaEnt):

    e = datetime.now()
    horaSaida = "%s/%s/%s " % (e.day, e.month, e.year)
    horaSaida += "%s:%s:%s" % (e.hour, e.minute, e.second)     
    
    try:
        vquery= "UPDATE tb_carros SET T_HORARIOSAIDA='%s' WHERE T_PLACA= '%s' AND T_HORARIOSAIDA IS NULL" % (horaSaida, vPlaca)
        tarifa = calcPagamento(horaSaida = e, horaEntrada= horaEnt)
        messagebox.showwarning(title= "PAGAMENTO", message= "O valor ficou em R$ %s Reais" % (tarifa))
        banco.dml(vquery)
        popular()

    except Exception as e:
        messagebox.showerror(title= "ERRO", message= e)
        return 

def pesquisar():

    if cplaca.get()== "":
            popular()

    else:
        tv.delete(*tv.get_children())
        vquery= "SELECT * FROM tb_carros WHERE T_PLACA LIKE '%" + cplaca.get()+ "%'"
        linhas= banco.dql(vquery)

        for i in linhas:
            if i[3] != None:
                continue
        else:
                tv.insert("", "end", values= i)



app = Tk() 
app.title("Estacionamento")
app.geometry("420x340")
app.configure(background="#dde")
app.resizable(False, False)


#quadroGrid
quadroGrid= LabelFrame(app, text= "Carros")
quadroGrid.pack(fill="both", expand="yes", padx=10, pady= 10)

#TreeView
tv = ttk.Treeview(quadroGrid, columns= ('placa', 'modelo', 'horaEnt', "tarifa"), show= 'headings')
tv.column('placa', minwidth= 0, width= 70)
tv.column('modelo', minwidth= 0, width= 100)
tv.column('horaEnt', minwidth= 0, width= 115)
tv.column('tarifa', minwidth= 0, width= 65)
tv.heading('placa', text= 'Placa')
tv.heading('modelo', text= 'Modelo')
tv.heading('horaEnt', text= 'Horário de Entrada')
tv.heading('tarifa', text= 'Tarifa')
tv.bind("<<TreeviewSelect>>", autocompletar)
tv.pack()
carros_no_patio = []
popular()

#quadroInserir
quadroInserir = LabelFrame(app, text= "Inserir, pesquisar ou dar baixa em carros")
quadroInserir.pack(fill= "both", expand= "yes", padx= 10, pady= 10)

#Labels
Label(quadroInserir, text= "Placa: ", background= "#dde", foreground= "#009").grid(column= 0, row= 0, padx= 5, pady= 5)
Label(quadroInserir, text= "Modelo: ", background= "#dde", foreground= "#009").grid(column= 2, row= 0, padx= 5, pady= 5)

#Entryes
cplaca = Entry(quadroInserir)
cplaca.grid(column= 1, row= 0, padx= 5, pady= 5)
cplaca.bind('<KeyRelease>', checar)
cplaca.bind('<Return>', (lambda event: fococModelo()))

cmodelo = Entry(quadroInserir)
cmodelo.grid(column= 3, row= 0, padx= 5, pady= 5)
cmodelo.bind('<KeyRelease>', checarM)
cmodelo.bind('<Return>', (lambda event: inserir()))

cplaca.focus()
app.mainloop()