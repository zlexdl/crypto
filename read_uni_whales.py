import json


with open("result.json",'r',encoding='utf-8') as load_f:
    load_dict = json.load(load_f)
    # print(load_dict['messages'])
    for m in load_dict['messages']:
        

if __name__ == '__main__':
    print('test')
