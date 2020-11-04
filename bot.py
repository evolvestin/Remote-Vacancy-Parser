import os
import re
import sys
import objects
import _thread
import gspread
import telebot
import requests
import traceback
import unicodedata
from PIL import Image
from time import sleep
from telebot import types
from PIL import ImageFont
from PIL import ImageDraw
from telegraph import upload
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode
from collections import defaultdict

stamp1 = int(datetime.now().timestamp())
objects.environmental_files()
client2 = gspread.service_account('person2.json')
used = client2.open('growing').worksheet('main')
used_array = used.col_values(1)

keyboard = types.InlineKeyboardMarkup(row_width=2)
buttons = [types.InlineKeyboardButton(text='✅', callback_data='post'),
           types.InlineKeyboardButton(text='👀', callback_data='viewed')]
starting = ['title', 'place', 'tags', 'geo', 'money', 'org_name', 'schedule', 'employment', 'short_place',
            'experience', 'education', 'contact', 'numbers', 'description', 'email', 'metro']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}

font = ImageFont.truetype('Roboto-Light.ttf', 80)
idMain = -1001272631426
keyboard.add(*buttons)
original_width = 1100
idAndre = 470292601
color = (0, 0, 0)
idMe = 396978030
idJobi = idMe
# =================================================================


def bold(txt):
    return '<b>' + txt + '</b>'


def code(txt):
    return '<code>' + txt + '</code>'


def italic(txt):
    return '<i>' + txt + '</i>'


def printer(printer_text):
    thread_name = str(thread_array[_thread.get_ident()]['name'])
    logfile = open('log.txt', 'a')
    log_print_text = thread_name + ' [' + str(_thread.get_ident()) + '] ' + printer_text
    logfile.write('\n' + re.sub('<.*?>', '', logtime(0)) + log_print_text)
    logfile.close()
    print(log_print_text)


def send_json(raw, name, error):
    json_text = ''
    if type(raw) is str:
        for character in raw:
            replaced = unidecode(str(character))
            if replaced != '':
                json_text += replaced
            else:
                try:
                    json_text += '[' + unicodedata.name(character) + ']'
                except ValueError:
                    json_text += '[???]'
    if len(error) <= 1000:
        if json_text != '':
            docw = open(name + '.json', 'w')
            docw.write(json_text)
            docw.close()
            doc = open(name + '.json', 'rb')
            bot.send_document(idMe, doc, caption=error)
            doc.close()
        else:
            bot.send_message(idMe, error, parse_mode='HTML')
    if len(error) > 1000 and len(error) <= 4000:
        bot.send_message(idMe, error)
    if len(error) > 4000:
        separator = 4000
        splited_sep = len(error) // separator
        splited_mod = len(error) / separator - len(error) // separator
        if splited_mod != 0:
            splited_sep += 1
        for i in range(0, splited_sep):
            splited_error = error[i * separator:(i + 1) * separator]
            if len(splited_error) > 0:
                bot.send_message(idMe, splited_error, parse_mode='HTML')


def executive(new, logs):
    search = re.search('<function (\S+)', str(new))
    if search:
        name = search.group(1)
    else:
        name = 'None'
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_raw = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error = 'Вылет ' + name + '\n'
    for i in error_raw:
        error += re.sub('<', '&#60;', str(i))
    send_json(logs, name, error)
    if logs == 0:
        sleep(100)
        thread_id = _thread.start_new_thread(new, ())
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = name
        thread_array[thread_id]['function'] = new
        bot.send_message(idMe, 'Запущен ' + bold(name), parse_mode='HTML')
        sleep(30)
        _thread.exit()


def logtime(stamp):
    if stamp == 0:
        stamp = int(datetime.now().timestamp())
    weekday = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%a')
    if weekday == 'Mon':
        weekday = 'Пн'
    elif weekday == 'Tue':
        weekday = 'Вт'
    elif weekday == 'Wed':
        weekday = 'Ср'
    elif weekday == 'Thu':
        weekday = 'Чт'
    elif weekday == 'Fri':
        weekday = 'Пт'
    elif weekday == 'Sat':
        weekday = 'Сб'
    elif weekday == 'Sun':
        weekday = 'Вс'
    day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
    month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
    year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
    hours = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%H')
    minutes = datetime.utcfromtimestamp(int(stamp)).strftime('%M')
    seconds = datetime.utcfromtimestamp(int(stamp)).strftime('%S')
    data = code(str(weekday) + ' ' + str(day) + '.' + str(month) + '.' + str(year) +
                ' ' + str(hours) + ':' + str(minutes) + ':' + str(seconds)) + ' '
    return data


logfile_start = open('log.txt', 'w')
logfile_start.write('Начало записи лога ' + re.sub('<.*?>', '', logtime(0)))
logfile_start.close()

bot = telebot.TeleBot(os.environ['TOKEN'])
start_message = bot.send_message(idMe, logtime(stamp1) + '\n' + logtime(0), parse_mode='HTML')
# ====================================================================================


def width(row_text):
    size = ImageFont.ImageFont.getsize(font, row_text)
    text_width = size[0][0]
    return text_width


def image(image_text):
    left = 50
    img = Image.open('bot.png')
    draw = ImageDraw.Draw(img)
    if width(image_text) <= original_width:
        left += (original_width - width(image_text)) // 2
        draw.text((left, 250), image_text, color, font)
    else:
        temp_text_array = re.sub('\s+', ' ', image_text.strip()).split(' ')
        layer = 1
        while layer <= 3:
            drop_text = ''
            clearer = 0
            for i in temp_text_array:
                if width((drop_text + ' ' + i).strip()) <= original_width:
                    drop_text = (drop_text + ' ' + i).strip()
                    clearer += 1
                else:
                    break
            for i in range(0, clearer):
                temp_text_array.pop(0)
            if len(drop_text) != 0:
                text_position = (left + (original_width - width(drop_text)) // 2, 172 + 78 * layer)
                draw.text(text_position, drop_text, color, font)
            layer += 1
    img.save('bot_edited.jpg')
    doc = open('bot_edited.jpg', 'rb')
    uploaded = upload.upload_file(doc)
    uploaded_link = '<a href="https://telegra.ph' + uploaded[0] + '">​​</a>️'
    return uploaded_link


def tut_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    title = soup.find('div', class_='vacancy-title')
    if title is not None:
        if title.find('h1') is not None:
            tag = ''
            headline = re.sub('\s+', ' ', title.find('h1').get_text())
            growing['title'] = headline
            headline = re.sub('\(.*?\)|[.,/]|г\.', '', headline.lower())
            headline = re.sub('e-mail', 'email', re.sub('\s+', ' ', headline))
            headline = re.sub('[\s-]', '_', headline.strip().capitalize())
            for i in re.split('(_)', headline):
                if len(tag) <= 20:
                    tag += i
            if tag.endswith('_'):
                tag = tag[:-1]
            growing['tags'] = [tag]

    place = soup.find('div', class_='vacancy-address-text')
    if place is not None:
        metro = ''
        metro_array = place.find_all('span', class_='metro-station')
        for i in metro_array:
            metro += re.sub('\s+', ' ', i.get_text().strip() + ', ')
        if metro != '':
            growing['metro'] = metro[:-2]
        growing['place'] = re.sub(metro, '', re.sub('\s+', ' ', place.get_text()).strip())

    short_place = soup.find_all('span')
    if short_place is not None:
        for i in short_place:
            if str(i).find('vacancy-view-raw-address') != -1:
                search = re.search('<!-- -->(.*?)<!-- -->', str(i))
                if search:
                    growing['short_place'] = re.sub('\s+', ' ', search.group(1).capitalize().strip())
                    break
        if growing['short_place'] == 'none':
            short_place = soup.find('div', class_='vacancy-company')
            if short_place is not None:
                short_place = short_place.find('p')
                if short_place is not None:
                    growing['short_place'] = re.sub('\s+', ' ', short_place.get_text().capitalize().strip())

    geo_search = re.search('{"lat": (.*?), "lng": (.*?), "zoom"', str(soup))
    if geo_search:
        growing['geo'] = re.sub('\s', '', geo_search.group(1)) + ',' + re.sub('\s', '', geo_search.group(2))

    money = soup.find('p', class_='vacancy-salary')
    if money is not None:
        money_array = []
        money = re.sub('\s', '', money.get_text().lower())
        search_ot = re.search('от(\d+)', money)
        search_do = re.search('до(\d+)', money)
        if search_do:
            money_array.append(search_do.group(1))
            money_array.append('none')
        elif search_ot:
            money_array.append(search_ot.group(1))
            money_array.append('more')
        else:
            money_array = 'none'
        growing['money'] = money_array

    org_name = soup.find('a', {'data-qa': 'vacancy-company-name'})
    if org_name is not None:
        growing['org_name'] = re.sub('\s+', ' ', org_name.get_text().strip())

    description = soup.find('div', class_='g-user-content')
    if description is not None:
        description = description.find_all(['p', 'ul', 'strong'])
        tempering = []
        main = ''
        prev = ''
        for i in description:
            text = ''
            lists = i.find_all('li')
            if len(lists) != 0:
                for g in lists:
                    text += '🔹 ' + re.sub('\n', '', g.get_text().capitalize()) + '\n'
            else:
                temp = i.get_text().strip()
                if prev != temp:
                    if temp.endswith(':'):
                        text += '\n✅ ' + bold(temp) + '\n'
                    else:
                        tempering.append(temp)
                prev = temp
            main += text
        main = main[:-1]
        if len(tempering) > 0:
            main += '\n\n'
        for i in tempering:
            main += i + '\n'
        growing['description'] = main

    numbers = ''
    items = soup.find_all(['p', 'a', 'span'])
    for i in items:
        search = re.search('data-qa="vacancy-view-employment-mode"', str(i))
        if search:
            schedule_text = ''
            schedule = i.find('span')
            if schedule is not None:
                schedule_text = re.sub('\s+', ' ', schedule.get_text().strip())
                growing['schedule'] = re.sub('график', '', schedule_text).strip().capitalize()
            employment = re.sub('\s+', ' ', i.get_text().lower())
            employment = re.sub(',|занятость|' + schedule_text, '', employment).strip().capitalize()
            growing['employment'] = employment

        search = re.search('data-qa="vacancy-experience"', str(i))
        if search:
            growing['experience'] = re.sub('\s+', ' ', i.get_text().strip())

        search = re.search('data-qa="vacancy-contacts__fio"', str(i))
        if search:
            growing['contact'] = re.sub('\s+', ' ', i.get_text().strip())

        search = re.search('data-qa="vacancy-contacts__email"', str(i))
        if search:
            growing['email'] = re.sub('\s+', ' ', i.get_text().strip())

        search = re.search('data-qa="vacancy-contacts__phone"', str(i))
        if search:
            if numbers.find(re.sub('\s+', ' ', i.get_text().strip())) == -1:
                numbers += re.sub('\s+', ' ', i.get_text().strip()) + '\n'
    if numbers != '':
        growing['numbers'] = numbers[:-1]
    return [pub_link, growing]


def former(growing, kind, pub_link):
    text = ''
    if growing['title'] != 'none':
        text_to_image = re.sub('\(.*?\)|[.,]|г\.', '', growing['title'])
        text_to_image = re.sub('e-mail', 'email', re.sub('\s+', ' ', text_to_image))
        text = image(re.sub('[\s-]', ' ', text_to_image.strip()))
        text += '👨🏻‍💻 ' + bold(growing['title']) + '\n'
    if growing['short_place'] != 'none':
        text += '🏙 ' + growing['short_place'] + '\n'
    if growing['experience'] != 'none':
        text += '🏅 Опыт работы ➡ ' + growing['experience'].capitalize() + '\n'
    if growing['education'] != 'none':
        text += '👨‍🎓 Образование ➡ ' + growing['education'].capitalize() + '\n'
    if growing['money'] != 'none':
        more = ''
        if growing['money'][1] != 'none':
            more += '+'
        text += '💸 ' + bold('З/П ') + growing['money'][0] + more + ' руб.' + '\n'
    if growing['description'] != 'none':
        text += '{}\n'
    text += bold('\n📔 Контакты\n')
    if growing['org_name'] != 'none':
        text += growing['org_name'] + '\n'
    if growing['contact'] != 'none':
        text += growing['contact'] + '\n'
    if growing['numbers'] != 'none':
        text += growing['numbers'] + '\n'
    if growing['email'] != 'none':
        text += growing['email'] + ' ➡ Резюме\n'
    if growing['place'] != 'none':
        text += bold('\n🏘 Адрес\n') + growing['place'] + '\n'
    if growing['metro'] != 'none':
        text += '🚇 ' + growing['metro'] + '\n'
    if growing['geo'] != 'none':
        text += '\n📍 <a href="http://maps.yandex.ru/?text=' + growing['geo'] + '">На карте</a>\n'

    text += '\n🔎 <a href="' + pub_link + '">Источник</a>\n'

    if growing['tags'] != 'none':
        text += italic('\n💼ТЕГИ: ')
        for i in growing['tags']:
            text += '#' + i + ' '
        text = text[:-1] + '\n'

    if growing['description'] != 'none':
        len_text = 4094 - len(text)
        if len_text - len(growing['description']) >= 0:
            text = text.format(growing['description'])
        else:
            text = text.format(growing['description'][:len_text])

    return [text, None, image(growing['title'])]


def poster(id_forward, array, pub_link):
    if array[0] is not None:
        if array[0] != pub_link:
            notify = None
            hours = int(datetime.utcfromtimestamp(int(datetime.now().timestamp() + 3 * 60 * 60)).strftime('%H'))
            if hours > 21 and hours < 8:
                notify = True
            bot.send_message(id_forward, array[0], reply_markup=array[1], parse_mode='HTML',
                             disable_web_page_preview=False, disable_notification=notify)
        else:
            bot.send_message(idMe, 'Что-то пошло не так:\n' + pub_link, parse_mode='HTML',
                             disable_web_page_preview=False)
    else:
        if id_forward != idMain:
            send = id_forward
        else:
            send = idMe
        bot.send_message(send, 'Что-то пошло не так:\n' + pub_link, parse_mode='HTML', disable_web_page_preview=False)


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    try:
        if call.data == 'post':
            search = re.search('🔎(.*?)🔎', call.message.text)
            if search:
                site_search = re.search('tut\.by|hh\.ru', search.group(1))
                if site_search:
                    post = tut_quest(search.group(1))
                    poster(idMain, former(post[1], 'MainChannel', post[0]), post[0])
                    text = call.message.text + code('\n✅ опубликован ✅')
                    bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                                          reply_markup=None, parse_mode='HTML', disable_web_page_preview=True)
                else:
                    send_json(call.message.text, 'callbacks', code('Не нашел в посте ссылку на вакансию'))
            else:
                send_json(call.message.text, 'callbacks', code('Не нашел в посте ссылку на вакансию'))

        elif call.data == 'viewed':
            text = call.message.text + code('\n👀 просмотрен 👀')
            bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                                  reply_markup=None, parse_mode='HTML', disable_web_page_preview=True)
    except IndexError and Exception:
        executive(callbacks, str(call))


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id == idMe or message.chat.id == idAndre:
            if message.text.startswith('https://'):
                site_search = re.search('tut\.by|hh\.ru', message.text)
                if site_search:
                    post = tut_quest(message.text)
                    poster(message.chat.id, former(post[1], 'Private', post[0]), post[0])
                else:
                    bot.send_message(message.chat.id, bold('ссылка не подошла, пошел нахуй'), parse_mode='HTML')
            elif message.text.startswith('/pic'):
                subbed = re.sub('/pic', '', message.text).strip()
                bot.send_message(message.chat.id, image(subbed), parse_mode='HTML')
            elif message.text.startswith('/base'):
                doc = open('log.txt', 'rt')
                bot.send_document(message.chat.id, doc)
                doc.close()
            else:
                bot.send_message(message.chat.id, bold('ссылка не подошла, пошел нахуй'), parse_mode='HTML')
    except IndexError and Exception:
        executive(repeat_all_messages, str(message))


def checker(adress, main_sep, link_sep, quest):
    global used
    global client2
    global used_array
    sleep(3)
    text = requests.get(adress, headers=headers)
    soup = BeautifulSoup(text.text, 'html.parser')
    posts_raw = soup.find_all('div', class_=main_sep)
    posts = []
    for i in posts_raw:
        link = i.find('a', class_=link_sep)
        if link is not None:
            posts.append(link.get('href'))
    for i in posts:
        if i not in used_array:
            try:
                used.insert_row([i], 1)
            except:
                client2 = gspread.service_account('person2.json')
                used = client2.open('growing').worksheet('main')
                used.insert_row([i], 1)
            used_array.insert(0, i)
            post = quest(i)
            poster(idMain, former(post[1], 'MainChannel', post[0]), post[0])
            printer(i + ' сделано')
            sleep(3)


def tut_checker():
    while True:
        try:
            checker('https://jobs.tut.by/search/vacancy?order_by=publication_time&clusters=true&area=16&'
                    'currency_code=BYR&enable_snippets=true&only_with_salary=true&schedule=remote', 'vacancy-serp-item',
                    'bloko-link', tut_quest)
        except IndexError and Exception:
            executive(tut_checker, 0)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        bot.stop_polling()
        sleep(1)
        telepol()


if __name__ == '__main__':
    gain = [tut_checker]
    thread_array = defaultdict(dict)
    for i in gain:
        thread_id = _thread.start_new_thread(i, ())
        thread_start_name = re.findall('<.+?\s(.+?)\s.*>', str(i))
        thread_array[thread_id] = defaultdict(dict)
        thread_array[thread_id]['name'] = thread_start_name[0]
        thread_array[thread_id]['function'] = i
    telepol()
