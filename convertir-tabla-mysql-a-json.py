# En Linux deberás de instalar tkinter usando: sudo apt-get install -y python-tk
import subprocess
import importlib
import sys

def install_mysql_connector():
    try:
        importlib.import_module('mysql.connector')
        print("La librería mysql-connector ya está instalada.")
    except ImportError:
        print("La librería mysql-connector no está instalada. Instalando...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'mysql-connector'])
        print("La librería mysql-connector ha sido instalada.")

install_mysql_connector()
import os
import tkinter as tk
from tkinter import messagebox, filedialog, IntVar
import mysql.connector
import json

# Función para obtener los nombres de las columnas desde la base de datos
def fetch_column_names(cursor):
    return [column[0] for column in cursor.description]

# Función para obtener los datos desde la base de datos
def fetch_data(cursor, batch_size=1000):
    while True:
        records = cursor.fetchmany(batch_size)
        if not records:
            break
        yield records

# Función para extraer y guardar los datos de la base de datos como archivo JSON
def fetch_mysql_data(host, user, password, database, table, output_file, replace_null, batch_size=1000):
    total_records = 0
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        
        column_names = fetch_column_names(cursor)
        
        with open(output_file, "w", encoding='utf-8') as f:  # Utilizar 'w' en lugar de 'a'
            f.write("[\n")
            first_record = True
            
            for records in fetch_data(cursor, batch_size):
                for record in records:
                    if replace_null:
                        record = [col if col is not None else "" for col in record]
                    data = dict(zip(column_names, record))
                    if not first_record:
                        f.write(",\n")
                    else:
                        first_record = False
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    total_records += 1
                    
            f.write("\n]")

        messagebox.showinfo("Éxito", f"Se han exportado un total de {total_records} registros al archivo JSON.")
        
    except mysql.connector.Error as error:
        messagebox.showerror("Error", str(error))
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Interfaz gráfica utilizando tkinter
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Exportar datos a JSON")
        self.geometry('350x250')
        self.configure(bg='#f0f0f0')  # Fondo claro
        self.resizable(False, False)  # Ventana no redimensionable

        # Obtiene la ruta absoluta del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Intenta cargar el icono si está disponible
        try:
            icon_path = os.path.join(script_dir, 'Proyecto-nuevo.ico')
            self.iconbitmap(icon_path)
        except Exception as e:
            print("Error al cargar el icono:", e)

        # Etiquetas y cuadros de texto para capturar entrada de usuario
        self.label_host = tk.Label(self, text="Host:", bg='#f0f0f0', fg='black')
        self.entry_host = tk.Entry(self)
        self.label_user = tk.Label(self, text="Usuario BD:", bg='#f0f0f0', fg='black')
        self.entry_user = tk.Entry(self)
        self.label_password = tk.Label(self, text="Contraseña BD:", bg='#f0f0f0', fg='black')
        self.entry_password = tk.Entry(self, show="*")
        self.label_database = tk.Label(self, text="Nombre BD:", bg='#f0f0f0', fg='black')
        self.entry_database = tk.Entry(self)
        self.label_table = tk.Label(self, text="Nombre de la tabla:", bg='#f0f0f0', fg='black')
        self.entry_table = tk.Entry(self)

        # Checkbutton para reemplazar null por comillas
        self.replace_null_var = IntVar()
        self.replace_null_checkbox = tk.Checkbutton(self, text="Reemplazar null por \"\"", variable=self.replace_null_var, bg='#f0f0f0')

        # Botón para ejecutar la función fetch_mysql_data
        self.button_run = tk.Button(self, text="Convertir tabla a JSON", command=self.run, bg='#363636', fg='white')

        # Configuración de posición de widgets
        self.label_host.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_host.grid(row=0, column=1, padx=5, pady=5)
        self.label_user.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entry_user.grid(row=1, column=1, padx=5, pady=5)
        self.label_password.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.entry_password.grid(row=2, column=1, padx=5, pady=5)
        self.label_database.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.entry_database.grid(row=3, column=1, padx=5, pady=5)
        self.label_table.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.entry_table.grid(row=4, column=1, padx=5, pady=5)
        self.replace_null_checkbox.grid(row=5, columnspan=2, padx=5, pady=5, sticky='w')
        self.button_run.grid(row=6, column=0, columnspan=2, pady=(10, 0), padx=5, sticky='ew')


    def run(self):
        host = self.entry_host.get()
        user = self.entry_user.get()
        password = self.entry_password.get()
        database = self.entry_database.get()
        table = self.entry_table.get()
        replace_null = bool(self.replace_null_var.get())

        # Verificar que todos los campos excepto el de contraseña estén llenos
        if not all((host, user, database, table)):
            messagebox.showerror("Error", "Todos los campos excepto el de contraseña son obligatorios.")
            return

        # Abrir el diálogo para seleccionar la ubicación y el nombre del archivo
        output_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Archivos JSON", "*.json")])

        if output_file:
            fetch_mysql_data(host, user, password, database, table, output_file, replace_null)

if __name__ == "__main__":
    app = App()
    app.mainloop()
