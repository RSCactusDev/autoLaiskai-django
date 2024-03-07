from lib2to3.pgen2.driver import Driver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import time 

def main_scraping(letters_):

    options = Options()
  
    options.headless = True
  
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options) 
    driver.set_window_size(1920,1080)


    get_coordinates(letters_,driver)

    get_regia_adress(letters_,driver) 

    get_mapslt_adress(letters_,driver)

    driver.close()

    return letters_

def get_main_plot_data(m_kad):
    
    options = Options()
  
    options.headless = True
  
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options) 
    driver.set_window_size(1920,1080)

    main = [{'kad_nr': [m_kad], 'coordinates': [], 'sklypo_adresas': []}];
    
    main = get_coordinates(main,driver)
    # print(main, 'letters_ after get_coordinates')
    main = get_regia_adress(main,driver)
    # print(main, 'letters_ after get_regia_adress')
    main = get_mapslt_adress(main,driver)
    main = main[0]
    # print(main, 'letters_ after get_mapslt_adress')
    driver.close()

    mat_adress = main['sklypo_adresas'][0]
    # print(mat_adress, 'Matuojamo sklypo adresas')

    return mat_adress


def get_coordinates(letters_,driver):
    # print(letters_, 'letters_ pries Geomatininka')
    ## Prisijungimas prie Registru Centras Geomatininkas
    driver.get('https://www.registrucentras.lt/ntr/reg.php')
    username=driver.find_element(By.XPATH,'//*[@id="vv"]')
    password=driver.find_element(By.XPATH, '//*[@id="vs"]')

    # Geomatinkas username and password
    username.send_keys("")
    password.send_keys("")   

    driver.find_element("name","login").click()
    driver.find_element("name","confirm_vasu").click()
    driver.find_element("name","login").click()
    driver.get('https://www.registrucentras.lt/usr/login.php?app=GeOO2')
    # print('Prisijunge sekmingai')
    wait = WebDriverWait(driver, 10)
    for x in letters_:
        for i in range(len(x["kad_nr"])):
            # Nekilnojamojo turto paieška žemėlapyje 
            driver.find_element(By.XPATH, '//*[@id="navigationTools_id"]/span/span').click()
            kad = driver.find_element(By.XPATH, '//*[@id="navigationTools_idSearchDialog"]/div/span/input[1]')
            kad.send_keys((x["kad_nr"])[i])
            driver.find_element(By.XPATH, '//*[@id="navigationTools_idSearchDialog_findButton"]/span/span').click()
            time.sleep(1)
            
            clickable = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="map_root"]/div[3]/div[2]')))
            # Zoom 3x NT žemėlapį
            driver.find_element(By.XPATH, '//*[@id="layout"]/div[15]/div[1]/div[2]/a').click()
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="map_zoom_slider"]/tbody/tr[1]/td[2]').click()
            driver.find_element(By.XPATH, '//*[@id="map_zoom_slider"]/tbody/tr[1]/td[2]').click()
            driver.find_element(By.XPATH, '//*[@id="map_zoom_slider"]/tbody/tr[1]/td[2]').click()
            time.sleep(2)

            # Gaunama NT koordinatė
            try:
                ActionChains(driver).move_to_element(clickable).perform()
                ActionChains(driver).move_by_offset(-16, 1).perform()
            except:
                print('Nerado left')
                try:
                    clickable = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="map_root"]/div[3]/div[1]/div[4]')))
                    ActionChains(driver).move_to_element(clickable).perform()    
                    ActionChains(driver).move_by_offset(1, 20).perform()
                except:
                    print('Nerado bottom')  
            
            time.sleep(2)
            coordinates = driver.find_element(By.XPATH, '//*[@id="mapCoordinates"]').text
            # print('Koordinatės: ', coordinates)
            time.sleep(2)
            # Pertvarkomos koordinatės Regia.lt
            xp = coordinates.split()
            s1= round(float(xp[0]))
            s2= round(float(xp[2]))
            s1 = xp[0][:-3]
            s2 = xp[2][:-3]
            new_coord_regia = s1 + xp[1]  + s2
            # print('Pakoreguotos', new_coord_regia)
            # print(x, 'x')
            x["coordinates"].append(str(new_coord_regia))
            time.sleep(1)
    return letters_

def get_regia_adress(letters_,driver):
    # print(letters_, 'Pries regia.lt')
    # Ieškoma adreso regia.lt
    driver.get('https://www.regia.lt/map/regia2')
    time.sleep(4)
    try:
        driver.find_element(By.XPATH, '//*[@id="sluo_id-22"]').click()
    except:
        print("An exception occurred")
    try:  
        e = driver.find_element(By.XPATH, '//*[@id="button-menu"]')
        location = e.location
        s = driver.find_element(By.XPATH, '//*[@id="xyTool-button-xy"]')
        s_location = s.location
    except Exception as e:
        print('Error ', e)
    # print(location, 'location')
    # print(s_location, 's_location')

    for x in letters_:
        for i in range(len(x["coordinates"])):
            driver.find_element(By.XPATH, '//*[@id="xy-box"]').click()
            coord_input = driver.find_element(By.XPATH, '//*[@id="xyTool_dialog_textbox"]')
            # print(x["coordinates"][i])
            coord_input.send_keys(x["coordinates"][i])
            driver.find_element(By.XPATH, '//*[@id="xyTool_dialog_button_find"]/span').click()
            driver.set_window_position(0, 0)
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2) 
            try:
                clickable = driver.find_element(By.XPATH, '//*[@id="xyTool-button-xy"]')
                ActionChains(driver).move_to_element(clickable).perform()
                ActionChains(driver).move_by_offset(585,255).click().perform()
                s = driver.find_element(By.XPATH, '//*[@id="xyTool-button-xy"]')
                s_location = s.location
                time.sleep(3)
            except:
                print('Neranda 165 line')
            try:
                adresas = driver.find_element(By.XPATH, '//*[@id="adr1"]/table/tbody/tr[1]/td[2]').text
                # print(adresas)
                x["sklypo_adresas"].append(str(adresas))
            except:
                print('Nėra adreso, Regia.lt')
                x["sklypo_adresas"].append(0)
    return  letters_


def get_mapslt_adress(letters_,driver):
    print(letters_, 'maps.lt letters_')
    try:
        driver.get('https://beta.maps.lt')
        if driver.find_element(By.XPATH, '/html/body/div[7]/div[2]/div[1]/div[2]/div[2]/button[1]/p'):
            driver.find_element(By.XPATH, '/html/body/div[7]/div[2]/div[1]/div[2]/div[2]/button[1]/p').click()
        for x in letters_:
            for i in range(len(x["coordinates"])):
                if x["sklypo_adresas"][i] == 0:

                    try:
                        ord = driver.find_element(By.XPATH, '//*[@id="widgetsContainer"]/div[2]/div[1]/div/div/div/div/div/div[1]/form/input')
                        ord.send_keys(x["coordinates"][i])
                        time.sleep(3)
                        ord.send_keys(u'\ue007')
                        ord.send_keys(u'\ue007')
                        ord.send_keys(u'\ue007')
                        ord.send_keys(u'\ue007')
                        ord.send_keys(u'\ue007')

                    except:
                        print("Neranda")
                    try:
                        time.sleep(2)
                        # Grazinama koordinate i 0,0 body
                        clickable = driver.find_element(By.XPATH, '/html/body')
                        s_loc = clickable.location
                        # print(s_loc, 'Body location')
                        ActionChains(driver).move_to_element(clickable).perform() 
                        ActionChains(driver).move_by_offset(240, 5).perform()
                        ActionChains(driver).context_click().perform()
                        time.sleep(3)
                        
                        adresas_1 = driver.find_element(By.XPATH,'//*[@id="widgetsContainer"]/div[7]/div/div/div/div[1]/div[1]/div/div/div/a').text 
                        #print(adresas_1, 'adresas 1')
                        adresas_0 = driver.find_element(By.XPATH,'//*[@id="widgetsContainer"]/div[7]/div/div/div/div[1]/div[1]/div/div/div/div').text
                        #print(adresas_0, 'adresas_0')
                        txt_adr_0 = adresas_0.split(',')
                        #print(txt_adr_0, 'txt_adr_0')
                        new_address = '' + txt_adr_0[1] + ', ' + txt_adr_0[0]
                        adresas_m = new_address + ', ' + adresas_1
                        
                        x["sklypo_adresas"][i] = adresas_m
                        time.sleep(2)
                        exit = driver.find_element(By.XPATH, '//*[@id="widgetsContainer"]/div[2]/div[1]/div/div/div/div/div[1]/div[2]/span/span')
                        exit.click()
                    except:
                        print(x["kad_nr"][i], 'Nerado')
                else:
                    print("Neveikia maps.lt", letters_, x["sklypo_adresas"][i])

        return letters_
    except:
        print("Neveikia maps.lt")

    return letters_






