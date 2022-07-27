from email import message_from_binary_file
from email.mime import message
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from sqlalchemy import false
import banco
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
        períodos = (totalminutos/720) - ((totalminutos/720)%1)
        tarifa = 15 + (períodos*15)
        return tarifa
    else:
        horas = ((totalminutos-60)/60) - (((totalminutos-60)/60)%1)
        tarifa = 9+(3*horas)
        return tarifa

def popular():
    tv.delete(*tv.get_children())
    carros_no_patio.clear()
    vquery= "SELECT * FROM tb_carros order by T_HORARIOENT"
    linhas= banco.dql(vquery)
    for i in linhas:
        if i[5]== 0:
            continue
        else:
            tv.insert("", "end", values= i)
            carros_no_patio.append(i)

def autocompletar(e):
    cplaca.delete(0, END)
    cmodelo.delete(0, END)

    carro= tv.item(tv.selection()[0], "values")
    valorPlaca = carro[1]
    valorModelo = carro[2]
    cplaca.insert(0, valorPlaca)
    cmodelo.insert(0, valorModelo)
    cmodelo.focus()

def atualizar(dados):
    tv.delete(*tv.get_children())
    for i in dados:
       tv.insert("", "end", values= i)

def checar(e):
    digitadoP = cplaca.get()
    digitadoM = cmodelo.get()

    if digitadoP == '': 
        if digitadoM == '':
            dados= carros_no_patio
        else:
            dados = []
            for item in carros_no_patio:
                modelo = item[2]
                if digitadoM.lower() in modelo.lower():  
                    dados.append(item)
    else:
        if digitadoM == '':
            dados = []
            for item in carros_no_patio:
                placa = item[1]
                if digitadoP.lower() in placa.lower():  
                    dados.append(item)
        else:
            for item in carros_no_patio:
                placa = item[1]
                modelo = item[2]
                if digitadoP.lower() in placa.lower(): 
                    if digitadoM.lower() in modelo.lower():
                        dados.append(item)

    atualizar(dados)

def inserir():
    if cplaca.get()== "" or cmodelo.get()== "":
        messagebox.showerror(title= "ERRO", message= "Preencha todos os campos!!")
        cplaca.focus()
        return
    
    e = datetime.now()
    horaEnt = "%s/%s/%s " % (e.day, e.month, e.year)
    horaEnt += "%s:%s:%s" % (e.hour, e.minute, e.second)

    try:
        vquery= "SELECT * FROM tb_carros WHERE T_PLACA LIKE '%" + cplaca.get()+ "%'"
        carros= banco.dql(vquery)
        for c in carros:
            vTicket= c[0]
            vPatio= c[5]
            vTicket= c[0]
            vEntrada= c[3]
       
        if vPatio== 1:
            deletar(c[0], c[3])
            cplaca.delete(0, END)
            cmodelo.delete(0, END)    
            cplaca.focus()
            return
    
        print(vTicket)
        vquery= "UPDATE tb_carros SET I_ESTANOPATIO= '1', T_HORARIOENT='%s' WHERE I_TICKET=%s" % (horaEnt, vTicket)
        banco.dml(vquery)

    except Exception as e:
        print(e)
        vquery= "INSERT INTO tb_carros (T_PLACA, T_MODELO, T_HORARIOENT, I_ESTANOPATIO) VALUES ('"+cplaca.get()+"','"+cmodelo.get()+"','"+horaEnt+"', '1')"
        banco.dml(vquery)

    popular()
    cplaca.delete(0, END)
    cmodelo.delete(0, END)    
    cplaca.focus()


def deletar(vTicket, horaEnt):

    e = datetime.now()
    horaSaida = "%s/%s/%s " % (e.day, e.month, e.year)
    horaSaida += "%s:%s:%s" % (e.hour, e.minute, e.second)     
    
    try:
        vquery= "UPDATE tb_carros SET I_ESTANOPATIO= '0', T_HORARIOSAIDA='%s'  WHERE I_TICKET='%s'" % (horaSaida, vTicket)
        tarifa = calcPagamento(horaSaida = e, horaEntrada= horaEnt)
        messagebox.showwarning(title= "PAGAMENTO", message= "O valor ficou em R$ %s Reais" % (tarifa))
        banco.dml(vquery)
        popular()

    except Exception as e:
        messagebox.showerror(title= "ERRO", message= e)
        return 

def pesquisar():

    if cplaca.get()== "":

        if cmodelo.get()== "":
            popular()

        else: 
            tv.delete(*tv.get_children())
            vquery= "SELECT * FROM tb_carros WHERE T_MODELO LIKE '%" + cmodelo.get()+ "%'"
            linhas= banco.dql(vquery)

            for i in linhas:
                if i[5]== 0:
                    continue
                else:
                    tv.insert("", "end", values= i)

    else:

        if cmodelo.get()== "":
            tv.delete(*tv.get_children())
            vquery= "SELECT * FROM tb_carros WHERE T_PLACA LIKE '%" + cplaca.get()+ "%'"
            linhas= banco.dql(vquery)

            for i in linhas:
                if i[5]== 0:
                    continue
                else:
                    tv.insert("", "end", values= i)

        else:
            tv.delete(*tv.get_children())
            vquery= "SELECT * FROM tb_carros WHERE T_PLACA LIKE '%" + cplaca.get()+ "%' AND T_MODELO LIKE '%" + cmodelo.get()+ "%'"
            linhas= banco.dql(vquery)

            for i in linhas:
                if i[5]== 0:
                    continue
                else:
                    tv.insert("", "end", values= i)
  


app = Tk() 
app.title("Estacionamento")
app.geometry("420x400")
app.configure(background="#dde")


#quadroGrid
quadroGrid= LabelFrame(app, text= "Carros")
quadroGrid.pack(fill="both", expand="yes", padx=10, pady= 10)

#TreeView
tv = ttk.Treeview(quadroGrid, columns= ('ticket', 'placa', 'modelo', 'horaEnt', "tarifa"), show= 'headings')
tv.column('ticket', minwidth= 0, width= 50)
tv.column('placa', minwidth= 0, width= 70)
tv.column('modelo', minwidth= 0, width= 100)
tv.column('horaEnt', minwidth= 0, width= 115)
tv.column('tarifa', minwidth= 0, width= 50)
tv.heading('ticket', text= 'Ticket')
tv.heading('placa', text= 'Placa')
tv.heading('modelo', text= 'Modelo')
tv.heading('horaEnt', text= 'Horário de Entrada')
tv.heading('tarifa', text= 'Tarifa')
tv.bind("<<TreeviewSelect>>", autocompletar)
tv.pack()
carros_no_patio = []
popular()

#quadroInserir
quadroInserir = LabelFrame(app, text= "Inserir ou pesquisar carros")
quadroInserir.pack(fill= "both", expand= "yes", padx= 10, pady= 10)

#Labels
Label(quadroInserir, text= "Placa: ", background= "#dde", foreground= "#009").grid(column= 0, row= 0, padx= 5, pady= 5)
Label(quadroInserir, text= "Modelo: ", background= "#dde", foreground= "#009").grid(column= 2, row= 0, padx= 5, pady= 5)

#Entryes
cplaca = Entry(quadroInserir)
cplaca.grid(column= 1, row= 0, padx= 5, pady= 5)
cplaca.bind('<KeyRelease>', checar)

cmodelo = Entry(quadroInserir)
cmodelo.grid(column= 3, row= 0, padx= 5, pady= 5)
cmodelo.bind('<Return>', (lambda event: inserir()))
cmodelo.bind('<KeyRelease>', checar)


#Buttons
btn_inserir= Button(quadroInserir, text= "Inserir", command= inserir)
btn_deletar= Button(quadroInserir, text= "Deletar", command= deletar)
btn_pesquisar= Button(quadroInserir, text= "Pesquisar", command= pesquisar)

btn_pesquisar.grid(column= 3, row= 1)

app.mainloop()