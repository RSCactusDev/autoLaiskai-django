from re import S
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import  HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_http_methods
import json
from datetime import date
from docxtpl import DocxTemplate
from django.http import JsonResponse
from django.http import FileResponse
from urllib.parse import urljoin
from django.contrib import messages
import os
import zipfile

# selenium imports
import ast

# Forms impoerts
from .forms import UserTemplateHeader

# Models imports
from authentication.models import CustomUser
from core.models import NeighbourNote, CrudList

# Algorithms app imports
from algorithms.mergedocx import mergedocx
from algorithms.ExtractPDF import (
    get_measured_plot_data,
    get_table_data,
    get_neighbours_data,
    get_neighbour_identity,
    get_owner_id,
    adjust_data,
    delete_owner_duplicates,
    get_neighbours_plot_address,
    merge_data_to_dict
)
from algorithms.scrapingData import (
    main_scraping, 
    get_main_plot_data
    )



@login_required
def landing_page(request, *args, **kwargs):
    context = {}
    user = request.user
   
    # Gretimybių pažymos įkėlimas
    if request.method == 'POST':
        uploaded_rc_pdf = request.FILES['rc_pdf']
        request.session['file_name'] = str(uploaded_rc_pdf)
        if NeighbourNote.objects.filter(fk=request.user.id):
            uploaded_rc_pdf_str = 'temp/' +'user_' + str(user.id) +'/'+ str(uploaded_rc_pdf)
            neighbournote = NeighbourNote.objects.get(fk=request.user.id)
            neighbournote.rc_pdf = uploaded_rc_pdf 
            neighbournote.save()
            print(uploaded_rc_pdf.name, 'uploaded_rc_pdf.name')
            NeighbourNote.objects.update(rc_pdf_old=uploaded_rc_pdf_str )
            return HttpResponseRedirect('/generate_letters')
        # Jei toks modelis neegzistuoja sukuria    
        else:
            neighbournote = NeighbourNote.objects.create(rc_pdf=uploaded_rc_pdf, fk = request.user)
            neighbournote.rc_pdf_old = 'temp/' + 'user_' + str(user.id) +'/'+ uploaded_rc_pdf.name
            neighbournote.save()
            print(uploaded_rc_pdf.name, 'uploaded_rc_pdf.name')
            return HttpResponseRedirect('/generate_letters')
       
    return render(request, "main/base.html", context)

@login_required
def generate_letters_view(request):

    if request.method == 'POST':
        count_crudlist = CrudList.objects.filter(fk = request.user).count()
        all_crudlist = CrudList.objects.filter(fk = request.user)
        letters_ = []
        selected_values = request.POST.getlist('ok')

        """ for i in all_crudlist:
            print(i,'all_crudlist values') """
        
        # print(selected_values, 'Selected value')

        request.session['session_name'] = selected_values
        for i in selected_values:
            letters = {"name": '', "gim_data": '', "kad_nr": [],"siuntimui":'', "sklypo_adresas": [], "coordinates":[], "mat_date": []}
            crudlist_from_database = CrudList.objects.filter(fk = request.user, id = int(i))
            for i in crudlist_from_database:
                letters["name"] = i.name
                letters["gim_data"] = i.gim_data
                letters["siuntimui"] = i.name_address
                letters["kad_nr"] = ast.literal_eval(i.kad_nr)
                letters["sklypo_adresas"] = ast.literal_eval(i.kad_address)
                letters["coordinates"] = ast.literal_eval(i.coordinates)
                letters["mat_date"] = ast.literal_eval(i.mat_date)
            
            letters_.append(letters)
        
        print(letters_, 'Before scraping')
      
        main_scraping(letters_)

        # print(letters_, 'After scraping')

        for x, letter in zip(selected_values, letters_):
            CrudList.objects.filter(fk=request.user, id=int(x)).update(
                coordinates=letter['coordinates'],
                kad_address=letter['sklypo_adresas'],
                name_address=letter['siuntimui'],
                mat_date=letter['mat_date']
            )

        return HttpResponseRedirect('/generate_letters_2')
    else:
        ## ---------------------------- ExtractPDF algorithm ---------------------------------
        uploaded_rc_pdf = NeighbourNote.objects.get(fk = request.user)
        
        media_url = settings.MEDIA_ROOT
        filepath = media_url + '\\'+ str(uploaded_rc_pdf.rc_pdf).replace('/',"\\")
        # print('---------------------------------------------------------------------------')
        # print('Filepath: ',filepath)
        m_kad, m_unique = get_measured_plot_data(filepath)
        # print('Matuojamas kad Nr: ',m_kad, 'Matuojamo unikalus Nr. : ', m_unique)

        user = request.user
        data_save = media_url + '\\'+ 'temp\\' + 'user_' + str(user.id) +'\\data.csv'
        table_data_list = get_table_data(filepath, data_save)

        
        neighbour_unikal, neighbours_kad, neighbour_identity_list = get_neighbours_data(table_data_list)
        print(neighbour_unikal, neighbours_kad,'--')

        neighbour_identity_gimdata = get_owner_id(neighbour_identity_list)
        #print('---------------------------------------------------------------------------')
        #print('Gimimo data:')
        print(neighbour_identity_gimdata)
        #print('---------------------------------------------------------------------------')

        neighbour_identity, dublicate_index_list, owner_number = get_neighbour_identity(neighbour_identity_list,neighbour_identity_gimdata)
        #print(neighbour_identity, dublicate_index_list,'owner number',  owner_number)
    
        adjusted_neighbours_kad = adjust_data(neighbours_kad,owner_number)

        to_whom = delete_owner_duplicates(neighbour_identity)
        #print(to_whom, 'to_whom')

        neighbours_address_list = get_neighbours_plot_address(neighbour_identity_list, neighbour_identity, dublicate_index_list)
        #print(neighbours_address_list,'kaiminu adresai')

        letters_ = merge_data_to_dict(to_whom,neighbour_identity, neighbour_identity_gimdata, neighbours_address_list, adjusted_neighbours_kad)
        #print(letters_)

        #print(letters_[0]['kad_nr'])

        # Add items from pdf file to database
        CrudList.objects.filter(fk = request.user).delete()
        for i in letters_:
            crudlist = CrudList.objects.create(name=i['name'], kad_nr=i['kad_nr'],
                                                name_address=i['siuntimui'], gim_data=i['gim_data'],
                                                coordinates=i['coordinates'], kad_address=i['sklypo_adresas'],
                                                mat_date=i['mat_date'] ,fk = request.user) 
            crudlist.save()
    
        crudlist_from_database = CrudList.objects.filter(fk = request.user)

        context = {'uploaded_rc_pdf':uploaded_rc_pdf.rc_pdf, 
                    'letters':letters_, 'crudlist_from_database':crudlist_from_database}


    return render(request, "app/generate_letters.html", context)

#---------------------------------------------------------------------------
@login_required
def search_address(request):
    selected_values = request.session.get('session_name')
    selected_values_crudlist = []
    for i in selected_values:
        crudlist_from_database = CrudList.objects.filter(fk = request.user, id = int(i))
        selected_values_crudlist.append(crudlist_from_database)
    context = {'selected_values_crudlist':selected_values_crudlist}
    
    return render(request, "app/generate_letters_2.html", context) 


@login_required
def settings_view(request):
    # Rekvizitų įkėlimas
    user = request.user
    if request.method =='POST' and 'upload' in request.POST:
        form = UserTemplateHeader(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/settings')
    else:
        form = UserTemplateHeader()
    
    file = CustomUser.objects.filter(email=request.user).values()
    
    return render(request, "app/settings.html", {'form': form, 'file': file} )

# Rekvizitų sujungimas su jau egzistuojančiu pavyzdžiu
@login_required
def generate(request):
    user = request.user
    media_url = settings.MEDIA_ROOT

    first = CustomUser.objects.filter(email=request.user).values_list('template_header')
    first_temp = media_url + '\\'+ first[0][0].replace('/',"\\")

    second_tmp = '\Template_KV.docx'
    second_tmp = media_url + second_tmp 

    output_file = media_url + '\\' +'user_' + str(user.id) + '\\'+ 'Template_KV.docx'
    output_file_database = 'user_' + str(user.id) + '\\'+ 'Template_KV.docx'

    mergedocx(first_temp, second_tmp, output_file)

    doc = CustomUser.objects.get(id=user.id)
    doc.generated_kv = output_file_database
    doc.save() 
    messages.success(request, "Rekvizitai sukurti sėkmingai")
    return HttpResponseRedirect('/settings')

def string_to_list(input_str):
    # Split the string by comma and strip whitespace from each item
    items = [item.strip() for item in input_str.split(',')]
    return items

def split_address_string(address_string, delimiter=';'):
    return [part.strip() for part in address_string.split(delimiter)]


@require_http_methods(["POST"])
def process_table_data(request):
    try:
        user = request.user
        data = json.loads(request.body)
        table_data = data.get('tableData')
        def rename_key(table_data, old_key, new_key):
            for item in table_data:
                if old_key in item:
                    item[new_key] = item.pop(old_key)
            return table_data
        table_data = rename_key(table_data, 'Sklypo adresas (formatas a;a)','Sklypo adresas')
        # print(table_data, 'data from table_data')
        letters = {'name': '', 'gim_data': '', 'kad_nr': [],'siuntimui':'', 'neighbours_address_list': [], 'matavimu_data':''}
        letters_ = []
        for i in table_data:
            letters['name'] = i["Savininkas"] 
            letters['gim_data'] = i["gim-data/ak. nr."] 
            letters['kad_nr'] = string_to_list(i["Kadastro numeris"])
            letters['siuntimui'] = i["Savininko gyv. vieta"] 
            letters['neighbours_address_list'] = split_address_string(i["Sklypo adresas"])
            letters['matavimu_data'] = i['Matavimų data']
            letters_.append(letters)
            letters = {'name': '', 'gim_data': '', 'kad_nr': [],'siuntimui':'', 'neighbours_address_list': []}
        # print(letters_, 'pakoreguotas')


        media_url = settings.MEDIA_ROOT
        doc = DocxTemplate( media_url + '\\' +'user_' + str(user.id) + '\\'+ 'Template_KV.docx')
        today = date.today()
        if isinstance(user, CustomUser) and hasattr(user, 'nr') and user.nr is not None:
            mb_nr = user.nr
        else:
            mb_nr = 0

        path = media_url + '\\temp\\' + 'user_' + str(user.id) +'\\'
        uploaded_rc_pdf = NeighbourNote.objects.get(fk = request.user)
        media_url = settings.MEDIA_ROOT
        filepath = media_url + '\\'+ str(uploaded_rc_pdf.rc_pdf).replace('/',"\\")
        m_kad, m_unique = get_measured_plot_data(filepath)
        mat_adress = get_main_plot_data(m_kad)
        generated_files = []
        generated_urls = []
        #print('success')
        if letters_ != []:
            #print('success2')
            try:
                
                for i in range(0,len(letters_)):
                    print("Creating letter for:\n ",letters_[i]['name'])
                    kad_nr = ''
                    address_final = ''
                    if len(letters_[i]['kad_nr']) > 1: 
                        # print('inside if')
                        # print('leters', letters_)
                        for n in range(0,len(letters_[i]['kad_nr'])):
                            if n != len(letters_[i]['kad_nr'])-1:
                                #print(kad_nr, 'kad_nr pries')
                                #print(letters_[i]['kad_nr'][n], 'ok')
                                measurement_data = letters_[i]['matavimu_data']
                                kad_nr += str(letters_[i]['kad_nr'][n]) + " ir "
                                address_final += str(letters_[i]['neighbours_address_list'][n]) + " ir "
                                #print(n, kad_nr, 'pirmas')
                            else:
                                measurement_data = letters_[i]['matavimu_data']
                                kad_nr += str(letters_[i]['kad_nr'][n])
                                address_final += str(letters_[i]['neighbours_address_list'][n])
                                a = letters_[i]['name']
                                b = letters_[i]['siuntimui']
                        mb_nr += 1
                        context = {'name': f'{a}', 'matavimu_data':f'{measurement_data}','siuntimui': f'{b}', 'MKAD':f'{m_kad}', 'gret_mat':f'{kad_nr}', \
                            'mat_adress':f'{mat_adress}', 'date':f'{today}', 'neighbours_address_list': f'{address_final}', 'sudarymo_vieta': 'Vilnius',\
                                'MB_NR': f'{mb_nr}'}
                        doc.render(context)
                        doc.save(f'{a}'+f'{i}'+'_Rendered.docx')
                        #print(kad_nr)
                        #print(address_final,"\n")
                       
                        doc.save(path + f'{a}'+f'{i}'+'_Rendered.docx')
                        generated_files.append(path + f'{a}'+f'{i}'+'_Rendered.docx')
                    else:
                        #print('else')
                        mb_nr += 1
                        kad_nr += letters_[i]['kad_nr'][0]
                        address_final += letters_[i]['neighbours_address_list'][0]
                        measurement_data = letters_[i]['matavimu_data']
                        a = letters_[i]['name']
                        b = letters_[i]['siuntimui']
                        context = {'name': f'{a}', 'matavimu_data':f'{measurement_data}','siuntimui': f'{b}', 'MKAD':f'{m_kad}', 'gret_mat':f'{kad_nr}', \
                            'mat_adress':f'{mat_adress}', 'date':f'{today}', 'neighbours_address_list': f'{address_final}', 'sudarymo_vieta': 'Vilnius' ,\
                                'MB_NR': f'{mb_nr}'}
                        doc.render(context)
                        
                        doc.save(path + f'{a}'+f'{i}'+'_Rendered.docx')
                        generated_files.append(path + f'{a}'+f'{i}'+'_Rendered.docx')
                        
                
                print("Total letters created: ",len(letters_))
                print("Finished processing letter for: ", letters_[i]['name'])
                if isinstance(user, CustomUser):
                    user.nr = mb_nr
                    user.save()

            except Exception as e:
                print("Error processing letter for ", letters_[i]['name'], ": ", str(e))
        else:
            print("Data could not be retrieved")
        print(generated_files, 'generated_files')
        for file_path in generated_files:
            # Convert local file paths to URLs
            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            file_url = urljoin(settings.MEDIA_URL, relative_path.replace('\\', '/'))
            generated_urls.append(file_url)
        # Create the ZIP file
        zip_file_directory = os.path.join(settings.MEDIA_ROOT, 'temp', f'user_{user.id}')
        zip_file_path = os.path.join(zip_file_directory, 'Kvietimai.zip')
        create_zip(generated_files, zip_file_path)
         # Generate URL for the ZIP file
        relative_zip_path = os.path.relpath(zip_file_path, settings.MEDIA_ROOT)
        zip_file_url = urljoin(settings.MEDIA_URL, relative_zip_path.replace('\\', '/'))

        return JsonResponse({'status': 'success', 'message': 'Data processed successfully.', 'files': generated_urls, 'zip_file': zip_file_url})

    
    except Exception as e:
 
        return JsonResponse({'status': 'error', 'message': str(e)})
    

def download_file(request, file_path):
 
    """ file_path = os.path.join(settings.MEDIA_ROOT, file_path) """
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponseNotFound()

def create_zip(files, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    return zip_name