import tkinter as tk
from tkinter import messagebox
import sympy as sp
from fpdf import FPDF
import os

def metodo_secante(funcion_str, xi_menos1, xi, error_absoluto_ingresado, decimales):
    x = sp.symbols('x')
    funcion = sp.sympify(funcion_str)
    
    xi_menos1 = round(float(xi_menos1), decimales)
    xi = round(float(xi), decimales)
    iteraciones = []
    paso = 1
    
    #esto almacena la cadena de funcion original para su visualizacion en el PDF
    funcion_original = funcion_str
    
    while True:
        #evaluamos la funcion en xi-1 y xi
        f_xi_menos1_expr = funcion.subs(x, xi_menos1)
        f_xi_menos1 = round(float(f_xi_menos1_expr.evalf()), decimales)
        
        f_xi_expr = funcion.subs(x, xi)
        f_xi = round(float(f_xi_expr.evalf()), decimales)
        
        #aca guardamos las expresiones sustituidas para mostrar en el PDF
        f_xi_menos1_calculo = funcion_str.replace('x', f'({xi_menos1})')
        f_xi_calculo = funcion_str.replace('x', f'({xi})')
        
        #aca calculamos xi+1 usando el metodo de la secante
        if f_xi - f_xi_menos1 == 0:
            messagebox.showerror("Error", "Division por cero en el metodo de la secante.")
            return None, None, None
        
        #formula_xi_mas1 = f"{xi} - ({f_xi} * ({xi} - {xi_menos1})) / ({f_xi} - {f_xi_menos1})"
        formula_xi_mas1 = f"(({f_xi}) * ({xi_menos1}) - ({f_xi_menos1}) * ({xi})) / (({f_xi}) - ({f_xi_menos1}))"
        xi_mas1 = round(xi - (f_xi * (xi - xi_menos1)) / (f_xi - f_xi_menos1), decimales)
        
        #calculamos el error absoluto
        formula_error = f"|({xi_mas1} - {xi}) / {xi_mas1}| * 100"
        error_absoluto = round(abs((xi_mas1 - xi) / xi_mas1) * 100, decimales)
        
        #guardamos los valores en la lista de iteraciones
        iteraciones.append((paso, xi_menos1, xi, xi_mas1, f_xi_menos1, f_xi, error_absoluto, 
                           f_xi_menos1_calculo, f_xi_calculo, formula_xi_mas1, formula_error))
        
        #hacemos una condicion para verificar si el error es menor o igual al error deseado
        if error_absoluto <= error_absoluto_ingresado:
            break
        
        #y actualizamos los valores para la siguiente iteracion
        xi_menos1 = xi
        xi = xi_mas1
        paso += 1
    
    #evaluamos la funcion con la raiz final
    evaluacion_final_expr = funcion.subs(x, xi_mas1)
    evaluacion_final = round(float(evaluacion_final_expr.evalf()), decimales)
    evaluacion_final_calculo = funcion_str.replace('x', f'({xi_mas1})')
    
    return iteraciones, error_absoluto, evaluacion_final, evaluacion_final_calculo

class PDF(FPDF):
    def header(self):
        #arial en negrita 15
        self.set_font('Arial', 'B', 15)
        #titulo
        self.set_fill_color(66, 133, 244)#encabezado azul
        self.set_text_color(255, 255, 255)#texto blanco
        self.cell(0, 15, 'Método de la Secante', 0, 1, 'C', 1)
        #salto de linea
        self.ln(5)
        
    def footer(self):
        # posicion a 1.5 cm del boton
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # color de texto gris
        self.set_text_color(128)
        # numero de pagina
        self.cell(0, 10, 'Página ' + str(self.page_no()), 0, 0, 'C')

def generar_pdf(iteraciones, error, evaluacion_final, funcion_str, error_absoluto_ingresado, evaluacion_final_calculo):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    #configurar colores para todo el documento
    color_principal = (66, 133, 244)  # azul
    color_secundario = (219, 68, 55)  # rojo
    color_acento = (15, 157, 88)      # verde
    color_neutro = (244, 180, 0)      # amarillo
    
    #apartdo de la informacion de nosotros 
    pdf.set_fill_color(240, 240, 240)#fondo gris claro
    pdf.set_draw_color(*color_principal)#color del borde
    pdf.set_line_width(0.5)
    pdf.rect(10, 25, 190, 30, 'DF')
    
    pdf.set_xy(10, 25)
    pdf.set_font("Arial", style='B', size=12)
    pdf.set_text_color(0, 0, 0)#texto negro
    pdf.cell(190, 10, "Estudiantes", ln=True, align='C')
    pdf.set_font("Arial", style='', size=10)
    pdf.cell(190, 5, "Juan David Sanchez Rubiano", ln=True, align='C')
    pdf.cell(190, 5, "Wilmer Alexander Beltran Trillos", ln=True, align='C')
    
    #apartado de la informacion del problema
    pdf.ln(5)
    pdf.set_fill_color(*color_principal)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(190, 8, "DATOS DEL PROBLEMA", 0, 1, 'C', 1)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_draw_color(*color_principal)
    pdf.set_line_width(0.3)
    
    #informacion de entrada para mostrarla en una tabla bonita
    pdf.ln(2)
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(40, 8, "Funcion:", 1, 0, 'L', 1)
    pdf.set_font("Arial", style='', size=9)
    pdf.cell(150, 8, f"{funcion_str} = 0", 1, 1, 'L')
    
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(40, 8, "Valor inicial Xi-1:", 1, 0, 'L', 1)
    pdf.set_font("Arial", style='', size=9)
    pdf.cell(150, 8, f"{iteraciones[0][1]}", 1, 1, 'L')
    
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(40, 8, "Valor inicial Xi:", 1, 0, 'L', 1)
    pdf.set_font("Arial", style='', size=9)
    pdf.cell(150, 8, f"{iteraciones[0][2]}", 1, 1, 'L')
    
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(40, 8, "Error absoluto deseado:", 1, 0, 'L', 1)
    pdf.set_font("Arial", style='', size=9)
    pdf.cell(150, 8, f"{error_absoluto_ingresado}%", 1, 1, 'L')
    
    #tabla de resultados
    pdf.ln(5)
    pdf.set_fill_color(*color_principal)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(190, 8, "RESULTADOS DE LAS ITERACIONES", 0, 1, 'C', 1)
    pdf.ln(2)
    
    #columnas de la tabla con colores alternados
    pdf.set_font("Arial", style='B', size=8)
    pdf.set_fill_color(*color_principal)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(15, 8, "Iteracion", 1, 0, 'C', 1)
    pdf.cell(25, 8, "Xi-1", 1, 0, 'C', 1)
    pdf.cell(25, 8, "Xi", 1, 0, 'C', 1)
    pdf.cell(25, 8, "Xi+1", 1, 0, 'C', 1)
    pdf.cell(25, 8, "f(Xi-1)", 1, 0, 'C', 1)
    pdf.cell(25, 8, "f(Xi)", 1, 0, 'C', 1)
    pdf.cell(25, 8, "Error (%)", 1, 0, 'C', 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln()
    
    #daatos de la tabla con colores alternados
    for i, (paso, xi_menos1, xi, xi_mas1, f_xi_menos1, f_xi, error, _, _, _, _) in enumerate(iteraciones):
        #esto es para alternar colores de fondo
        if i % 2 == 0:
            pdf.set_fill_color(235, 245, 255)#azul claro
        else:
            pdf.set_fill_color(245, 245, 245)#gris claro
        
        pdf.set_font("Arial", style='', size=8)
        pdf.cell(15, 8, str(paso), 1, 0, 'C', 1)
        pdf.cell(25, 8, str(xi_menos1), 1, 0, 'C', 1)
        pdf.cell(25, 8, str(xi), 1, 0, 'C', 1)
        pdf.cell(25, 8, str(xi_mas1), 1, 0, 'C', 1)
        pdf.cell(25, 8, str(f_xi_menos1), 1, 0, 'C', 1)
        pdf.cell(25, 8, str(f_xi), 1, 0, 'C', 1)
        
        #condicion de que sii el error es menor al deseado, mostrarlo en la tabla como verde
        if error <= error_absoluto_ingresado:
            pdf.set_text_color(*color_acento)
            pdf.set_font("Arial", style='B', size=8)
        pdf.cell(25, 8, str(error), 1, 0, 'C', 1)
        pdf.set_text_color(0, 0, 0)#para restaurar el color
        pdf.ln()
    
    #calculos detallados de cada iteracion
    pdf.ln(5)
    pdf.set_fill_color(*color_principal)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(190, 8, "CÁLCULOS DETALLADOS", 0, 1, 'C', 1)
    pdf.ln(2)
    
    for i, (paso, xi_menos1, xi, xi_mas1, f_xi_menos1, f_xi, error, f_xi_menos1_calculo, f_xi_calculo, formula_xi_mas1, formula_error) in enumerate(iteraciones):
        #encabezado de la iteracion con fondo de color
        pdf.set_fill_color(*color_secundario)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", style='B', size=9)
        pdf.cell(190, 8, f"Iteracion {paso}", 1, 1, 'L', 1)
        
        #datos de la iteracion
        pdf.set_fill_color(245, 245, 245)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", style='B', size=8)
        
        #valores iniciales
        pdf.cell(35, 8, "Valores iniciales:", 1, 0, 'L', 1)
        pdf.set_font("Arial", style='', size=8)
        pdf.cell(155, 8, f"Xi-1 = {xi_menos1}    |    Xi = {xi}", 1, 1, 'L')
        
        #calculos de la funcion
        pdf.set_font("Arial", style='B', size=8)
        pdf.cell(35, 8, "Evaluacion f(Xi-1):", 1, 0, 'L', 1)
        pdf.set_font("Arial", style='', size=8)
        pdf.cell(155, 8, f"{f_xi_menos1_calculo} = {f_xi_menos1}", 1, 1, 'L')
        
        pdf.set_font("Arial", style='B', size=8)
        pdf.cell(35, 8, "Evaluación f(Xi):", 1, 0, 'L', 1)
        pdf.set_font("Arial", style='', size=8)
        pdf.cell(155, 8, f"{f_xi_calculo} = {f_xi}", 1, 1, 'L')
        
        #calculo de xi+1
        pdf.set_font("Arial", style='B', size=8)
        pdf.cell(35, 8, "Cálculo de Xi+1:", 1, 0, 'L', 1)
        pdf.set_font("Arial", style='', size=8)
        pdf.cell(155, 8, f"Xi+1 = {formula_xi_mas1} = {xi_mas1}", 1, 1, 'L')
        
        #calculo del error
        pdf.set_font("Arial", style='B', size=8)
        pdf.cell(35, 8, "Cálculo del error:", 1, 0, 'L', 1)
        pdf.set_font("Arial", style='', size=8)
        pdf.cell(155, 8, f"Error = {formula_error} = {error}%", 1, 1, 'L')
        
        pdf.ln(2)
    
    #resultados finales
    pdf.ln(5)
    pdf.set_fill_color(*color_acento)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(190, 8, "RESULTADOS FINALES", 0, 1, 'C', 1)
    pdf.ln(2)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(60, 8, "Raíz aproximada:", 1, 0, 'L', 1)
    pdf.set_font("Arial", style='', size=9)
    pdf.cell(130, 8, f"{iteraciones[-1][3]}", 1, 1, 'L')
    
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(60, 8, "Error absoluto obtenido:", 1, 0, 'L', 1)
    pdf.set_font("Arial", style='', size=9)
    pdf.cell(130, 8, f"{error}%", 1, 1, 'L')
    
    pdf.set_font("Arial", style='B', size=9)
    pdf.cell(60, 8, "Evaluación de la función f(x):", 1, 0, 'L', 1)
    pdf.set_font("Arial", style='', size=9)
    pdf.cell(130, 8, f"f({iteraciones[-1][3]}) = {evaluacion_final_calculo} = {evaluacion_final}", 1, 1, 'L')

    #guardar el PDF en la carpeta del proyecto
    carpeta_descargas = os.path.join(os.path.expanduser("~"), "C:\Analisis Numerico")
    #aca nos aseguramos de que la carpeta existe
    if not os.path.exists(carpeta_descargas):
        os.makedirs(carpeta_descargas)
    ruta_pdf = os.path.join(carpeta_descargas, "secante_resultado.pdf")
    pdf.output(ruta_pdf)
    
    messagebox.showinfo("PDF Generado", f"El archivo ha sido guardado en:\n{ruta_pdf}")

def calcular():
    try:
        funcion_str = entrada_funcion.get()
        xi_menos1 = float(entrada_xi_menos1.get())
        xi = float(entrada_xi.get())
        error_absoluto_ingresado = float(entrada_tolerancia.get())
        decimales = int(entrada_decimales.get())
        
        iteraciones, error, evaluacion_final, evaluacion_final_calculo = metodo_secante(funcion_str, xi_menos1, xi, error_absoluto_ingresado, decimales)
        if iteraciones is not None:
            generar_pdf(iteraciones, error, evaluacion_final, funcion_str, error_absoluto_ingresado, evaluacion_final_calculo)
    except Exception as e:
        messagebox.showerror("Error", f"Se ha producido un error: {e}")

#interfaz grafica con tkinter
ventana = tk.Tk()
ventana.title("Método de la Secante")

tk.Label(ventana, text="Funcion f(x):").grid(row=0, column=0)
entrada_funcion = tk.Entry(ventana)
entrada_funcion.grid(row=0, column=1)

tk.Label(ventana, text="Valor inicial xi-1:").grid(row=1, column=0)
entrada_xi_menos1 = tk.Entry(ventana)
entrada_xi_menos1.grid(row=1, column=1)

tk.Label(ventana, text="Valor inicial xi:").grid(row=2, column=0)
entrada_xi = tk.Entry(ventana)
entrada_xi.grid(row=2, column=1)

tk.Label(ventana, text="Error absoluto:").grid(row=3, column=0)
entrada_tolerancia = tk.Entry(ventana)
entrada_tolerancia.grid(row=3, column=1)

tk.Label(ventana, text="Numero de decimales:").grid(row=4, column=0)
entrada_decimales = tk.Entry(ventana)
entrada_decimales.grid(row=4, column=1)

tk.Button(ventana, text="Calcular", command=calcular).grid(row=5, columnspan=2)

ventana.mainloop()