from unipath import Path
from os import listdir
import os

BASE_DIR = Path().absolute()
DIR_PASTAS = BASE_DIR.ancestor(2).child('processos_tjce_lider')
LIST_PASTAS = listdir(DIR_PASTAS)


def str2bool(v):
    return v.lower() in ("true", "t", "1")


def getclassification(data):
    classification = {}
    for x in data:
        a, b = x.rstrip().split(' - ')
        classification.update({int(a): b})
    return classification


def files2str():
    r = []
    for pasta in LIST_PASTAS:
        pasta_path = DIR_PASTAS.child(pasta)
        docs_path = listdir(pasta_path)
        classificacao_path = pasta_path.child('classificacoes_sentenca.txt')

        with open(classificacao_path, "r") as myfile:
            data = myfile.readlines()
        classification = getclassification(data)

        for txt_path in docs_path:
            try:
                id_txt = int(txt_path.strip('.txt'))
                txt_path = pasta_path.child(txt_path)
                with open(txt_path, "r") as f:
                    txt = f.read().replace('\\t', '')\
                        .replace('\t', '').replace('\n', '').replace('\r', '')
                line = '"{0}", "{1}" \n'.format(classification[id_txt], txt)
                r.append(line)
            except:
                pass
    return r


def str2txt(array):
    with open('idf_sentencas.txt', 'r+') as f:
        for line in array:
            f.write(line)

if __name__ == "__main__":
    str2txt(files2str())
