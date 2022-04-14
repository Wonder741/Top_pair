import json


def build_diction():
    part_count = 70
    diction = {}
    for diction_index in range(part_count):
        diction[diction_index] = {'order_id': '0', 'location_placed': False, 'source': None, 'state': None,
                                  'pair_found': False, 'keyword_1': [], 'top_list': []}
    return diction


def check_diction(cd_diction):
    cd_list = []
    for cd_index in range(10):
        print('In def cd:', cd_diction[cd_index+1]['top_list'])
        cd_temp = cd_diction[cd_index]['top_list']

        if cd_temp == ['eva', '2mm', 'black']:
            cd_code = 100
        elif cd_temp == ['eva', '3mm', 'black']:
            cd_code = 101
        elif cd_temp == ['eva', '2mm', 'blue']:
            cd_code = 102
        elif cd_temp == ['eva', '3mm', 'blue']:
            cd_code = 103
        elif cd_temp == ['eva', '2mm', 'red']:
            cd_code = 104
        elif cd_temp == ['eva', '3mm', 'red']:
            cd_code = 105
        elif cd_temp == ['eva', '2mm', 'blu/blk/grn']:
            cd_code = 106
        elif cd_temp == ['eva', '3mm', 'blu/blk/grn']:
            cd_code = 107
        elif cd_temp == ['eva', '2mm', 'blu/pur/wht']:
            cd_code = 108
        elif cd_temp == ['eva', '3mm', 'blu/pur/wht']:
            cd_code = 109
        elif cd_temp == ['eva', '2mm', 'blu/yel']:
            cd_code = 110
        elif cd_temp == ['eva', '3mm', 'blu/yel']:
            cd_code = 111
        elif cd_temp == ['eva', '2mm', 'red/pur/wht']:
            cd_code = 112
        elif cd_temp == ['eva', '3mm', 'red/pur/wht']:
            cd_code = 113
        elif cd_temp == ['eva', '2mm', 'yel/blk/gry']:
            cd_code = 114
        elif cd_temp == ['eva', '3mm', 'yel/blk/gry']:
            cd_code = 115
        else:
            cd_code = 116
        cd_list.append(cd_code)
    return cd_list


pair_diction = build_diction()
json_diction_path = 'C:/Users/iOrthotics/Desktop/Test/js_diction_2.json'
while True:
    sess = input('\nStart new session? (Enter n for new, c to continue previous, or any other key to exit)')
    if sess == 'n':
        print('Start new session')
        break
    if sess == 'c':
        print('Continue previous session')
        # load saved JSON as dictionary ([0]dictionary, [1]placed part number)
        with open(json_diction_path, 'r') as js_load:
            js_read = json.load(js_load)
        part_index = int(js_read[1]) + 1
        for js_index in range(part_index):
            pair_diction[js_index] = js_read[0][str(js_index)]
        break
    else:
        print('Exiting')
        exit(0)


top_pair_list = check_diction(pair_diction)
print(top_pair_list)