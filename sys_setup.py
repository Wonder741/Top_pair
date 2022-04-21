import os
import io
import cv2
from datetime import datetime
import csv
import re
import subprocess
import tkinter as tk
from tkinter import *
from tkinter import ttk
from google.cloud import vision


def google_vision_setup(env_var_value):
    env_var = 'GOOGLE_APPLICATION_CREDENTIALS'
    os.environ[env_var] = env_var_value


def google_vision(google_vision_path):
    #  detect text in image
    google_vision_text = []
    with io.open(google_vision_path, 'rb') as image_file:
        content = image_file.read()

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if len(annotations) < 1:
        print('NO characters detected')
    else:
        print('characters detected')
        for i in range(1, len(annotations)):
            google_vision_text.append(annotations[i].description)
    return google_vision_text


# Function to capture image from the usb camera. Subject to change if camera changes.
def camera_capture(capture_camera_index, capture_frame_width, capture_frame_height):
    # initialize the camera
    capture_cam = cv2.VideoCapture(capture_camera_index, cv2.CAP_DSHOW)  # 0,1 -> index of camera

    capture_cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_width)
    capture_cam.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_height)
    capture_cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    # capture_cam.set(cv2.CAP_PROP_FOCUS, 320)
    #  capture_cam.set(cv2.CAP_PROP_FOCUS, 0)
    #  capture_cam.set(cv2.CAP_PROP_BRIGHTNESS, 0)
    #  capture_cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)

    capture_success, capture_camera_image = capture_cam.read()
    if capture_success:  # frame captured without any errors
        print('capture success')
    else:
        print('capture FAILED')
    capture_cam.release()
    return capture_camera_image


def image_save(image_to_save, save_path, image_index):
    now = datetime.now()
    date_hour = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)

    # save image for ocr
    cv2.imwrite(save_path + 'scan.jpg', image_to_save)
    # copy image as backup
    image_file_name = save_path + date_hour + str(image_index) + '.jpg'
    cv2.imwrite(image_file_name, image_to_save)
    print('image saved as: ' + image_file_name)
    return image_file_name


# Function to display matched order id or order key word on computer
# Inputs: order_diction
def display_grid(order_diction):
    root = tk.Tk()
    root.title("Sorted Grid")
    root.geometry('1500x1000')
    cols = ["", "A", "B", "C", "D", "E", "F", "G"]
    rows = ["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    od_index = 0

    for grid_i in range(11):
        for grid_j in range(8):
            if grid_i == 0:
                tk.Label(root, relief='groove', height=2, width=5,
                         text=cols[grid_j]).grid(row=grid_i, column=grid_j, sticky='NSEW')
            elif grid_j == 0:
                tk.Label(root, relief='groove', height=3, width=5,
                         text=rows[grid_i]).grid(row=grid_i, column=grid_j, sticky='NSEW')
            else:
                filled_words = str(order_diction[od_index]['order_id']) + '\n' + str(order_diction[od_index]['source']) + \
                               '\n' + str(order_diction[od_index]['keyword'])
                tk.Label(root, bg="white", height=3, width=24, relief='ridge',
                         text=filled_words).grid(row=grid_i, column=grid_j, sticky='NSEW')
                od_index = od_index + 1
    root.mainloop()


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


def write_csv(wc_csv_path, image_name, csv_orc_words):
    data = [image_name, csv_orc_words]

    with open(wc_csv_path, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the data
        writer.writerow(data)


def words_process(string_list):
    # find 6 digital number
    result_number = re.findall(r'\d{6}', str(string_list))
    # find non-digital characters and remove symbols
    if result_number:
        print('find order number: ', result_number)
        result_word = re.findall(r'\D+', str(string_list))
        result_word = re.findall(r'\w+', str(result_word))
        result_word = str(result_word).lower()
        wp_number_flag = True
    # cannot find number id, use keyword instead
    else:
        result_word = re.findall(r'\w+', str(string_list))
        result_word = str(result_word).lower()
        print('NOT find order number')
        print('use keyword instead: ', result_word)
        wp_number_flag = False

    return result_number, result_word, wp_number_flag


# Function to check the order id against the server using the CLI tool developed
# Inputs: Order number (Checks for 'cooling')
def server_check(sc_order_number, sc_csv_path, sc_tool_path):
    args = [sc_tool_path, 'get-order', '-s', 'aus', '-k', '1LpGQMtIo3oHy6D174fmj40p',
            '--order-number', str(sc_order_number), '-f', sc_csv_path, '-q']
    subprocess.call(args)

    sc_order_state = None
    sc_data_colour = None
    sc_data_thick = None
    sc_data_type = None

    with open(sc_csv_path) as csvDataFile:
        sc_data = list(csv.reader(csvDataFile))
        # print(sc_data)

        for sc_data_index in range(len(sc_data)):
            # print(sc_data_index)
            sc_data_name = sc_data[sc_data_index][0]
            sc_data_data = sc_data[sc_data_index][1]
            if sc_data_name == 'OrderNumber' and str(sc_data_data) == '00217':
                print("ORDER ID INCORRECT or FAILED to connect server: ", sc_order_number)
                return sc_order_state, sc_data_type, sc_data_colour, sc_data_thick
            else:
                if sc_data_name == 'Status':
                    sc_order_state = str(sc_data_data).lower()
                # search for colour information
                if sc_data_name == 'FootOrthotic.finishing.top_covers.color':
                    sc_data_colour = str(sc_data_data).lower()
                    break
                if sc_data_name == 'FootOrthotic.finishing.top_covers.cover':
                    sc_data_type = str(sc_data_data).lower()
                if sc_data_name == 'FootOrthotic.finishing.top_covers.content':
                    sc_data_thick = str(sc_data_data).lower()
    print('ORDER information found: ', sc_order_number)
    return sc_order_state, sc_data_type, sc_data_colour, sc_data_thick


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


def display_table(dt_diction):
    root = Tk()
    root.title('Pair position')
    root.geometry('700x1000')

    my_tree = ttk.Treeview(root, height='1000')
    # Format column
    my_tree['column'] = ['Position', 'Order ID', 'Source', 'Keywords']
    my_tree.column('#0', width=30)
    my_tree.column('Position', anchor=CENTER, width=60)
    my_tree.column('Order ID', anchor=CENTER, width=80)
    my_tree.column('Source', anchor=CENTER, width=80)
    my_tree.column('Keywords', anchor=W, width=400)

    # Create heading
    my_tree.heading('#0', text='')
    my_tree.heading('Position', text='Position', anchor=CENTER)
    my_tree.heading('Order ID', text='Order ID', anchor=CENTER)
    my_tree.heading('Source', text='Source', anchor=CENTER)
    my_tree.heading('Keywords', text='Keywords', anchor=W)

    # Adding data
    for dt_index in range(len(dt_diction)):
        dt_record = dt_diction[dt_index]
        dt_d = (dt_index // 7) + 65
        dt_da = chr(dt_d)
        dt_r = dt_index % 7
        dt_p = str(dt_da) + str(dt_r)

        my_tree.insert(parent='', index='end', iid=dt_index, text='',
                       value=(dt_p, dt_record['order_id'], dt_record['source'], dt_record['keyword_1']))
    my_tree.pack(pady=5)
    root.mainloop()


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


def check_diction(cd_cover_list, cd_flag):
    cd_temp = cd_cover_list
    if cd_flag is True:
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
        elif cd_temp == ['eva', '2mm', 'red/pur/wht']:
            cd_code = 110
        elif cd_temp == ['eva', '3mm', 'red/pur/wht']:
            cd_code = 111
        elif cd_temp == ['eva', '2mm', 'yel/blk/gry']:
            cd_code = 112
        elif cd_temp == ['eva', '3mm', 'yel/blk/gry']:
            cd_code = 113
        elif cd_temp == ['eva', '2mm', 'blu/yel']:
            cd_code = 114
        elif cd_temp == ['eva', '3mm', 'blu/yel']:
            cd_code = 115
        else:
            cd_code = 116
            cd_flag = False
    return cd_code, cd_flag

if __name__ == '__main__':
    pass
