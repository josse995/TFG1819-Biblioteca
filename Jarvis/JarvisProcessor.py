# -*- coding: utf-8 -*-
"""
Módulo PLN Codename Jarvis - Proyecto Janet
Versión 0.5.0

@author: Mauricio Abbati Loureiro - Jose Luis Moreno Varillas
© 2019 Mauricio Abbati Loureiro - Jose Luis Moreno Varillas. All rights reserved.
"""

import os
from rasa_nlu.training_data import load_data
from rasa_nlu.components import ComponentBuilder
from rasa_nlu.model import Trainer
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_nlu import config
from rasa_core import train
from rasa_core.domain import Domain
from rasa_core.training import interactive
from rasa_core.agent import Agent
from rasa_core.utils import EndpointConfig
from rasa_core.tracker_store import MongoTrackerStore

class JarvisProcessor():

    def __init__(self):
        directorioModelos = 'model/default/Jarvis'
        if (os.path.isdir(directorioModelos)):
            self.interpreter = RasaNLUInterpreter(directorioModelos)
            action_endopoint = EndpointConfig(url="http://localhost:5055/webhook")
            tracker_store = MongoTrackerStore(domain= Domain.load('model/dialogue/domain.yml'),
                                              host='mongodb://localhost:27017',
                                              db='rasa',
                                              username='rasa',
                                              password='Pitonisa46')
            self.agent = Agent.load('model/dialogue',
                                    interpreter=self.interpreter,
                                    action_endpoint=action_endopoint,
                                    tracker_store=tracker_store)
            self._slots = {}

    def train_nlu(self):
        
        builder = ComponentBuilder(use_cache=False)
        
        self.__trainer_data = load_data("data/nlu.md")
        self.__trainer = Trainer(config.load("config/config.yml"), builder)
        self.__trainer.train(self.__trainer_data)
        self.__model_directory = self.__trainer.persist('model/',
                                                        fixed_model_name = 'Jarvis')
        
        return self.__model_directory

    def train_dialogue(self, domain_file='domain.yml',
                       stories_file='data/stories.md',
                       model_path='model/dialogue',
                       policy_config='config/config.yml'):
        return train.train_dialogue_model(domain_file=domain_file,
                                          stories_file=stories_file,
                                          output_path=model_path,
                                          policy_config=policy_config)


    def train_all(self):
        model_directory = self.train_nlu()
        self.agent = self.train_dialogue()

        return [model_directory, self.agent]

    def train_interactive(self):
        self.train_nlu()
        self.agent = self.train_dialogue()

        return interactive.run_interactive_learning(self.agent)

    def procesarPeticion(self, peticion, senderid='default'):

        respuesta = {}

        print(senderid)
        respuesta["nlu"] = self.interpreter.parse(peticion)
        #self.agent.
        tracker = self.agent.tracker_store.get_or_create_tracker(sender_id=senderid)
        #mensaje = self.agent.handle_message(peticion)
        #tracker.update(SlotSet("channel", channel))
        #self.agent.tracker_store.save(tracker)
        mensaje = self.agent.handle_text(text_message=peticion, sender_id=senderid)
        #print(self.agent.domain.slots.)
        self.agent.tracker_store.save(tracker)

        self._slots = self.__rellenaSlots(tracker)

        print(respuesta["nlu"])

        for response in mensaje:
            respuesta["text"] = response["text"]
        print(respuesta["text"])

        return respuesta

    def formatearResultado(self, peticion):
        resultado = {}

        resultado['intent'] = peticion['nlu']['intent']['name']
        resultado['entities'] = []
        tmp = {}

        if resultado['intent'] is 'saludos':
            tmp['persona'] = self._slots['persona']
        elif resultado['intent'] is 'me_llamo':
            tmp['persona'] = self._slots['persona']
        elif resultado['intent'] is 'consulta_telefono' or resultado['intent'] is \
                'consulta_localizacion_empty' or resultado['intent'] is 'consulta_telefono_empty' \
                or resultado['intent'] is 'consulta_localizacion' or resultado['intent'] is \
                'consulta_horario_close' or resultado['intent'] is 'consulta_horario_general' \
                or resultado['intent'] is 'consulta_horario_open':
            if self._slots['localizacion'] is not None:
                tmp['localizacion'] = self._slots['localizacion']

        elif resultado['intent'] is 'consulta_libros_kw' or resultado['intent'] is \
                'consulta_libro_kw' or resultado['intent'] is 'consulta_libros_titulo' \
                or resultado['intent'] is 'consulta_libro_autor' or resultado['intent'] is \
                'consulta_libros_titulo_autor' or resultado['intent'] is 'consulta_libros_kw_autor' \
                or resultado['intent'] is 'consulta_libro_kw_autor' or resultado['intent'] is \
                'consulta_libros_autor' or resultado['intent'] is 'consulta_libro_titulo_autor':
            if self._slots['libro'] is not None:
                tmp['libro'] = self._slots['libro']
            if self._slots['autores'] is not None:
                tmp['autores'] = self._slots['autores']
            tmp['searchindex'] = self._slots['searchindex']

        elif resultado['intent'] is 'consulta_articulos_kw' or resultado['intent'] is \
                'consulta_articulo_kw':
            tmp['articulos'] = self._slots['libro']
            tmp['searchindex'] = self._slots['searchindex']

        elif resultado['intent'] is 'consulta_juegos_kw' or resultado['intent'] is \
                'consulta_juego_kw':
            tmp['juego'] = self._slots['juego']
            tmp['searchindex'] = self._slots['searchindex']

        elif resultado['intent'] is 'consulta_musicas_kw' or resultado['intent'] is \
                'consulta_musica_kw':
            if self._slots['musica'] is not None:
                tmp['musica'] = self._slots['musica']
            if self._slots['autores'] is not None:
                tmp['autores'] = self._slots['autores']
            tmp['searchindex'] = self._slots['searchindex']

        elif resultado['intent'] is 'consulta_peliculas_kw' or resultado['intent'] is \
                'consulta_pelicula_kw':
            if self._slots['pelicula'] is not None:
                tmp['pelicula'] = self._slots['pelicula']
            if self._slots['autores'] is not None:
                tmp['autores'] = self._slots['autores']
            tmp['searchindex'] = self._slots['searchindex']

        elif resultado['intent'] is 'busca_mas' or resultado['intent'] is \
                'mas_info_primero' or resultado['intent'] is 'mas_info_segundo' or \
                resultado['intent'] is 'mas_info_tercero':
            if self._slots['pelicula'] is not None:
                tmp['pelicula'] = self._slots['pelicula']
            elif self._slots['libro'] is not None:
                tmp['libro'] = self._slots['libro']
            elif self._slots['articulos'] is not None:
                tmp['articulos'] = self._slots['articulos']
            elif self._slots['musica'] is not None:
                tmp['musica'] = self._slots['musica']
            if self._slots['autores'] is not None:
                tmp['autores'] = self._slots['autores']

            tmp['searchindex'] = self._slots['searchindex']

        #for entity in peticion['nlu']['entities']:
            #tmp = {}
            #tmp['type'] = entity['entity']
            #tmp['value'] = entity['value']
            #resultado['entities'].append(tmp)

        resultado['message'] = peticion['text']
        resultado['entities'].append(tmp)
            
        return resultado

    def __rellenaSlots(self, tracker):
        list = {}
        list['libro'] = tracker.get_slot("libro")
        list['articulos'] = tracker.get_slot("articulos")
        list['autores'] = tracker.get_slot("autores")
        list['localizacion'] = tracker.get_slot("localizacion")
        list['musica'] = tracker.get_slot("musica")
        list['pelicula'] = tracker.get_slot("pelicula")
        list['persona'] = tracker.get_slot("persona")
        list['searchindex'] = tracker.get_slot("searchindex")

        return list


if __name__ == '__main__':
    jarvis = JarvisProcessor()
    while True:
        a = input()
        if a == 'stop':
            break
        responses = jarvis.agent.handle_message(a)
        for response in responses:
            print(response)
            print(response["text"])
