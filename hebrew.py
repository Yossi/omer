#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import render_template # pip install flask
from Yom import yom # creates just the "hayom...laomer" line
import yaml

def hebrew_numeral(val, gershayim=True):
    hsn = yaml.load(open('data/hebrew-special-numbers/styles/default.yml', encoding="utf8"))

    def add_gershayim(s):
        if len(s) == 1:
            return s + hsn['separators']['geresh']
        else:
            return ''.join([s[:-1], hsn['separators']['gershayim'], s[-1:]])

    if val in hsn['specials']:
        retval = hsn['specials'][val]
        return add_gershayim(retval) if gershayim else retval

    parts = []
    rest = str(val)
    l = len(rest) - 1
    for n, d in enumerate(rest):
        digit = int(d)
        if digit == 0: continue
        power = 10 ** (l-n)
        parts.append(hsn['numerals'][power * digit])
    retval = ''.join(parts)

    return add_gershayim(retval) if gershayim else retval

def textforday(day, times=''):
    if day not in range(1,50):
        return render_template('error.html', day=day)

    special = {15: u"א' דראש חודש אייר",
               16: u"ב' דראש חודש אייר",
               29: u'פסח שני‎',
               33: u'ל״ג בעומר',
               45: u'ראש חודש סיון'}

    tzeit = u'צאת הכוכבים׃' + times[u'nightfall'].strftime(u'%H:%M %Y-%m-%d')
    twilight = u'background-color:#ddd;' if times['now'][0] < times[u'nightfall'] and times['now'][0] > times[u'sunset'] and not times['print'] else u''
    bracha_style = u'color:#aaa;font-size:14px;' if times['now'][0] < times[u'sunset'] and times['now'][0] > times[u'dawn'] and not times['print'] else u'font-size:21px;'
    bracha = u'בָּרוּךְ אַתָּה יְהוָה אֱלהֵֽינוּ מֶֽלֶךְ הָעוֹלָם, אֲשֶׁר קִדְּשָֽׁנוּ בְּמִצְוֹתָיו, וְצִוָּֽנוּ עַל סְפִירַת הָעֽוֹמֶר'
    harachaman = u'הָרַחֲמָן הוּא יַחֲזִיר לָֽנוּ עֲבוֹדַת בֵּית הַמִּקְדָּשׁ לִמְקוֹמָהּ, בִּמְהֵרָה בְיָמֵֽינוּ אָמֵן סֶֽלָה'
    baruchshem = u'בָּרוּךְ שֵׁם כְּבוֹד מַלְכוּתוֹ לְעוֹלָם וָעֶד'

    output = {
              u'day': day,
              u'hebnum': hebrew_numeral(day, False),
              u'twilight': twilight,
              u'zipcode': times['zipcode'],
              u'special': special.get(day, ''),
              u'bracha_style': bracha_style,
              u'bracha': bracha+u'׃',
              u'yom': yom(day-1)+u'׃',
              u'harachaman': harachaman+u'׃',
              u'lamnatzeach': lamnatzeach(day),
              u'anabechoach': anabechoach(day-1),
              u'baruchshem': baruchshem+u'׃',
              u'ribonoshelolam': ribonoshelolam(day),
              u'tzeit': tzeit,
             }

    return render_template('main.html', **output)

def lamnatzeach(day):
    cday = day
    if day >= 16: cday = day + 1 # this is for dealing with
    if day >= 33: cday = day + 2 # the two commas in yismechu
    lamnatzeach = [ # double spacing so that we can easily parse <span id=red> as a single item
u'לַמְנַצֵּֽחַ  בִּנְגִינוֹת  מִזְמוֹר  שִׁיר׃  אֱלהִים  יְחָנֵּֽנוּ  וִיבָרְכֵֽנוּ,  יָאֵר  פָּנָיו  אִתָּֽנוּ  סֶלָה׃ ',
u' לָדַֽעַת  בָּאָֽרֶץ  דַּרְכֶּֽךָ,  בְּכָל  גּוֹיִם  יְשׁוּעָתֶֽךָ׃  יוֹדֽוּךָ  עַמִּים  ׀  אֱלהִים,  יוֹדֽוּךָ  עַמִּים  כֻּלָּם׃ ',
u' יִשְׂמְחוּ  וִירַנְּנוּ  לְאֻמִּים,  כִּי  תִשְׁפֹּ\u200cט  עַמִּים  מִישֹׁ\u200cר,  וּלְאֻמִּים  בָּאָֽרֶץ  תַּנְחֵם  סֶֽלָה׃  יוֹדֽוּךָ ',
u' עַמִּים  ׀  אֱלהִים,  יוֹדֽוּךָ  עַמִּים  כֻּלָּם׃  אֶֽרֶץ  נָתְנָה  יְבוּלָהּ,  יְבָרְכֵֽנוּ  אֱלהִים  אֱלהֵֽינוּ׃ ',
u' יְבָרְכֵֽנוּ  אֱלהִים,  וְיִירְאוּ  אוֹתוֹ  כָּל  אַפְסֵי  אָֽרֶץ׃']

    yismechu = lamnatzeach[2]
    numletters, i1, i2 = 0, None, None
    for c, char in enumerate(yismechu):
        if char in u'אבגדהוזחטיךכלםמןנסעףפץצקרשת\u200c':
            numletters += 1
        if numletters == day and not i1:
            i1 = c
        if numletters == day+1 and not i2:
            i2 = c
            while yismechu[i2-1] in u' ,׃':
                i2 -= 1

    letter = yismechu[i1:i2]
    if '\u200c' in letter:
        i1 -= 1 
        letter = letter.replace('\u200c', u'וֹ')

    lamnatzeach[2] = yismechu[:i1] + u'<span id=red>' + letter + u'</span>' + yismechu[i2:]

    l = u''.join(lamnatzeach).split(u'  ')
    return u' '.join(l[:cday+3]) + u'\n<span class=bigbold>' + l[cday+3] + u'</span>\n' + u' '.join(l[cday+4:])

def anabechoach(day):
    anabechoach = [ # double spacing here for HTML as well as the roshei teivos sets at the end of the line
u'אָנָּא,  בְּכֹֽחַ  גְּדֻלַּת  יְמִינְךָ,  תַּתִּיר  צְרוּרָה  אב"ג ית"ץ',
u'קַבֵּל  רִנַּת  עַמְּךָ,  שַׂגְּבֵֽנוּ,  טַהֲרֵֽנוּ,  נוֹרָא  קר"ע שט"ן',
u'נָא  גִבּוֹר,  דּוֹרְשֵׁי  יִחוּדְךָ,  כְּבָבַת  שָׁמְרֵם  נג"ד יכ"ש',
u'בָּרְכֵם,  טַהֲרֵם,  רַחֲמֵי  צִדְקָתְךָ  תָּמִיד  גָּמְלֵם  בט"ר צת"ג',
u'חֲסִין  קָדוֹשׁ,  בְּרוֹב  טוּבְךָ  נַהֵל  עֲדָתֶֽךָ  חק"ב טנ"ע',
u'יָחִיד,  גֵּאֶה,  לְעַמְּךָ  פְּנֵה,  זוֹכְרֵי  קְדֻשָּׁתֶֽךָ  יג"ל פז"ק',
u'שַׁוְעָתֵֽנוּ  קַבֵּל,  וּשְׁמַע  צַעֲקָתֵֽנוּ,  יוֹדֵֽעַ  תַּעֲלוּמוֹת  שק"ו צי"ת']
    week, day = divmod(day, 7)
    out = []
    for num, row in enumerate(anabechoach):
        if num != week:
            out.append(u'\n<tr><td class=left>' + row.split(u'  ')[-1] +
                       u'</td><td>.' + u'  '.join(row.split(u'  ')[:-1]) + u'</td></tr>')
        else:
            a = row.split(u'  ')
            bolded_row = u'  '.join(a[:day]) + \
            u'  <span class=bigbold>' + a[day] + u'</span>  ' + \
            u'  '.join(a[day+1:])
            b = bolded_row.strip().split(u'  ')
            out.append(u'\n<tr><td class=left>' + b[-1] + u'</td><td>.' + u'  '.join(b[:-1]) + u'</td></tr>')
    return u''.join(out)

def ribonoshelolam(day):
    def sefiros(day):
        sefiros = u'חֶֽסֶד גְּבוּרָה תִּפְאֶֽרֶת נֶֽצַח הוֹד יְסוֹד מַלְכוּת'.split()
        week, day = divmod(day-1, 7)
        if week in (1, 5):
            s = u'י' + sefiros[week][2:] if week == 5 else sefiros[week]
            return u'<span class=bigbold>' + sefiros[day] + u' שֶׁבִּ' + s + u'</span>'
        else:
            s = u'ת' + sefiros[week][2:] if week == 2 else sefiros[week]
            return u'<span class=bigbold>' + sefiros[day] + u' שֶׁבְּ' + s + u'</span>'

    ribonoshelolam = [
u'רִבּוֹנוֹ שֶׁל עוֹלָם, אַתָּה צִוִּיתָֽנוּ עַל יְדֵי משֶׁה עַבְדֶּֽךָ לִסְפּוֹר סְפִירַת הָעֽוֹמֶר כְּדֵי לְטַהֲרֵֽנוּ מִקְלִפּוֹתֵֽינוּ וּמִטּוּמְאוֹתֵֽינוּ, כְּמוֹ שֶׁכָּתַֽבְתָּ בְּתוֹרָתֶֽךָ׃',
u'וּסְפַרְתֶּם לָכֶם מִמָּחֳרַת הַשַּׁבָּת מִיוֹם הֲבִיאֲכֶם אֶת עֽוֹמֶר הַתְּנוּפָה שֶֽׁבַע שַׁבָּתוֹת תְּמִימוֹת תִּהְיֶֽינָה, עַד מִמָּחֳרַת הַשַּׁבָּת הַשְּׁבִיעִית תִּסְפְּרוּ חֲמִשִּׁים יוֹם,',
u'כְּדֵי שֶׁיִּטָּהֲרוּ נַפְשׁוֹת עַמְּךָ יִשְׂרָאֵל מִזֻּהֲמָתָם, וּבְכֵן יְהִי רָצוֹן מִלְּפָנֶֽיךָ, יְהוָה אֱלהֵֽינוּ וֵאלהֵי אֲבוֹתֵֽינוּ,',
u'שֶׁבִּזְכוּת סְפִירַת הָעֽוֹמֶר שֶׁסָּפַֽרְתִּי הַיּוֹם יְתֻקַּן מַה שֶׁפָּגַֽמְתִּי בִּסְפִירָה',

u'וְאֶטָּהֵר וְאֶתְקַדֵּשׁ בִּקְדֻשָּׁה שֶׁל מַעְֽלָה,',
u'וְעַל יְדֵי זֶה יֻשְׁפַּע שֶֽׁפַע רַב בְּכָל הָעוֹלָמוֹת וּלְתַקֵּן אֶת נַפְשׁוֹתֵֽינוּ וְרוּחוֹתֵֽינוּ וְנִשְׁמוֹתֵֽינוּ מִכָּל סִיג וּפְגַם וּלְטַהֲרֵֽנוּ וּלְקַדְּשֵֽׁנוּ בִּקְדֻשָׁתְךָ הָעֶלְיוֹנָה, אָמֵן סֶֽלָה׃']

    return u' '.join(ribonoshelolam[:4] + [sefiros(day)] + ribonoshelolam[4:])
