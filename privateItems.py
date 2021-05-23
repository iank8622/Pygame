'''
目前已無作用。
為優化前主程式之私有物件。
'''

class Dic():
        def __init__(self):
            self.__dic = locals()

        def set_dic(self, name, obj):
            self.__dic[name] = obj

        def get_dic(self, name):
            return self.__dic[name]