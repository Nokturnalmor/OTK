import io, os, sys, config, telebot, time, copy
from datetime import datetime as Dt
import Cust_Functions as F


Year = Dt.now().year
Cxema = dict()
cfg = config.Config('Config\CFG.cfg') #файл конфига, находится п папке конфиг
put_p = cfg['put_docs'] + '\\' + str(Year)  #путь к документам + папка ГОД
if os.path.exists(put_p) == False: #если нет папки новго года то создать
    os.mkdir(put_p)
put_bd = cfg['BDact']
if  os.path.exists(put_bd + '\\BDact.txt') == False: #если нет файла в году то создать
    with open(put_bd + '\\BDact.txt', 'w') as f:
        f.close()


def ochistit_spisok_Gmenu():                    # созлает список из текстовых файлов как главное меню
    lists = os.listdir('Struct')
    listsr = []
    lists.sort()
    for filek in lists:
        ima, rash = [x for x in filek.split('.')]
        if rash == 'txt':
            listsr.append(ima)

    return listsr


def Poluchit_cxemy(message): #создать словарь для заполенения АКта номер акта и имя ОТК и дата
    # создание схемы
    # Получение номера
    Stroki = F.otkr_f(put_bd + os.sep + 'BDact.txt')
    if len(Stroki) < 1:
        N_act = 0
    else:
        Last_stroka = Stroki[len(Stroki)-1].split("|")
        Nact_s = Last_stroka[0].split(":")
        N_act = int(Nact_s[1])
    Cxema = {"Номер акта": N_act + 1}

    imaOTK = ""
    first_name = ''
    last_names = ''
    if message.from_user.first_name != None:
        first_name = message.from_user.first_name.encode('cp1251', errors='ignore').decode('cp1251')
    if message.from_user.last_name != None:
        last_names = message.from_user.last_name.encode('cp1251', errors='ignore').decode('cp1251')
    username_1 = message.from_user.username
    if first_name != None and first_name != "":
        imaOTK = first_name + " "
    if last_names != None and last_names != "":
        imaOTK = imaOTK + last_names
    if username_1 != None and imaOTK == "":
        imaOTK = username_1
    if imaOTK == "":
        imaOTK = message.from_user.id
    Cxema['Мастер ОТК'] = imaOTK
    del(imaOTK)
    del(first_name)
    del(last_names)
    del(username_1)
    Cxema['Дата'] = Dt.now().strftime("%Y.%m.%d %H:%M")
    for i in ochistit_spisok_Gmenu():
        Cxema[i] = ""
    return Cxema

def otsek(fraza,znach):                             #разбиение названия на 2 части
    arr = [i for i in fraza.split("&")]
    if len(arr) ==2:
        return arr[znach]
    else:
        return fraza

def poisk(data):                            #поиск списка по ключу
    lists = os.listdir('Struct')
    for ima in lists:
        with open("Struct\\" + ima, "r") as file:
            for line in file:
                S = [i.rstrip() for i in line.split("{")]

                if data in S[0]:
                    S2 = [j for j in S[1].split("$")]
                    return S2

def nazad(spisok):                          #возврат по спискам на один уровень
    lists = os.listdir('Struct')
    for ima in lists:
        with open("Struct\\" + ima, "r") as file:
            for line in file:
                S = [i for i in line.split("{")]
                if spisok in S[1]:
                    with open("Struct\\" + ima, "r") as file:
                        for line in file:
                            S2 = [j for j in line.split("{")]
                            if S[0] in S2[1]:
                                S3 = [k for k in S2[1].split("$")]
                                return S3

def viviod_slovara(slovar):
    S = []
    for key, value in slovar.items():
        if "Выход" not in key:
            S.append(otsek(key,1) + ":  " + str(value))
            S2 = ("\n   ").join(S)
    return S2

def viviod_slovara_v_BD(slovar):
    S = []
    for key, value in slovar.items():
        if "Выход" not in key:
            S.append(otsek(key,1) + ":" + str(value).replace("\n"," ").strip())
            S2 = ("|").join(S)
    return S2

def get_podmenu(spisok,message):                #Вывод подменю
    keyboard = telebot.types.InlineKeyboardMarkup()
    global Musor
    for ima in spisok:
        keyboard.row(
            telebot.types.InlineKeyboardButton(otsek(ima,1), callback_data=ima)
        )
    tmp_msg_id = bot.send_message(
        message.chat.id, viviod_slovara(Cxema) + '\n' + """\
                                    Выбери категорию.\
                                    """ + '\n' +  otsek(kategoria_gl_menu,1),
        reply_markup=keyboard
    )
    Musor.add(tmp_msg_id.message_id)

def get_ruchnoi_vvod(message, data):
    global ruchnoi_vvod_flag
    global Musor
    ruchnoi_vvod_flag = data
    tmp_msg_id = bot.send_message(message.chat.id, otsek(data,1) +". Введи данные:")
    Musor.add(tmp_msg_id.message_id)

def Zapis_cxemi(Cxema):
    Stroki = F.otkr_f(put_bd + os.sep + 'BDact.txt')
    Stroki.append(viviod_slovara_v_BD(Cxema))
    F.zap_f(put_bd + os.sep + 'BDact.txt',Stroki)
    return


def spis_act_po_mk_id_op(mk, id, spis_op):
    sp = []
    nar = F.otkr_f(F.tcfg('Naryad'), False, '|')
    sp_act = F.otkr_f(F.tcfg('BDact'),False,'|')
    for i in range(1, len(nar)):
        if nar[i][1].strip() == str(mk) and nar[i][25].strip() == str(id) and nar[i][24].strip() in spis_op:
            for j in range(len(sp_act)):
                if sp_act[j][3] == 'Номер наряда:' + nar[i][0].strip():
                    sost = ''
                    if '(Исправлен по наряду №' in sp_act[j][7]:
                        sost = 'Исправлен'
                    elif sp_act[j][6] == 'Категория брака:Неисправимый':
                        if '(Изгот.вновь по МК №' in sp_act[j][7]:
                            sost = 'Изгот.вновь'
                        else:
                            sost = 'Неисп-мый'
                    nom_acta = sp_act[j][0].replace('Номер акта:','')
                    sp.append(nom_acta + ' ' + sost)
    return sp


def otmetka_v_mk(nom, spis_op, sp_nar, id, sp_tabl_mk):
    for j in range(1, len(sp_tabl_mk)):
        if sp_tabl_mk[j][6] == id:
            for i in range(11, len(sp_tabl_mk[0]), 4):
                if sp_tabl_mk[j][i].strip() != '':
                    obr = sp_tabl_mk[j][i].strip().split('$')
                    obr2 = obr[-1].split(";")
                    if spis_op == obr2:
                        text = '$'.join(sp_nar)
                        sp_tabl_mk[j][i + 3] = text
                        F.zap_f(F.scfg('mk_data') + os.sep + nom + '.txt', sp_tabl_mk, '|')
                        return


def spis_op_po_mk_id_op(sp_tabl_mk, id, op):
    for j in range(1, len(sp_tabl_mk)):
        if sp_tabl_mk[j][6] == id:
            for i in range(11, len(sp_tabl_mk[0]), 4):
                if sp_tabl_mk[j][i].strip() != '':
                    obr = sp_tabl_mk[j][i].strip().split('$')
                    obr2 = obr[-1].split(";")
                    if op in obr2:
                        return obr2
            return None


def zapis_v_mk(Cxema,message,proverka):
    tek_nar = Cxema['1&Номер наряда']
    sp_nar = F.otkr_f(F.tcfg('Naryad'), False, '|')
    nom_mk = F.naiti_v_spis_1_1(sp_nar, 0, tek_nar, 1)
    if nom_mk == None:
        Cxema['1&Номер наряда'] = ''
        return "Наряд номер " + tek_nar + " отсутствует, введи правильный номер"
    id_det = F.naiti_v_spis_1_1(sp_nar, 0, tek_nar, 25)
    n_op = F.naiti_v_spis_1_1(sp_nar, 0, tek_nar, 24)
    if F.nalich_file(F.scfg('mk_data') + os.sep + nom_mk + '.txt') == False:
        print('Не обнаружен файл mk_data')
        return 'Не обнаружен файл mk_data'
    sp_tabl_mk = F.otkr_f(F.scfg('mk_data') + os.sep + nom_mk + '.txt', False, '|')
    if sp_tabl_mk == []:
        print('Некорректное содержимое МК ' + nom_mk)
        return 'Некорректное содержимое МК ' + nom_mk
    spis_op = spis_op_po_mk_id_op(sp_tabl_mk, id_det, n_op)
    if spis_op == None:
        print('Некорректное содержимое списка операций ' + id_det + ' ' + sp_tabl_mk)
        return 'Некорректное содержимое списка операций ' + id_det + ' ' + sp_tabl_mk
    if proverka == True:
        return
    spis_act_mk = spis_act_po_mk_id_op(nom_mk, id_det, spis_op)
    otmetka_v_mk(nom_mk, spis_op, spis_act_mk, id_det, sp_tabl_mk)




def get_akt(N_akt): #вывод списка смхемы акта по номеру акта
    with open(put_bd + '\\BDact.txt', 'r') as file:
        for line in file:
            spst = [x for x in line.split('|')]
            Nn = [v for v in spst[0].split(':')]
            if Nn[1] == N_akt:
                spisok = ''
                for i in spst:
                    spisok = spisok + i + "\n"
                return spisok
    return "Не найден акт №" + str(N_akt)

def get_foto_po_akt(spisok): #вывод списка имен фоток по списку схемы акта
    sp = [x for x in spisok.split("\n")]
    for elem in sp:
        if "Фото:" in elem:
            sp2 = [z for z in elem.split(":")]
            sp_fot = sp2[1][1:-1]
            spisok_fot = [v for v in sp_fot.split(')(')]
            return spisok_fot


def get_spispok_aktov(): #вывод словаря акты : дата и вид брака
    global Musor
    spis = dict()
    sp_dl_rev = []
    with open(put_bd + '\\BDact.txt', 'r') as file:
        for line in file:
            temp_sp = []
            spst = [x for x in line.split('|')]
            temp_sp.append(spst[2])
            temp_sp.append(spst[5])
            Nn = [v for v in spst[0].split(':')]
            spis[Nn[1]] = temp_sp
            sp_dl_rev.append(Nn[1])
    sp_dl_rev.reverse()
    newdict = {}
    if len(sp_dl_rev) < 4:
        predel = len(sp_dl_rev)
    else:
        predel = 5
    for s in range(0,predel):
        newdict[sp_dl_rev[s]] = spis[sp_dl_rev[s]]
    return newdict


def get_iq_articles(exchanges):  # обработка для вывода в другой чат
    result = []
    for exc in exchanges.keys():
        it1 = exchanges[exc][0]
        it2 = exchanges[exc][1]
        result.append(
            telebot.types.InlineQueryResultArticle(
                id=exc,
                title="Акт №" + exc,
                input_message_content=telebot.types.InputTextMessageContent(
                    get_akt(exc),
                    parse_mode='HTML' #'Markdown'  # 'HTML'
                ),
                # reply_markup="",
                description=it1 + " " + it2,
                # thumb_url = "D:/Python/OTK/Config/docs/2020/16_14_19_34_069609.jpg"
            )
        )
    return result

def ochistka_soob(chat_id,Mnogestvo_msg_id,vid):
    global Musor
    try:
        for item in Mnogestvo_msg_id:
            bot.delete_message(chat_id, item)  # удаление сообщения
    except:
        print("Ошибка в чистке мусора" + str(item) + '{' + str(vid))
    finally:
        Musor.clear()
    return

for popitka in range(1, 2999):
    time.sleep(2)
    try:
        bot = telebot.TeleBot(cfg['token'])
        if cfg['prx'] != "":
            telebot.apihelper.proxy = {'https': cfg['prx']}
        kategoria_gl_menu = ""
        ruchnoi_vvod_flag = ""
        prinyat_foto_flag = ""
        parol_vvod_flag = ""
        Musor = set()
        time.sleep(2)

        print(time.ctime())
        print('Попытка ' + str(popitka))
        print("Соединение... " + str(telebot.apihelper.proxy), end='\n')


        @bot.message_handler(content_types=['photo'])
        def handle_docs_photo(message):  # тест сохранения картинки
            global prinyat_foto_flag
            global Musor
            if prinyat_foto_flag != "":
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                Vrem_metka = Dt.now().strftime("%H_%M_%S_%f")
                src = put_p + '\\' + str(Cxema["Номер акта"]) + "_" + Vrem_metka + ".jpg"
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                Cxema[kategoria_gl_menu] = Cxema[kategoria_gl_menu] + "(" + str(Cxema["Номер акта"]) + "_" + Vrem_metka + ".jpg" + ")"
                prinyat_foto_flag = ""
                Musor.add(message.message_id)
                ochistka_soob(message.chat.id,Musor,1)
                #bot.delete_message(message.chat.id, message.message_id)  # удаление сообщения
                #bot.delete_message(message.chat.id, message.message_id-1)  # удаление сообщения
                get_menu(message)
                return


        @bot.callback_query_handler(func=lambda call: True) #обработка ответа
        def iq_callback(query):
            global Musor
            data = query.data
            #bot.answer_callback_query(callback_query_id=query.id, text="Акт зарегистрирован.")
            #bot.answer_callback_query(query.id)
            #bot.send_chat_action(query.message.chat.id, 'typing')
            if data in ochistit_spisok_Gmenu():
                global kategoria_gl_menu
                kategoria_gl_menu = copy.deepcopy(data)

            spisok = poisk(data)
            Musor.add(query.message.message_id)
            ochistka_soob(query.message.chat.id,Musor,2)
            if data.startswith('get_menu'):
                global Cxema
                Cxema = Poluchit_cxemy(query.message)
                #bot.delete_message(query.message.chat.id, query.message.message_id)  # удаление сообщения
                #bot.delete_message(query.message.chat.id, query.message.message_id-1)  # удаление сообщения
                get_menu(query.message)
            elif otsek(data,1) == 'Выход':
                #bot.delete_message(query.message.chat.id, query.message.message_id)  # удаление сообщения
                #bot.delete_message(query.message.chat.id, query.message.message_id - 1)  # удаление сообщения
                Cxema.clear()
                time.sleep(1)
                #raise Exception('Моё исключение')
                ochistka_soob(query.message.chat.id, Musor,3)
            elif spisok != None:
                if len(spisok) == 1:
                    if otsek(spisok[0],0) == "END": #обработка итогов
                        if Cxema[kategoria_gl_menu] != '':
                            Cxema[kategoria_gl_menu] = Cxema[kategoria_gl_menu]  + ";"
                        Cxema[kategoria_gl_menu] = Cxema[kategoria_gl_menu] + otsek(data,1)
                        kategoria_gl_menu = ""
                        #bot.delete_message(query.message.chat.id, query.message.message_id)  # удаление сообщения
                        get_menu(query.message)
                    elif otsek(spisok[0],0) == "NUM": #обработка ручного ввода
                        #bot.delete_message(query.message.chat.id, query.message.message_id)  # удаление сообщения
                        get_ruchnoi_vvod(query.message,data)
                    elif otsek(spisok[0], 0) == "BACK": #обработка кнопки назад
                        spisok.clear()
                        spisok= nazad(data)
                        #bot.delete_message(query.message.chat.id, query.message.message_id)  # удаление сообщения
                        if spisok == None:
                            get_menu(query.message)
                        else:
                            get_podmenu(spisok, query.message)
                    elif otsek(spisok[0], 0) == "FOTO":  # обработка кнопки назад
                        global prinyat_foto_flag
                        prinyat_foto_flag = data
                        #bot.delete_message(query.message.chat.id, query.message.message_id)  # удаление сообщения
                        tmp_msg_id = bot.send_message(query.message.chat.id, "Отправь фото:")
                        Musor.add(tmp_msg_id.message_id)

                else:
                    #bot.delete_message(query.message.chat.id, query.message.message_id)  # удаление сообщения
                    get_podmenu(spisok,query.message)
            else:
                zaglushka(query.message)

        def zaglushka(message):
            global Musor
            tmp_msg_id = bot.send_message(message.chat.id, "Не верная категория.")
            Musor.add(tmp_msg_id.message_id)

        def get_menu(message):                          #вывод меню
            global Musor
            keyboard = telebot.types.InlineKeyboardMarkup()
            files = ochistit_spisok_Gmenu()

            Spisok_zapolnenia = []
            for ima in files:
                if Cxema[ima] == "" or "+" in ima :
                    Spisok_zapolnenia.append(ima)
                    keyboard.row(
                        telebot.types.InlineKeyboardButton(otsek(ima,1), callback_data=ima)
                    )
            flag_plus = 1
            for ima in Spisok_zapolnenia:
                if "+" not in ima:
                    flag_plus = 0
                    break
            if flag_plus == 1:

                rezult = zapis_v_mk(Cxema,message,True)
                if rezult != None:
                    bot.send_message(
                        message.chat.id, rezult)
                    get_menu(message)
                    return
                Zapis_cxemi(Cxema)
                zapis_v_mk(Cxema, message, False)
                user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
                user_markup.row('/start')
                bot.send_message(
                    message.chat.id, "Акт " + str(Cxema['Номер акта']) + " успешно зарегистрирован.", reply_markup=user_markup)
                Cxema.clear()
                #raise Exception('Моё исключение')
                return

            tmp_msg_id = bot.send_message(
                message.chat.id,viviod_slovara(Cxema) + '\n' + """\
                                    Выбери категорию.\
                                    """ + '\n' +  otsek(kategoria_gl_menu,1),
                reply_markup=keyboard
            )
            Musor.add(tmp_msg_id.message_id)


            # Handle '/start' and '/help'
        @bot.message_handler(commands=['start'])
        def start_message(message):
            global Musor
            global parol_vvod_flag
            user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
            user_markup.row('/start')
            parol_vvod_flag = 1
            ima = cfg['ima']
            tmp_msg_id = bot.send_message(message.from_user.id,'Привет, я ' + ima + 'ОТК бот. Я нужен, чтобы \
            регистрировать и просматривать акты о браке. Просто введи без кавычек <<пароль акт номер>> для просмотра, пример: \
            <<qwerty акт 123>> или для регистрации нового акта введи только пароль:', reply_markup=user_markup)
            Musor.add(tmp_msg_id.message_id)

            #keyboard = telebot.types.InlineKeyboardMarkup()
            #keyboard.row(
            #    telebot.types.InlineKeyboardButton('Начать', callback_data='get_menu')
            #)
            #bot.send_message(
            #    message.chat.id, """\
            #        Добрый день, я ОТК бот
            #        Я нужен чтобы регистрировать случаи брака. Просто нажми кнопку <начать> для регистрации акта.\
            #        """,
            #    reply_markup = keyboard
            #)


        @bot.inline_handler(func=lambda query: True) #обработка запроса с другого чата
        def query_text(inline_query):
            #if 'акт' in inline_query.query and inline_query.query[-1] == '.':
                #bot.send_photo(inline_query.id,open('D:\\Python\\OTK\\Config\\docs\\2020\\16_14_19_34_069609.jpg', 'rb'))
                bot.answer_inline_query(
                    inline_query.id,
                    get_iq_articles(get_spispok_aktov())
                )

        @bot.message_handler(content_types=['text'])
        def send_text(message):
            global Musor
            global parol_vvod_flag
            global ruchnoi_vvod_flag
            Musor.add(message.message_id)
            ochistka_soob(message.chat.id, Musor,4)
            if parol_vvod_flag != None and parol_vvod_flag != "":
                if "акт " in message.text.lower():
                    with open(cfg['identp']+ '\\r.txt', 'r') as file:
                        for line in file:
                            par_r = line
                            break
                    sost_soob = [x for x in message.text.lower().split(' ')]
                    if len(sost_soob) == 3 and sost_soob[0] == par_r and sost_soob[1] == 'акт':
                        N_acta = sost_soob[2]
                        tmp_msg_id = bot.send_message(message.from_user.id, get_akt(N_acta))
                        Musor.add(tmp_msg_id.message_id)
                        if "Не найден акт" not in get_akt(N_acta):
                            for elem in get_foto_po_akt(get_akt(N_acta)):
                                if elem != '' and elem != None:
                                    if os.path.exists(put_p + '\\' + elem):
                                        tmp_msg_id = bot.send_photo(message.chat.id,open(put_p + '\\' + elem, 'rb'))
                                        Musor.add(tmp_msg_id.message_id)
                    else:
                        #bot.delete_message(message.chat.id, message.message_id)  # удаление сообщения
                        tmp_msg_id = bot.send_message(message.from_user.id, """Пароль не верный. Введи номер акта для просмотра, пример: "пароль акт 123":""")
                        Musor.add(tmp_msg_id.message_id)
                else:
                    with open(cfg['identp']+ '\\w.txt', 'r') as file:
                        for line in file:
                            par_w = line
                            break
                    if par_w == message.text:
                        parol_vvod_flag = None
                        #bot.delete_message(message.chat.id, message.message_id - 1)  # удаление сообщения
                        #bot.delete_message(message.chat.id, message.message_id)  # удаление сообщения
                        global Cxema
                        Cxema = Poluchit_cxemy(message)
                        get_menu(message)
                    else:
                        #bot.delete_message(message.chat.id, message.message_id - 1)  # удаление сообщения
                        #bot.delete_message(message.chat.id, message.message_id)  # удаление сообщения
                        tmp_msg_id = bot.send_message(message.from_user.id,"""Пароль не верный. Введи пароль:""")
                        Musor.add(tmp_msg_id.message_id)
            if ruchnoi_vvod_flag != None and ruchnoi_vvod_flag != "":
                global kategoria_gl_menu
                if len(Cxema) == 0:
                    Cxema = Poluchit_cxemy(message)
                    get_menu(message)
                    return
                if Cxema[kategoria_gl_menu] != '':
                    Cxema[kategoria_gl_menu] = Cxema[kategoria_gl_menu] + ";"
                Cxema[kategoria_gl_menu] = Cxema[kategoria_gl_menu] + message.text
                kategoria_gl_menu = ""
                ruchnoi_vvod_flag = ''
                #bot.delete_message(message.chat.id, message.message_id-1)  # удаление сообщения
                #bot.delete_message(message.chat.id, message.message_id)  # удаление сообщения
                get_menu(message)
                return



        print("Соединено")
        time.sleep(1)
        bot.polling(none_stop = True)

    except:
        print("Ожидание")
        time.sleep(5)
