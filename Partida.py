from Jugador import Jugador
import numpy as np
import random

class Partida:
    probabilidad_salir_en_ronda = 0.2
    distancia_maxima_relacionados = 15     # Calculado a base de prueba-error
    fichas_por_jugador = 50
    
    def __init__(self, n_jugadores, baraja, nombre_jugador, nombres_jugadores):
        # Creo una variable para almacenar el input de un jugador
        self.decision = ''
        
        # Cargo una configuracion de partida
        self.baraja = np.array(baraja)
        
        # Creo una lista de jugadores
        self.jugadores = [Jugador(nombre = nombres_jugadores[i],fichas = self.fichas_por_jugador) for i in range(n_jugadores)]
        
        # Creo al jugadorampliasen
        self.jugador = Jugador(nombre = nombre_jugador, fichas = self.fichas_por_jugador)
        
    '''
    Calcula la puntuacion a tener en cuenta en caso de un empate
    Se usan las distancias entre embeddings para calcular la puntuacion
    '''    
    def puntuacion_desempate(self, cartas, mesa):
        mano = np.vstack((cartas, mesa))
        puntuacion = 0
        for i in range(len(mano)):
            for j in range(len(mano)):
                puntuacion = puntuacion + Partida.distancia(mano[i], mano[j])
                
        return puntuacion
                
    '''
    Devuelve la distancia entre dos cartas(embeddings) 
    '''
    def distancia(carta1, carta2):
        return np.sum(abs(carta1[1:] - carta2[1:]))
    
    '''
    Devuelve verdadero si las dos cartas estan relacionadas
    Para esto se tiene en cuenta la distancia entre estas
    '''
    def estan_relacionadas(self, carta1, carta2):
        return self.distancia_maxima_relacionados >= Partida.distancia(carta1, carta2)
        
    '''
    Calcula la puntuacion de un set de cartas
    '''
    def calcular_puntuacion(self, cartas, mesa):
        mano = np.vstack((cartas, mesa))
        
        # relaciones [4, 3, 2] numero de cartas relacionadas entre si
        relaciones = [0, 0, 0]
        
        for i in range(len(mano)):
            n_relacionados = 0
            for j in range(i+1, len(mano)):
                if self.estan_relacionadas(mano[i, 1:], mano[j, 1:]):
                    n_relacionados = n_relacionados + 1
            if n_relacionados >= 4:
                relaciones[0] = relaciones[0] + 1
            elif n_relacionados == 3:
                relaciones[1] = relaciones[1] + 1
            elif n_relacionados == 2:
                relaciones[2] = relaciones[2] + 1
                
        if relaciones[0] != 0:
            return 5     # Poker
        if relaciones[1] != 0 and relaciones[2] != 0:
            return 4     # Full
        if relaciones[1] != 0:
            return 3     # Trio
        if relaciones[2] >= 2:
            return 2     # Doble pareja
        if relaciones[2] == 1:
            return 1     # Una pareja
        
        return 0         # carta alta
        
    '''
    Devuelve una lista con 3 cartas aleatorias
    v1.0. 
    '''
    def escoger_cartas(self, n_cartas = 2):
        return self.baraja[np.random.randint(0, len(self.baraja), n_cartas)]
        
    '''
    Se calcula si un jugador entra o no a una ronda
    v1.0. Hay una probabilidad fija de que un jugador decida no entra a esta ronda
    '''
    def entra_en_ronda(self, jugador):
        if(jugador.fichas == 0):
            return False
        
        return (np.random.uniform(0, 1) > self.probabilidad_salir_en_ronda)
    
    '''
    Se calcula la apuesta que un jugador realizara
    v1.0. Se escoje una apuesta aleatoria menor que el numero de fichas del jugador
    '''
    def calcula_apuesta(self, jugador):
        return np.random.randint(0, jugador.fichas + 1)
        
        
    '''
    Simula el flujo de un partida de Poker
    '''
    def jugar_ronda(self):
        self.decision = ''
        esta_jugando = True
        fichas_apostadas = 0
        self.cartas_mesa = None
        jugadores_ronda = []
        
        # Fase 1 - Se reparten 2 cartas a cada jugador
        self.jugador.cartas = self.escoger_cartas(2)
        for jugador in self.jugadores:
            jugador.cartas = self.escoger_cartas(2)
            jugadores_ronda.append(jugador)
        yield "entrar"
        
        # Fase 2 - Jugadores deciden si entrar en partida o no
        if(self.decision == 'n'):
            esta_jugando = False
            return                      
        jugadores_ronda = [jugador for jugador in jugadores_ronda if self.entra_en_ronda(jugador)]
        # Si no hay jugadores salgo de la ronda
        if(len(jugadores_ronda) == 0 or (len(jugadores_ronda) == 1 and not esta_jugando)):
            return
        
        # Fase 3 - Fase de apuestas
        cartas_a_ensenar = [3,1,1]     # El numero de cartas que se enseñaran en cada ronda de apuestas
        for n_cartas in cartas_a_ensenar:
            if(self.cartas_mesa is None):
                self.cartas_mesa = self.escoger_cartas(n_cartas)
            else:
                self.cartas_mesa = np.vstack((self.cartas_mesa, self.escoger_cartas(n_cartas)))
            
            random.shuffle(jugadores_ronda)
            apuesta_maxima = self.calcula_apuesta(jugadores_ronda[0])

            # Calculo la accion de cada jugador
            jugadores_a_retirar = []
            for i in range(1,len(jugadores_ronda)):
                jugador = jugadores_ronda[i]
                if self.calcula_apuesta(jugador) < apuesta_maxima:
                    jugadores_a_retirar.append(jugador)
                    
            # Retiro a los jugadores que no han seguido apostando
            for jugador in jugadores_a_retirar:
                jugadores_ronda.remove(jugador)
                
            # Quito las fichas apostadas a los jugadores restantes y actualizo la apuesta total
            fichas_apostadas = fichas_apostadas + apuesta_maxima * len(jugadores_ronda)
            for jugador in jugadores_ronda:
                jugador.fichas = jugador.fichas - apuesta_maxima
            
            if(esta_jugando):
                yield f"apostar {apuesta_maxima}"              # Espero a que el usuario tome una decision
                
                if(self.decision == 'n' or self.jugador.fichas < apuesta_maxima):
                    esta_jugando = False
                else:
                    self.jugador.fichas = self.jugador.fichas - apuesta_maxima
                    fichas_apostadas = fichas_apostadas + apuesta_maxima
                
            # Si no querdan jugadores termino la fase de apuestas
            if(len(jugadores_ronda) == 0 or (len(jugadores_ronda) == 1 and not esta_jugando)):
                break  
        
        # Fin de ronda - Se calcula al ganador
        puntuaciones = []
        for jugador in jugadores_ronda:
            puntuaciones.append(self.calcular_puntuacion(jugador.cartas, self.cartas_mesa))
        maxima_puntuacion = max(puntuaciones)
        
        if(esta_jugando and self.calcular_puntuacion(self.jugador.cartas, self.cartas_mesa) > maxima_puntuacion):
            self.jugador.fichas = self.jugador.fichas + fichas_apostadas
            return
        
        ganadores = [i for i,j in enumerate(puntuaciones) if j == maxima_puntuacion]
        if(len(ganadores) == 1):     # Si solo hay un ganador se le dan las fichas
            ganador = 0
        else:                        # Si hay empate se desempata
            max_pos = 0
            min_punt = self.puntuacion_desempate(jugadores_ronda[0].cartas, self.cartas_mesa)
            for i in range(1, len(ganadores)):
                punt = self.puntuacion_desempate(jugadores_ronda[0].cartas, self.cartas_mesa)
                if punt < min_punt:
                    min_punt = punt
                    max_pos = i
            ganador = max_pos
            
            if esta_jugando and self.puntuacion_desempate(self.jugador.cartas, self.cartas_mesa) < min_punt:
                self.jugador.fichas = self.jugador.fichas + fichas_apostadas
                return

        jugadores_ronda[ganadores[ganador]].fichas = jugadores_ronda[ganadores[ganador]].fichas + fichas_apostadas