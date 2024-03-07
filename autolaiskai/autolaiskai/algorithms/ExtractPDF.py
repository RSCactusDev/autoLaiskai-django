import re
import pdfplumber
from tabula import read_pdf
from tabulate import tabulate
import csv
import codecs
import regex


## Getting measured plot m_kad - Cadastral number, m_unique - Unique number.
def get_measured_plot_data(filepath):
    with pdfplumber.open(filepath) as pdf:
        first_page = pdf.pages[0]
        
        # PDF converted to text
        a = first_page.extract_text()

        # Unique and Cadastral number of the measured plot.
        x = re.findall(r"kurio unikalus Nr.:\s\w\w\w\w-\w\w\w\w-\w\w\w\w", a)
        m_unique = re.findall(r"\w\w\w\w-\w\w\w\w-\w\w\w\w",str(x))

        x = re.findall(r"kadastro Nr.: \w\w\w\w/\w\w\w\w:[00-99]*", a)
        m_kad = re.findall(r"\w\w\w\w/\w\w\w\w:[00-99]*", str(x))

        ## Unique number formating.
        m_unique = m_unique[0]
        m_unique = m_unique.replace("-", "")   
        m_kad = m_kad[0]
        pdf.close()

    return m_kad, m_unique

## Exctract table from pdf file.
def get_table_data(filepath, data_save):
    tables = read_pdf(filepath, pages="all") 
    ## print(tabulate(tables[0]))
    
    ## Export table individually as CSV.
    tables[0].to_csv(data_save, encoding="cp775") 

    ## Opening table data from CSV.
    file = open(data_save, encoding="cp775")
    csvreader = csv.reader(file)
    header = next(csvreader)
    ## print(header, 'the header')
    """ with codecs.open('readme.txt', 'w', 'cp775') as f:
        f.write(tabulate(tables[0])) """
    ## Table data in list format
    table_data_list = []
    for row in csvreader:
        table_data_list.append(row)
    file.close()
    
    return table_data_list

## Getting measured plot neighbours data: unique/cadastral numbers, neighbour_identity with address in list
def get_neighbours_data(table_data_list):
    neighbour_unikal = []
    neighbours_kad = []
    neighbour_identity_list = []

    for x in table_data_list:
        neighbour_unikal.append(x[2].replace("-", ""))
        try:
            neighbours_kad.append(x[3].replace("* ","")) 
        except:
            print('There is no * symbol in pdf table')
            neighbours_kad.append(x[3])
            
        # Formating neighbour identity with addressess in list (fifth column)
        fifth_column_row = x[4].replace('\n'," ")
        fifth_column_row = fifth_column_row.replace('UŽDAROJI AKCINĖ BENDROVĖ','UAB')
        fifth_column_row = fifth_column_row.replace('"','')
        neighbour_identity_list.append(fifth_column_row)
    
    return neighbour_unikal, neighbours_kad, neighbour_identity_list

## Function to delete list dublicate values by list index (Sometimes Registru Centras generates owners duplicates)
def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)
            
## Collecting people birhtday date or companies a.k number 
def get_owner_id(neighbour_identity_list):
    neighbour_identity_gimdata = []
    neighbour_identity_gimdata_ = []
    ## print(neighbour_identity_list,'neighbour_identity_list')
    for i in neighbour_identity_list:
        people_birthday = regex.findall(r"gim.\s\w*-\w*-\w*,",i)
        ## print(people_birthday,'people birthday')
        company_id = regex.findall(r"(.*?),",i)
        company_id_ = regex.findall(r"(.*?),",i)
        ## print(company_id_,'company_id')
        if 'LIETUVOS RESPUBLIKA' in company_id[0]:
            result = ''
            for i in range(0, len(company_id)):
                if 'a.k' in company_id[i]:
                    if 'a.k' in result:
                        result += ' ir' + company_id[i]
                    else:
                        result += company_id[i]
            neighbour_identity_gimdata.append(result)
            
        if 'LIETUVOS RESPUBLIKA' not in company_id[0]:
            if len(company_id) >= 2:
                for i in range(0,len(company_id)):
                    if 'LIETUVOS RESPUBLIKA' in company_id[i]:
                        for n in range(4):
                            ## print(company_id_,'company id pop')
                            company_id_.pop(i)
           
            for x in company_id_:
                if 'a.k.' in x:
                    neighbour_identity_gimdata.append(x)
            
        if people_birthday == []:
            #logger.info("There is no data about people birthday date")
            pass
            
        for x in people_birthday:
            x = x.replace(",","")
            neighbour_identity_gimdata_.append(x)
            neighbour_identity_gimdata.append(x)
        

    ## print(neighbour_identity_gimdata,'gimimo s')
    return neighbour_identity_gimdata


## Getting measured plot neighbours identity and deleting dublicates
def get_neighbour_identity(neighbour_identity_list, neighbour_identity_gimdata):
    dublicate_index = [] 
    dublicate_index_ = []
    dublicate_index_list = []
    owner_number = []
    neighbour_identity = []
    very = neighbour_identity_gimdata
    owners_=[]

    for s in neighbour_identity_list:
        owners = [] 
        people = regex.findall(r'\p{Lu}*\s\p{Lu}*, gim. \w*-\w*-\w*|\p{Lu}*\s\p{Lu}*\s\p{Lu}*, gim. \w*-\w*-\w*',s)
        company = regex.findall(r'(.*?), a.k',s)
        ## print(people, "People!")
        ## print(company, 'Company!')
        if len(people) != 0 and "LIETUVOS RESPUBLIKA" in people[0]:
            people = []
        if len(company) != 0 and "LIETUVOS RESPUBLIKA" in company[0]:
            second =  company[1].partition("Patikėtinis:")[2]
            ## print(company[0] + second, 'company[0] + second')
            company_1 = company[0] +' Patikėtinis: '+ second 
            owners.append(company_1)
            owners_.append(company_1)
            company = []

        ## Search dublicates and delete
        print(people,'people before delete')
        print(owners,'owner before delete')
        for i in people:
            if i[0] == ' ':
                owners.append(i[1:])
                owners_.append(i[1:])
            else: 
                owners.append(i)
                owners_.append(i)
        print(owners_,'Owners_ after first correction')
        ## Finds owner dublicates indexs
        for i in range(len(owners)):
            for j in range(i + 1, len(owners)):
                if owners[i] == owners[j]  and owners[i] != 'None':
                    ## print(owners[i],'---------owners----------', owners[j],'ii',i,j)
                    dublicate_index.append(j)
        for i in range(len(owners_)):
            for j in range(i + 1, len(owners_)):
                if owners_[i] == owners_[j]  and owners_[i] != 'None':
                    ## print(owners_[i],'---------owners_----------', owners_[j],'ii',i,j)
                    
                    dublicate_index_.append(j)

        ## print(owners,'owners array')
        ## print(dublicate_index,'dublicate_index')
        ### print(dublicate_index_,'dublicate_index_')
        ## print(very,'neighbour_identity_gimdata (very)')
                    
        delete_multiple_element(owners,dublicate_index)
        delete_multiple_element(owners_,dublicate_index_)
        delete_multiple_element(very,dublicate_index_)

        print(owners_, 'owners_ after  delete_multiple_element')
        print(very,'neighbour_identity_gimdata (very) after delete_multiple_element')

        dublicate_index_list.append(dublicate_index)
        owner_number.append(len(owners))
        dublicate_index = []
        dublicate_index_ = []

        ## The owner of the adjacent plot is obtained
        for name_surname in owners:
            name_surname = re.sub(", gim. \d\d\d\d-\d\d-\d\d","", name_surname)
            neighbour_identity.append(name_surname)

        for title in company:
            neighbour_identity.append(title)
            
    print(very,'neighbour_identity_gimdata (very)')

    return neighbour_identity, dublicate_index_list, owner_number


## Adjust MATA_TIP, neighbours cadastral number, neighbours plot addressess by number of owners
def adjust_data(neighbours_kad,owner_number):
    adjusted_neighbours_kad = sum([[s] * n for s, n in zip(neighbours_kad, owner_number)], [])
    print(adjusted_neighbours_kad, 'adjusted_neighbours_kad')
    return  adjusted_neighbours_kad

## Deleting owners duplicates
def delete_owner_duplicates(neighbour_identity):
    to_whom = [] + neighbour_identity
    to_whom = list(dict.fromkeys(to_whom))
    return to_whom

## Exctracting neighbours plot addresses
def get_neighbours_plot_address(neighbour_identity_list, neighbour_identity, dublicate_index_list):
    neighbour_identity_ = []

    for x in neighbour_identity_list:
        
        x = re.sub(r", gim. \w\w\w\w-\w\w-\w\w,",";",x)
        x = re.sub(r",\s*UAB, a.k.\s*\w*, ",";",x)
        x = re.sub(r", a.k.\s*\w*, ",";",x)
        x = re.sub(r"\n"," ",x) 
        
        neighbour_identity_.append(x)

    neighbours_address_list = []

    for x in range(0,len(neighbour_identity_)):
        if "LIETUVOS RESPUBLIKA" in neighbour_identity_[x]:
            #logger.info("LIETUVOS RESPUBLIKA in neighbour_identity")
            ik = re.split(r"LIETUVOS RESPUBLIKA...",neighbour_identity_[x])
            lt_res_adres = ik[1].partition(";")[2]
            # ik.pop()
            neighbours_address_list.append(lt_res_adres)

            neighbour_identity_[x] = ' '.join(ik)
            for i in neighbour_identity:
                if i in neighbour_identity_[x]:
                    for i in neighbour_identity:
                        neighbour_identity_[x] = neighbour_identity_[x].replace(f'{i}','')

                    res_adresiukas = re.split(r";", neighbour_identity_[x])

                    ## Deletes empty [''] items from the list
                    res_adresiukas = list(filter(lambda a: a != '', res_adresiukas))

                    if dublicate_index_list[x] != []:
                        delete_multiple_element(res_adresiukas,dublicate_index_list[x])
                    
                    for i in res_adresiukas:
                        if i[0] == ' ':
                            neighbours_address_list.append(i[1:])
                        else: 
                            neighbours_address_list.append(i)
        else:
            for i in neighbour_identity:
                neighbour_identity_[x] = neighbour_identity_[x].replace(f'{i}','')
        
            res_adresiukas = re.split(r";", neighbour_identity_[x])

            ## Deletes empty [''] items from the list
            res_adresiukas = list(filter(lambda a: a != '', res_adresiukas))

            if dublicate_index_list[x] != []:
                delete_multiple_element(res_adresiukas,dublicate_index_list[x])

            for i in res_adresiukas:
                if i[0] == ' ':
                    neighbours_address_list.append(i[1:])
                else: 
                    neighbours_address_list.append(i)
    print(neighbours_address_list, 'neighbours_address_list')

    return neighbours_address_list


## Combining the obtained data in dict
def merge_data_to_dict(to_whom,neighbour_identity, neighbour_identity_gimdata, neighbours_address_list, adjusted_neighbours_kad):
    letters = {"name": '', "gim_data": '', "kad_nr": [],"siuntimui":'', "sklypo_adresas": [], "coordinates":[], "mat_date": []}
    letters_ = []
    # print(to_whom, 'to whoom')
    # print(neighbour_identity, 'neighbour_identity')
    for i in range(len(to_whom)):
        letters["name"] = to_whom[i]
        for x in range(len(neighbour_identity)):
            # print(to_whom[i], 'to_whom',i, 'neighbour_identity[x]', neighbour_identity[x],'x',x )
            if to_whom[i] == neighbour_identity[x]:
                # print(neighbour_identity_gimdata,x,'neighbour_identity_gimdata and x')
                try:
                    letters["gim_data"] = neighbour_identity_gimdata[i]
                except:
                    pass
                letters["kad_nr"].append(adjusted_neighbours_kad[x])
                try:
                    letters["siuntimui"] = (neighbours_address_list[x])
                except:
                    pass
                # letters['neighbours_address_list'].append(adjusted_address[x])
        letters_.append(letters)
        letters = {"name": '', "gim_data": '', "kad_nr": [],"siuntimui":'', "sklypo_adresas": [], "coordinates":[], "mat_date": []} 

    return letters_