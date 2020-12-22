# Librerías importadas por David
from interfaz import *
from PyQt5.QtWidgets import QFileDialog, QComboBox
from PyQt5 import QtGui
import os

# Librerías importadas por Joan Requena
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import math

class MainWindow( QtWidgets.QMainWindow, Ui_MainWindow ):

    datos = None
    carpeta_destino = None
    calidad = 108
    boolean_carpeta = False
    boolean_datos = False

    def __init__( self, *args, **kwargs ):

        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Conecta los botones de la interfaz gráfica con las funciones a las que llamará
        self.pushButton_abrir.clicked.connect(self.funcion_Abrir)
        self.pushButton_cambiar.clicked.connect(self.funcion_Modificar)
        self.pushButton_generar_grafica.clicked.connect(self.funcion_Generar_Grafica)

        self.pushButton_generar_grafica.setStyleSheet("background-color: gray")
        self.pushButton_generar_grafica.setEnabled(False)

    # Modifica la ruta de entrada del fichero y lo carga en una variable
    def funcion_Abrir( self ):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.datos, _ = QFileDialog.getOpenFileName( self, "Abrir ensayo", "", "Documentos de texto (*.txt)", options = options)
        
        if self.datos:

            self.textBrowser_ruta_entrada.setText( self.datos )
            self.datos = pd.read_csv( self.datos, sep = "\t" )
            self.boolean_datos = True

            if self.boolean_carpeta is True:
                self.pushButton_generar_grafica.setStyleSheet("background-color: rgb(0, 16, 103); color: rgb(255, 255, 255);")
                self.pushButton_generar_grafica.setEnabled(True)

            return self.datos

        else:

            print( "self.datos vacío: " + self.datos )

    # Modifica la ruta de destino, se puede añadir una ruta por defecto en caso de no modificarse
    def funcion_Modificar( self ):

        self.carpeta_destino = str( QFileDialog.getExistingDirectory( self, "Guardar en" ) )
        
        if self.carpeta_destino:

            self.textBrowser_ruta_salida.setText( str( self.carpeta_destino ) )
            self.boolean_carpeta = True

            if self.boolean_datos is True:

                self.pushButton_generar_grafica.setStyleSheet("background-color: rgb(0, 16, 103); color: rgb(255, 255, 255);")
                self.pushButton_generar_grafica.setEnabled(True)

            return self.carpeta_destino

        else: 
            
            print("self.carpeta_destino vacía: " + self.carpeta_destino)
    
    # Genera el informe y lo guarda en la ruta de destino
    def funcion_Generar_Grafica( self ):
        
        def Mensaje( self, Color, Mensaje ):

            if Color == 'red':
                self.label_mensajes.setStyleSheet('color: red')
            elif Color == 'green':
                self.label_mensajes.setStyleSheet('color: green')
            elif Color == 'blue':
                self.label_mensajes.setStyleSheet('color: blue')
            else:
                self.label_mensajes.setStyleSheet('color: black')
            
            self.label_mensajes.setText( Mensaje )            

        # Lee la selección del menú desplegable
        Mensaje( self, "", "")
        Seleccion = self.comboBox_desplegable_graficas.currentIndex()
       
        # Genera la gráfica de Conexión/Desconexión de los ventiladores
        def Conexion_Desconexion_Ventiladores( self ):

            # Asigna las variables del documento .txt a las variables python
            Ventilador1 = self.datos['VENTILADOR1']
            Ventilador2 = self.datos['VENTILADOR2']
            Fases = self.datos['Pattern Phase']
            Potencia = self.datos['KW+']
            TEMP_MKE = self.datos['TEMP_MKE']

            Vent1_puntos = np.zeros( [len( Ventilador1 ), 2] )                                             # Matriz de los puntos donde se enchufa y se apaga el ventilador
            Vent2_puntos = np.zeros( [len( Ventilador2 ), 2] )                                             # Matriz de los puntos donde se enchufa y se apaga el ventilador

            i1 = 0
            i2 = 0

            for z in range( 1, len(Ventilador1 ), 1 ):

                if ( Ventilador1[z] != Ventilador1[ z - 1 ] 
                and ( Fases[z] == 'F0- TABLA CONEX VENTIADORES' 
                or Fases[z] == 'F0- TABLA DESCONEX VENTIADORES' ) ):
                    Vent1_puntos[ i1, 0 ] = TEMP_MKE[z]
                    Vent1_puntos[ i1, 1 ] = z        
                    i1 = i1 + 1

                if ( Ventilador2[z] != Ventilador2[ z - 1 ] 
                and ( Fases[z] == 'F0- TABLA CONEX VENTIADORES' 
                or Fases[z] == 'F0- TABLA DESCONEX VENTIADORES' ) ):
                    Vent2_puntos[ i2, 0 ] = TEMP_MKE[z]
                    Vent2_puntos[ i2, 1 ] = z        
                    i2 = i2 + 1

            y1 = np.zeros( i1 )
            y2 = np.zeros( i2 )

            Ventilador_graf = plt.figure( figsize = ( 15, 10 ) )                                           # Asigna el tamaño de la ventana de la gráfica

            ax0 = plt.subplot( 3, 1, 1 )

            P = ax0.plot( np.linspace( 0, len( Potencia ), 
                        len( Potencia ), endpoint = True ), 
                        Potencia, 'tab:cyan', label = 'Potencia real' )

            plt.xlabel( 'Número de muestreo' )
            plt.ylabel( 'Potencia kW' )
            plt.legend( loc = 'best' )
            plt.grid( True )

            ax1 = ax0.twinx( )

            T = ax1.plot( np.linspace( 0, len( Potencia ), 
                        len( Potencia ), endpoint = True ), 
                        TEMP_MKE, 'crimson', label = 'Temperatura' )

            plt.ylabel( 'Temperatura °C' )
            lns = T + P
            labs = [ l.get_label() for l in lns ]


            plt.subplot( 3, 1, 2 )

            plt.plot( np.linspace( 0, len( Ventilador1 ), 
                    len( Ventilador1 ), endpoint = True ),
                    Ventilador1, 'orange', label = 'Ventilador 1' )

            plt.plot( Vent1_puntos[ 0 : i1, 1 ], y1 + 1, 'go', 
                    label = 'Conexión/Desconexión' )

            plt.ylabel( 'Estado del ventilador 1' )
            plt.xlabel( 'Número de muestreo' )
            plt.legend( loc = 'best' )
            plt.grid( True )


            plt.subplot( 3, 1, 3 )

            plt.plot( np.linspace( 0, len( Ventilador2 ), 
                    len( Ventilador2 ), endpoint = True ), 
                    Ventilador2, label = 'Ventilador 2' )

            plt.plot( Vent2_puntos[ 0 : i2, 1 ], y2 + 1, 'ro', 
                      label='Conexión/Desconexión' )
                    
            plt.ylabel( 'Estado del ventilador 2' )
            plt.xlabel( 'Número de muestreo' )
            plt.legend( loc = 'best' )
            plt.grid( True )

            columnas = ( 'Temperatura de conexión (°C)', 'Temperatura de desconexión (°C)' )
            filas = ( 'Ventilador 1', 'Ventilador 2' )
            
            cellText = [ [ Vent1_puntos[0,0], Vent1_puntos[1,0]], [Vent2_puntos[0,0], Vent2_puntos[1,0] ] ]
            tabla = plt.table( cellText = cellText, rowLoc = 'right',
                            rowLabels = filas,
                            colWidths = [ .5, .5 ], colLabels = columnas,
                            colLoc ='center', loc = 'bottom', bbox = [ 0, -0.8, 1, 0.5 ], zorder = 20 )

            tabla.auto_set_font_size( True )
            tabla.scale( 1, 1 )
            plt.grid( True )
            ax0.set_title( 'Conexión/Desconexión de ventiladores', fontsize = 16 )

            plt.tight_layout()
            ruta = self.carpeta_destino + '/' + 'Ventilador_graf.png'
            plt.savefig( ruta, dpi = self.calidad )
            plt.close( Ventilador_graf )

            Mensaje(self, "green", "Gráfica de Conexión/Desconexión de ventiladores generada con éxito.")
 
        # Genera la gráfica de Conexión/Desconexión del Kidk-Down
        def Conexion_Desconexion_KickDown( self ):
            
            # Asigna las variables del documento .txt a las variables python
            KICK_DOWN1 = self.datos['KICK-DOWN1']
            KICK_DOWN2 = self.datos['KICK-DOWN2']
            Fases = self.datos['Pattern Phase']
            Potencia = self.datos['Potencia']
            Par = self.datos['Par']

            Kick_down1_puntos = np.zeros( [ len( KICK_DOWN1 ), 2 ] )                                         # Matriz de los puntos donde se enchufa y se apaga el kick-down1
            Kick_down2_puntos = np.zeros( [ len( KICK_DOWN2 ), 2 ] )                                         # Matriz de los puntos donde se enchufa y se apaga el kick-down2

            i3 = 0
            i4 = 0

            for z in range( 1, len( KICK_DOWN1 ), 1 ):

                if ( KICK_DOWN1[z] != KICK_DOWN1[ z - 1 ] 
                and ( Fases[z] == 'F1_APROXIMACION KD1' 
                or Fases[z] == 'F1_TABLA CONEX KICKDOWN 1' ) ):
                    Kick_down1_puntos[ i3, 0 ] = Par[z]
                    Kick_down1_puntos[ i3, 1 ] = z        
                    i3 = i3 + 1

                if ( KICK_DOWN2[z] != KICK_DOWN2[ z - 1 ] 
                and ( Fases[z] == 'F2_APROXIMACION KD2' 
                or Fases[z] == 'F2_TABLA CONEX KICKDOWN 2' ) ):
                    Kick_down2_puntos[ i4, 0 ] = Par[z]
                    Kick_down2_puntos[ i4, 1 ] = z        
                    i4 = i4 + 1

            y3 = np.zeros( i3 )
            y4 = np.zeros( i4 )

            Kic_down_graf= plt.figure( figsize = ( 15, 10 ) )  

            plt.subplot( 3, 1, 1 )

            plt.plot( np.linspace( 0, len( Potencia ), 
                      len( Potencia ), endpoint = True ), 
                      Par, 'tab:cyan', label= 'Par motor' )
            
            plt.ylabel( 'Par Nm' )
            plt.xlabel( 'Número de muestreo' )
            plt.legend( loc = 'best' )
            plt.grid( True )

            Kic_down_graf.suptitle( 'Conexión Kick-Down', fontsize = 16 )

            plt.subplot( 3, 1, 2 )

            plt.plot( np.linspace( 0, len( KICK_DOWN1 ), 
                      len( KICK_DOWN1 ), endpoint = True ), 
                      KICK_DOWN1, 'orange', label = 'KICK_DOWN1 1' )

            plt.plot( Kick_down1_puntos[ 0 : i3, 1 ], y3 + 1, 'go',
                      label = 'Conexión/Desconexión' )
            
            plt.ylabel( 'Estado del Kick-Down 1' )
            plt.xlabel( 'Número de muestreo' )
            plt.legend( loc = 'best' )
            plt.grid( True )

            plt.subplot( 3, 1, 3 )

            plt.plot( np.linspace( 0, len( KICK_DOWN2 ), 
                      len( KICK_DOWN2 ), endpoint = True ), 
                      KICK_DOWN2, 'b', label = 'KICK_DOWN2' )

            plt.plot( Kick_down2_puntos[ 0 : i4, 1 ], y4 + 1, 'go', 
                      label='Conexión/Desconexión' )
            
            plt.ylabel( 'Estado kick-down 2' )
            plt.xlabel( 'Número de muestreo' )
            plt.legend( loc = 'best' )
            plt.grid( True )

            columnas=( 'Par (Nm)', 'Potencia real (kW)' )
            filas=( 'Kick-Down 1', 'Kick-Down 2' )
            
            cellText = [ [ int( Kick_down1_puntos[ 0, 0 ] ), int( Potencia[ Kick_down1_puntos[ 0, 1 ] ] )], [ int( Kick_down2_puntos[ 0, 0 ] ), int( Potencia[ Kick_down2_puntos[ 0, 1 ] ] ) ] ]
            tabla = plt.table( cellText = cellText, rowLoc = 'right',
                            rowLabels = filas,
                            colWidths = [ .5, .5 ], colLabels = columnas,
                            colLoc = 'center', loc = 'bottom', zorder = 20 )

            tabla.auto_set_font_size( True )
            tabla.scale( 1, 1 )
            plt.grid( True )
            #ax0.set_title( 'Conexión/Desconexión de ventiladores', fontsize = 16 )

            #plt.tight_layout()
            ruta = self.carpeta_destino + '/' + 'Kick_down_graf.png'
            plt.savefig( ruta, dpi = self.calidad )
            plt.close( Kic_down_graf )

            Mensaje(self, "green", "Gráfica de Conexión/Desconexión del Kick-Down generada con éxito.")

        # Genera la gráfica de Pérdida de potencia en función de la temperatura
        def Perdida_Potencia_Temperatura( self ):
            
            KICK_DOWN2 = self.datos['KICK-DOWN2']
            Potencia = self.datos['Potencia']
            Fases = self.datos['Pattern Phase']
            TEMP_MKE = self.datos['TEMP_MKE']

            Potencia_puntos = np.zeros( [ len( KICK_DOWN2 ), 3 ] )                                          # Matriz de los puntos donde baja la potencia en funcion de la temperatura

            i5 = 0  

            for z in range( 0, len( Potencia ), 1 ):
                if Fases[z] == 'F3_TABLA_PERD. POT':
                    Potencia_puntos[ i5, 0 ] = Potencia[z]
                    Potencia_puntos[ i5, 1 ] = z
                    Potencia_puntos[ i5, 2 ] = i5         
                    i5 = i5 + 1
                    
            "Busca el punto máximo y mínimo, y obtiene sus posiciones"
            Max_perdida = np.zeros( [ 1, 3 ] )
            Min_perdida = np.zeros( [ 1, 3 ] )
                    
            Max_perdida[ 0, 0 ] = np.amax( Potencia_puntos[ : i5, 0] )
            Max_perdida[ 0, 1 ] = Potencia_puntos[ np.argmax( Potencia_puntos[ : i5, 0 ] ), 2 ]   
            Max_perdida[ 0, 2 ] = Potencia_puntos[ np.argmax( Potencia_puntos[ : i5, 0 ] ), 1 ]    

            Min_perdida[ 0, 0 ] = np.amin( Potencia_puntos[ :i5, 0] )  
            Min_perdida[ 0, 1 ] = Potencia_puntos[ np.argmin( Potencia_puntos[ : i5, 0] ), 2 ]  
            Min_perdida[ 0, 2 ] = Potencia_puntos[ np.argmin( Potencia_puntos[ : i5, 0] ), 1 ]

            Temp_max_perdida = TEMP_MKE[ Max_perdida[ 0, 2 ] ]
            Temp_min_perdida = TEMP_MKE[ Min_perdida[ 0, 2 ] ]  

            #%%
            'Perdida potencia-temperatura'
            Perdida_potencia ,ax1= plt.subplots(figsize=(15,10))
            P=ax1.plot(Potencia_puntos[:i5,2], Potencia_puntos[:i5,0],'orange', label='Potencia real')
            plt.ylabel('Potencia(kW)')
            plt.xlabel('Número de muestra')
            plt.plot(Max_perdida[0,1],Max_perdida[0,0],'go',label='Máximo')
            plt.plot(Min_perdida[0,1],Min_perdida[0,0],'ro',label='Mínimo')

            ax2 = ax1.twinx()

            T=ax2.plot(Potencia_puntos[:i5,2], TEMP_MKE[Potencia_puntos[:i5,1]],'b', label='Temperatura MKE')
            plt.ylabel('Temperatura ºC')
            lns = T+P
            labs = [l.get_label() for l in lns]
            Perdida_potencia.suptitle('Rampa pérdida de potenica', fontsize=16)
            Perdida_potencia.legend(lns, labs,loc='right', bbox_to_anchor=(0.25,0.5))
            ax1.yaxis.grid() # horizontal lines
            ax1.xaxis.grid() # vertical lines 
            columnas=('Potencia kW','Temperatura MKE ºC')
            filas=('Máximo valor','VenMínimo valor')
            n_filas=2
            y_offset = np.zeros(len(columnas))
            cellText = [[round(Max_perdida[0,0],2),round(Temp_max_perdida,1)],[round(Min_perdida[0,0],2),round(Temp_min_perdida,1)]]
            tabla = plt.table(cellText=cellText, rowLoc='right',
                            rowLabels=filas,
                            colWidths=[.5,.5], colLabels=columnas,
                            colLoc='center', loc='bottom',zorder=20)

            tabla.auto_set_font_size(True)
            tabla.scale(1,1)
            Perdida_potencia.suptitle('Pérdida de potencia', fontsize=16)
            
            ruta = self.carpeta_destino + '/' + 'Perdida_Potencia.png'
            plt.savefig( ruta, dpi = self.calidad )
            plt.close(Perdida_potencia)
        
            Mensaje(self, "green", "Gráfica de Pérdida de potencia por temperatura generada con éxito.")

        # Genera la gráfica de Desconexión a 1200 rpm
        def Desconexion_1200rpm( self ):

            KICK_DOWN1 = self.datos['KICK-DOWN1']
            Revoluciones = self.datos['Revoluciones']
            Ventilador1 = self.datos['VENTILADOR1']
            Ventilador2 = self.datos['VENTILADOR2']
            Potencia = self.datos['Potencia']
            Fases = self.datos['Pattern Phase']

            Desconexion_1200=np.zeros(len(Fases))
            i6=0  
            for z in range(0, len(Potencia),1):
                if Fases[z]=='F7_TABLA_DESC. VENTILA 1200':
                    Desconexion_1200[i6]=z        
                    i6=i6+1

            Des_1200_graf, ax = plt.subplots(figsize=(15,10))
            plt.subplot(311)
            plt.plot(Revoluciones[Desconexion_1200[0:i6]],'tab:cyan', label='RPM motor')
            plt.legend(loc='best')
            plt.ylabel('Revoluciones/minuto')
            plt.xlabel('Número de muestreo')
            plt.grid(True)

            plt.subplot(312)
            plt.plot(Ventilador1[Desconexion_1200[0:i6]],'r', label='Ventilador 1')
            plt.plot(Ventilador2[Desconexion_1200[0:i6]],'b--', label='Ventilador 2')

            plt.grid(True)
            plt.legend(loc='best')
            plt.ylabel('Estado Ventiladores')
            plt.xlabel('Número de muestreo')

            plt.subplot(313)
            plt.plot(KICK_DOWN1[Desconexion_1200[0:i6]],'r', label='KICK_DOWN1')
            plt.plot(KICK_DOWN1[Desconexion_1200[0:i6]],'b--', label='KICK_DOWN2')
            plt.legend(loc='best')
            plt.ylabel('Estado kick-down')
            plt.xlabel('Número de muestreo')

            plt.grid(True)
            Des_1200_graf.suptitle('Desconexión 1200 rpm', fontsize=16)

            plt.grid(True)

            ruta = self.carpeta_destino + '/' + 'Des_1200_graf.png'
            plt.savefig( ruta, dpi = self.calidad )
            plt.close(Des_1200_graf)

            Mensaje( self, "green", "Gráfica de Desconexión a 1200rpm generada con éxito." )
            
        # Genera la gráfica de Desconexión a 1400 rpm
        def Desconexion_1400rpm( self ):
            
            Revoluciones = self.datos['Revoluciones']
            Ventilador1 = self.datos['VENTILADOR1']
            Ventilador2 = self.datos['VENTILADOR2']
            KICK_DOWN1 = self.datos['KICK-DOWN1']
            Fases = self.datos['Pattern Phase']
            Potencia= self.datos['Potencia']

            Desconexion_1400=np.zeros(len(Fases))

            i7=0  
            for z in range(0, len(Potencia),1):
                if Fases[z]=='F9_TABLA_DESC. VENTILA 1400':
                    Desconexion_1400[i7]=z        
                    i7=i7+1

            Des_1400_graf=plt.figure(figsize=(15,10))
            ax0=plt.subplot(311)
            ax0.plot(Revoluciones[Desconexion_1400[0:i7]],'tab:cyan', label='RPM motor')
            ax0.legend(loc='best')
            ax0.set_ylabel('Revoluciones/minuto')
            ax0.set_xlabel('Número de muestreo')
            plt.grid(True)

            ax1=plt.subplot(312)
            ax1.plot(Ventilador1[Desconexion_1400[0:i7]],'r', label='Ventilador 1')
            ax1.plot(Ventilador2[Desconexion_1400[0:i7]],'b--', label='Ventilador 2')
            ax1.set_ylim([0,1.05])

            plt.grid(True)
            ax1.legend(loc='lower right')
            ax1.set_ylabel('Estado ventiladores')

            ax1.set_xlabel('Número de muestreo')

            ax2=plt.subplot(313)
            ax2.plot(KICK_DOWN1[Desconexion_1400[0:i7]],'r', label='KICK_DOWN1')
            ax2.plot(KICK_DOWN1[Desconexion_1400[0:i7]],'b--', label='KICK_DOWN2')
            ax2.legend(loc='best')
            ax2.set_ylabel('Estado kick-down')
            ax2.set_xlabel('Número de muestreo')


            plt.grid(True)
            Des_1400_graf.suptitle('Desconexión 1400 rpm', fontsize=16)

            plt.grid(True)
            ruta = self.carpeta_destino + '/' + 'Des_1400_graf.png'
            plt.savefig( ruta, dpi = self.calidad )
            plt.close(Des_1400_graf)

            Mensaje(self, "green", "Gráfica de Desconexión a 1400rpm generada con éxito." )
        
        # Genera la gráfica de la prueba del regulador
        def Prueba_Regulador( self ):

            Fases = self.datos['Pattern Phase']
            Potencia= self.datos['Potencia']
            Revoluciones = self.datos['Revoluciones']
            Par = self.datos['Par']

            Regulador = np.zeros( len( Fases ) )

            i8 = 0

            for z in range( 0, len( Potencia ), 1 ):
                if Fases[z] == 'F5_PRB REGULADOR':
                    Regulador[i8] = z        
                    i8 = i8 + 1

            def make_patch_spines_invisible(ax):
                ax.set_frame_on(True)
                ax.patch.set_visible(False)
                for sp in ax.spines.values():
                    sp.set_visible(False)


            fig, host = plt.subplots()
            fig.subplots_adjust(right=0.75)

            par1 = host.twinx()
            par2 = host.twinx()

            # Offset the right spine of par2.  The ticks and label have already been
            # placed on the right by twinx above.
            par2.spines["right"].set_position(("axes", 1.2))
            # Having been created by twinx, par2 has its frame off, so the line of its
            # detached spine is invisible.  First, activate the frame but make the patch
            # and spines invisible.
            make_patch_spines_invisible(par2)
            # Second, show the right spine.
            par2.spines["right"].set_visible(True)

            p1, = host.plot(np.linspace(0, i8*5, i8),Potencia[Regulador[0:i8]],'r--', label='Potencia real')
            p2, = par1.plot(np.linspace(0, i8*5, i8),Par[Regulador[0:i8]],'b--', label='Par')
            p3, = par2.plot(np.linspace(0, i8*5, i8),Revoluciones[Regulador[0:i8]],'g', label='Revoluciones')

            host.set_xlabel("Tiempo (s)")
            host.set_ylabel("Potencia (kW)")
            par1.set_ylabel("Par (Nm)")
            par2.set_ylabel("Revoluciones (rpm)")

            tkw = dict(size=4, width=1.5)
            host.tick_params(axis='y', colors=p1.get_color(), **tkw)
            par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
            par2.tick_params(axis='y', colors=p3.get_color(), **tkw)

            lines = [p1, p2, p3]

            host.legend(lines, [l.get_label() for l in lines],loc='center right')
            ruta = self.carpeta_destino + '/' + 'Regulador_2680.png'
            plt.savefig( ruta, dpi = self.calidad )
            
            Mensaje(self, "green", "Gráfica del regulador generado con éxito.")

        # Genera el informe completo
        def Completo( self ):

            Conexion_Desconexion_Ventiladores( self )
            Conexion_Desconexion_KickDown( self )
            Perdida_Potencia_Temperatura( self )
            Desconexion_1200rpm( self )
            Desconexion_1400rpm( self )
            Prueba_Regulador( self )
            
            Mensaje( self, "green", "Informe completo generado con éxito." )

        # Si se añade algun tipo de gráfica más, se debe añadir un elif en este bloque con el nombre
        # de la nueva función que realiza la gráfica y asignarle un número al desplegable continuando el orden.
        # Este bloque llama a la función que genera el informe de salida dependiendo de la selección del usuario en el menu desplegable
        if Seleccion == 0:
            Conexion_Desconexion_Ventiladores(self)
        elif Seleccion == 1:
            Conexion_Desconexion_KickDown(self)
        elif Seleccion == 2:
            Perdida_Potencia_Temperatura(self)
        elif Seleccion == 3:
            Desconexion_1200rpm(self)
        elif Seleccion == 4:
            Desconexion_1400rpm(self)
        elif Seleccion == 5:
            Prueba_Regulador(self)
        else:
            Completo(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()