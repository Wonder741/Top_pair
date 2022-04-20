import os
import io
from datetime import datetime
import csv
import re
import subprocess
import Offline_test


# create new diction with 7x8 elements
def build_new_diction(bnd_number):
    bnd_diction = {}
    for bnd_i in range(bnd_number):
        bnd_diction[bnd_i] = {'order_id': '00217',  # default order number returned from server
                              'placed': False,  # position is occupied
                              'paired': False,
                              'source': None,  # internal or external
                              'state': None,  # status of order
                              'keyword': [],  # keywords of order
                              'top_list': []  # cover, content, and colour of top cover
                              }
    return bnd_diction


# add row into a csv file
def write_csv_add_row(wca_csv_path,  # file path of csv to be edited
                      wca_list_data  # list of data to be added to a new row of csv file
                      ):
    with open(wca_csv_path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(wca_list_data)


# if order id exist, check order id from diction, else, check order keyword
# if order match in diction, pair parts, else put part in new position
# return a flag that indicates new internal order paired
def diction_fill_check(dfc_diction,  # diction to be filled or checked
                       dfc_order_flag,  # order id exist in server
                       dfc_placed_index,  # how many order in diction
                       dfc_part_id,  # order id in number
                       dfc_part_keyword,  # if order id does not exist, use keyword instead
                       dfc_order_state,  # status of order
                       dfc_top_list  # for top cover pairing
                       ):
    print('Order exist: ', dfc_order_flag)
    dfc_order_paired_flag = False
    dfc_recycle = []
    dfc_i = 0

    if dfc_order_flag:
        for dfc_i in range(dfc_placed_index + 1):
            if dfc_diction[dfc_i]['order_id'] == str(dfc_part_id):
                dfc_diction[dfc_i]['paired'] = True
                dfc_order_paired_flag = True
                print('TWO internal parts paired at position: ', dfc_i)
                break
            elif dfc_diction[dfc_i]['placed'] is False and dfc_i < dfc_placed_index:
                dfc_recycle.append(dfc_i)
            elif dfc_i == dfc_placed_index:
                if not dfc_recycle:
                    dfc_j = dfc_i
                else:
                    dfc_j = dfc_recycle[0]
                dfc_diction[dfc_j]['order_id'] = str(dfc_part_id)
                dfc_diction[dfc_j]['placed'] = True
                dfc_diction[dfc_j]['source'] = 'IN'
                dfc_diction[dfc_j]['keyword'] = dfc_part_keyword
                dfc_diction[dfc_j]['state'] = dfc_order_state
                dfc_diction[dfc_j]['top_list'] = dfc_top_list
                print('Single internal part placed at position: ', dfc_j)
                dfc_i = dfc_j
                break
    else:
        for dfc_i in range(dfc_placed_index + 1):
            if dfc_diction[dfc_i]['keyword'] == dfc_part_keyword:
                dfc_diction[dfc_i]['paired'] = True
                print('TWO external parts paired at position: ', dfc_i)
                break
            elif dfc_diction[dfc_i]['placed'] is False and dfc_i < dfc_placed_index:
                dfc_recycle.append(dfc_i)
            elif dfc_i == dfc_placed_index:
                if not dfc_recycle:
                    dfc_j = dfc_i
                else:
                    dfc_j = dfc_recycle[0]
                dfc_diction[dfc_j]['keyword'] = dfc_part_keyword
                dfc_diction[dfc_j]['placed'] = True
                dfc_diction[dfc_j]['source'] = 'EX'
                print('Single external part placed at position: ', dfc_j)
                dfc_i = dfc_j
                break
    print("Diction filled")
    return dfc_diction, dfc_i, dfc_order_paired_flag


# if a new internal order part paired, clean the data in diction, recycle the position in diction
def diction_paired_clean(dpc_diction,  # diction to be edited
                         dpc_index  # diction index to be cleaned
                         ):
    dpc_diction[dpc_index] = {'order_id': '00217',  # default order number returned from server
                              'placed': False,  # position is occupied
                              'paired': False,
                              'source': None,  # internal or external
                              'state': None,  # status of order
                              'keyword': [],  # keywords of order
                              'top_list': []  # cover, content, and colour of top cover
                              }
    print('Diction position ' + str(dpc_index) + ' cleaned and recycled')
    return dpc_diction


if __name__ == '__main__':
    Pair_diction = build_new_diction(57)
    test_list = [221100, 221101, 221102, 221108, 221100, 230000, 230005, 221108, 224410, 221101, 221102, 221103,
                 221103, 230001, 230004, 230004, 230002, 224410, 230005, 230001, 230002, 230003, 230003, 230000]
    test_keyword = ['aa', 'bb', 'ab', 'ba', 'bb', 'cc', 'aa', 'cc', 'ab', 'ba']
    order_flag = True
    keyword = 'K'
    state = 'S'
    top_list = 'T'
    for i in range(len(test_list)):
        Pair_diction, Pair_index, Paired_flag = diction_fill_check(Pair_diction, order_flag, i, test_list[i], keyword,
                                                                   state, top_list)
        if Paired_flag:
            Pair_diction = diction_paired_clean(Pair_diction, Pair_index)
        print(Pair_index, Paired_flag)
