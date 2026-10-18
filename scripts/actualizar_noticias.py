"""Pone en el README las últimas noticias de marcodiez.es (lee el RSS de la web).

Sustituye lo que hay entre <!-- NOTICIAS:INICIO --> y <!-- NOTICIAS:FIN -->. Si no hay cambios, no toca el fichero.
Uso: python scripts/actualizar_noticias.py   (lo lanza cada semana .github/workflows/noticias.yml)
"""
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

RSS = 'https://marcodiez.es/rss.xml'
CUANTAS = 5
README = pathlib.Path(__file__).resolve().parent.parent / 'README.md'
INICIO, FIN = '<!-- NOTICIAS:INICIO -->', '<!-- NOTICIAS:FIN -->'


def noticias():
    req = urllib.request.Request(RSS, headers={'User-Agent': 'actualizar-noticias (github.com/marcodiezferreira)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        raiz = ET.fromstring(r.read())
    salida = []
    for item in raiz.iter('item'):
        titulo, enlace = (item.findtext('title') or '').strip(), (item.findtext('link') or '').strip()
        if titulo and enlace.startswith('https://marcodiez.es/'):
            salida.append(f'- [{titulo.replace("[", "(").replace("]", ")")}]({enlace})')
        if len(salida) == CUANTAS:
            break
    return salida


def main():
    lista = noticias()
    if not lista:
        print('El RSS no trae noticias: no cambio nada.')
        return 0
    texto = README.read_text(encoding='utf-8')
    patron = re.compile(re.escape(INICIO) + r'.*?' + re.escape(FIN), re.S)
    if not patron.search(texto):
        print('No encuentro las marcas NOTICIAS en el README.', file=sys.stderr)
        return 1
    nuevo = patron.sub(lambda _: INICIO + '\n' + '\n'.join(lista) + '\n' + FIN, texto)
    if nuevo == texto:
        print('Sin noticias nuevas.')
        return 0
    README.write_text(nuevo, encoding='utf-8', newline='\n')
    print(f'README actualizado con {len(lista)} noticias.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
