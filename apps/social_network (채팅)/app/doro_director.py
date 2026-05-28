from fastapi import FastAPI

from apps.doro.app.doro_reader import DoroReader




app = FastAPI(title="Doro Director")



class DoroDirector:
    def __init__(self):
        pass

    def get_data(self):
        dr = DoroReader()
        return dr.get_data()




    