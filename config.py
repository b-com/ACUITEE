# config.py – Software ACUITEE
# Copyright 2021 b<>com. All rights reserved.
# This software is licensed under the Apache License, Version 2.0.
# You may not use this file except in compliance with the license. 
# You may obtain a copy of the license at: 
# http://www.apache.org/licenses/LICENSE-2.0 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and 
# limitations under the License.

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'1\x11s\xfa\x83Y]\x9b\xb2\xd2\xff\x82\xe3\xa8F\xad'
    JWT_SECRET_KEY = SECRET_KEY
    JSON_REPO = "."
    EXAMPLE_NOTE = """Chère Consœur,
Je vous remercie de m'avoir adressé en consultation de génétique la jeune PRENOM NOM, née le DD/DD/DDDD, accompagnée de ses parents. PRENOM est suivie pour un retard global de développement associé à des difficultés de comportement.
Sur le plan familial, PRENOM est le seul enfant du couple. La maman a eu d'une première union un fils âgé de 10 ans en bonne santé et qui n'a pas eu de problème dans son développement. Les parents ne sont pas apparentés. Le papa est en parfaite santé. A noter chez son neveu un trouble du spectre de l’autisme avec un suivi au CAMSP. La maman est en bonne santé et il n'existe pas d'antécédent notable de son côté.
Concernant PRENOM, la grossesse avait été marquée par une clarté nucale augmentée, sans autre anomalie lors du suivi échographique. Elle est née à terme avec des mensurations dans la norme.
Sur le plan développemental, il existe un retard psychomoteur avec une tenue assise acquise à l'âge de 15 mois, une marche acquise à l'âge de 3 ans ayant nécessité une prise en charge en kinésithérapie. Sur le plan du langage, elle est actuellement capable de répéter quelques mots mais ne construit pas actuellement de phrases. Sur le plan du comportement, elle se montre assez hyperactive, avec des difficultés attentionnelles. Elle n'a jamais fait de crise d'épilepsie. 
A l'examen ce jour, à l'âge de 4 ans, PRENOM pèse 12 kg, inférieur à - 2 DS pour une taille de 99 cm (-1 DS) et un PC mesuré à 46.5 cm (-2.5 DS). Il existe une hyperlaxité distale. Sur le plan cardiaque, je n'ai pas perçu de souffle. On note sur le plan morphologique quelques particularités, à savoir des oreilles basses et en rotation postérieure, un épicanthus, une racine du nez assez proéminente. 
Au total, je rencontre ce jour PRENOM âgé de 4 ans qui présente un retard global de développement associé à des troubles comportementaux et une microcéphalie. Devant ce tableau, je n'ai pas de diagnostic étiologique précis et propose la réalisation d'un exome en trio. Les deux parents ont donc été prélevés ce jour pour réaliser cette analyse. 
Je ne manquerai pas de tenir informé la famille dès réception des résultats.
Confraternellement. """
    CERT_FILE = ''
    KEY_FILE  = ''
