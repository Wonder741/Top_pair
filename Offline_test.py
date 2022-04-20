import csv


# test function process 500 csv files
def csv_process_five():
    cpf_path = 'D:/pythonProjects/LPY/Orders/order_export'
    cpf_number = 500
    for cpf_i in range(cpf_number):
        cpf_path_1 = cpf_path + str(cpf_i) + '.csv'
        with open(cpf_path_1) as f:
            cpf_data = list(csv.reader(f))
            cpf_top_cover = ''
            cpf_top_content = ''
            cpf_top_color = ''
        for cpf_data_i in range(cpf_data.__len__()):
            if 'Status' in cpf_data[cpf_data_i]:
                cpf_state = cpf_data[cpf_data_i][1]
            if 'FootOrthotic.finishing.top_covers.cover' in cpf_data[cpf_data_i]:
                cpf_top_cover = cpf_data[cpf_data_i][1]
            if 'FootOrthotic.finishing.top_covers.content' in cpf_data[cpf_data_i]:
                cpf_top_content = cpf_data[cpf_data_i][1]
            if 'FootOrthotic.finishing.top_covers.color' in cpf_data[cpf_data_i]:
                cpf_top_color = cpf_data[cpf_data_i][1]
        cpf_top_list = [cpf_top_cover, cpf_top_content, cpf_top_color]
        print(cpf_state)
        print(cpf_top_list)


