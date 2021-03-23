from flask import render_template
from Yom import yom # creates just the "hayom...laomer" line
import yaml
import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

def hebrew_numeral(val, gershayim=True):
    hsn = yaml.load(open(os.path.join(THIS_FOLDER,'data/hebrew-special-numbers/styles/default.yml'), encoding="utf8"), Loader=yaml.SafeLoader)

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

def textforday(kwargs):
    '''
        kwargs is a dict with keys: ['day_of_omer', 'print', 'zipcode', 'hash', 'now', 'dawn', 'sunset', 'nightfall']
        where:
            day_of_omer is an int
            print is a bool
            zipcode is a string
            hash is a string
            rest are datetime
    '''
    day = kwargs['day_of_omer'] # dont feel like renaming every instance below

    if day not in range(1,50):
        return render_template('error.html', day=day)

    special = {15: "א' דראש חודש אייר",
               16: "ב' דראש חודש אייר",
               29: 'פסח שני‎',
               33: 'ל״ג בעומר',
               45: 'ראש חודש סיון'}

    try:
        tzeit = 'צאת הכוכבים׃' + kwargs['nightfall'].strftime(u'%H:%M %Y-%m-%d')
        twilight = 'background-color:#ddd;' if kwargs['now'] < kwargs['nightfall'] and kwargs['now'] > kwargs['sunset'] and not kwargs['print'] else ''
        bracha_style = 'color:#aaa;font-size:14px;' if kwargs['now'] < kwargs['sunset'] and kwargs['now'] > kwargs['dawn'] and not kwargs['print'] else 'font-size:21px;'
    except KeyError:
        tzeit, twilight, bracha_style = 'Zmanim error: Next day appears at noon', '', ''

    bracha = 'בָּרוּךְ אַתָּה יְהֹוָה אֱלהֵֽינוּ מֶֽלֶךְ הָעוֹלָם, אֲשֶׁר קִדְּשָֽׁנוּ בְּמִצְוֹתָיו, וְצִוָּֽנוּ עַל סְפִירַת הָעֽוֹמֶר'
    if kwargs['print']:
        bracha = bracha.replace(
            'יְהֹוָה אֱלהֵֽינוּ',
            'ה׳ אֱלקֵֽינוּ'
        )
    harachaman = 'הָרַחֲמָן הוּא יַחֲזִיר לָֽנוּ עֲבוֹדַת בֵּית הַמִּקְדָּשׁ לִמְקוֹמָהּ, בִּמְהֵרָה בְיָמֵֽינוּ אָמֵן סֶֽלָה'
    baruchshem = 'בָּרוּךְ שֵׁם כְּבוֹד מַלְכוּתוֹ לְעוֹלָם וָעֶד'

    output = {
              'day': day,
              'hebnum': hebrew_numeral(day, False),
              'twilight': twilight,
              'zipcode': kwargs['zipcode'],
              'special': special.get(day, ''),
              'bracha_style': bracha_style,
              'bracha': bracha+'׃',
              'yom': yom(day-1)+'׃',
              'harachaman': harachaman+'׃',
              'lamnatzeach': lamnatzeach(day, kwargs['print']),
              'anabechoach': anabechoach(day-1),
              'baruchshem': baruchshem+'׃',
              'ribonoshelolam': ribonoshelolam(day, kwargs['print']),
              'tzeit': tzeit,
              'hash': kwargs.get('hash', '_'),
              'debug': kwargs
             }

    return render_template('main.html', **output)

def lamnatzeach(day, prnt=False):
    cday = day
    if day >= 16: cday = day + 1 # this is for dealing with
    if day >= 33: cday = day + 2 # the two commas in yismechu
    lamnatzeach = [ # double spacing so that we can easily parse <span id=red> as a single item
        'לַמְנַצֵּֽחַ  בִּנְגִינוֹת  מִזְמוֹר  שִׁיר׃  אֱלהִים  יְחָנֵּֽנוּ  וִיבָרְכֵֽנוּ,  יָאֵר  פָּנָיו  אִתָּֽנוּ  סֶלָה׃ ',
        ' לָדַֽעַת  בָּאָֽרֶץ  דַּרְכֶּֽךָ,  בְּכָל  גּוֹיִם  יְשׁוּעָתֶֽךָ׃  יוֹדֽוּךָ  עַמִּים  ׀  אֱלהִים,  יוֹדֽוּךָ  עַמִּים  כֻּלָּם׃ ',
        ' יִשְׂמְחוּ  וִירַנְּנוּ  לְאֻמִּים,  כִּי  תִשְׁפֹּ\u200cט  עַמִּים  מִישֹׁ\u200cר,  וּלְאֻמִּים  בָּאָֽרֶץ  תַּנְחֵם  סֶֽלָה׃  יוֹדֽוּךָ ',
        ' עַמִּים  ׀  אֱלהִים,  יוֹדֽוּךָ  עַמִּים  כֻּלָּם׃  אֶֽרֶץ  נָתְנָה  יְבוּלָהּ,  יְבָרְכֵֽנוּ  אֱלהִים  אֱלהֵֽינוּ׃ ',
        ' יְבָרְכֵֽנוּ  אֱלהִים,  וְיִירְאוּ  אוֹתוֹ  כָּל  אַפְסֵי  אָֽרֶץ׃'
    ]

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
        letter = letter.replace('\u200c', 'וֹ')

    lamnatzeach[2] = yismechu[:i1] + '<span id=red>' + letter + '</span>' + yismechu[i2:]

    lamnatzeach = ''.join(lamnatzeach)
    if prnt:
        lamnatzeach = lamnatzeach.replace(
            'אֱלהִים',
            'אֱלקִים'
        ).replace(
            'אֱלהֵֽינוּ׃',
            'אֱלקֵֽינוּ'
        )
    l = lamnatzeach.split('  ')
    return ' '.join(l[:cday+3]) + '\n<span class=bigbold>' + l[cday+3] + '</span>\n' + ' '.join(l[cday+4:])

def anabechoach(day):
    anabechoach = [ # double spacing here for HTML as well as the roshei teivos sets at the end of the line
        'אָנָּא,  בְּכֹֽחַ  גְּדֻלַּת  יְמִינְךָ,  תַּתִּיר  צְרוּרָה  אב"ג ית"ץ',
        'קַבֵּל  רִנַּת  עַמְּךָ,  שַׂגְּבֵֽנוּ,  טַהֲרֵֽנוּ,  נוֹרָא  קר"ע שט"ן',
        'נָא  גִבּוֹר,  דּוֹרְשֵׁי  יִחוּדְךָ,  כְּבָבַת  שָׁמְרֵם  נג"ד יכ"ש',
        'בָּרְכֵם,  טַהֲרֵם,  רַחֲמֵי  צִדְקָתְךָ  תָּמִיד  גָּמְלֵם  בט"ר צת"ג',
        'חֲסִין  קָדוֹשׁ,  בְּרוֹב  טוּבְךָ  נַהֵל  עֲדָתֶֽךָ  חק"ב טנ"ע',
        'יָחִיד,  גֵּאֶה,  לְעַמְּךָ  פְּנֵה,  זוֹכְרֵי  קְדֻשָּׁתֶֽךָ  יג"ל פז"ק',
        'שַׁוְעָתֵֽנוּ  קַבֵּל,  וּשְׁמַע  צַעֲקָתֵֽנוּ,  יוֹדֵֽעַ  תַּעֲלוּמוֹת  שק"ו צי"ת'
    ]
    week, day = divmod(day, 7)
    out = []
    for num, row in enumerate(anabechoach):
        if num != week:
            out.append('\n<tr><td class=left>' + row.split('  ')[-1] +
                       '</td><td>.' + '  '.join(row.split('  ')[:-1]) + '</td></tr>')
        else:
            a = row.split('  ')
            bolded_row = '  '.join(a[:day]) + \
            '  <span class=bigbold>' + a[day] + '</span>  ' + \
            '  '.join(a[day+1:])
            b = bolded_row.strip().split('  ')
            out.append('\n<tr><td class=left>' + b[-1] + '</td><td>.' + '  '.join(b[:-1]) + '</td></tr>')
    return u''.join(out)

def ribonoshelolam(day, prnt=False):
    def sefiros(day):
        sefiros = 'חֶֽסֶד גְּבוּרָה תִּפְאֶֽרֶת נֶֽצַח הוֹד יְסוֹד מַלְכוּת'.split()
        week, day = divmod(day-1, 7)
        if week in (1, 5):
            s = 'י' + sefiros[week][2:] if week == 5 else sefiros[week]
            return '<span class=bigbold>' + sefiros[day] + ' שֶׁבִּ' + s + '</span>'
        else:
            s = 'ת' + sefiros[week][2:] if week == 2 else sefiros[week]
            return '<span class=bigbold>' + sefiros[day] + ' שֶׁבְּ' + s + '</span>'

    ribonoshelolam = [
        'רִבּוֹנוֹ שֶׁל עוֹלָם, אַתָּה צִוִּיתָֽנוּ עַל יְדֵי משֶׁה עַבְדֶּֽךָ לִסְפּוֹר סְפִירַת הָעֽוֹמֶר כְּדֵי לְטַהֲרֵֽנוּ מִקְלִפּוֹתֵֽינוּ וּמִטּוּמְאוֹתֵֽינוּ, כְּמוֹ שֶׁכָּתַֽבְתָּ בְּתוֹרָתֶֽךָ׃',
        'וּסְפַרְתֶּם לָכֶם מִמָּחֳרַת הַשַּׁבָּת מִיוֹם הֲבִיאֲכֶם אֶת עֽוֹמֶר הַתְּנוּפָה שֶֽׁבַע שַׁבָּתוֹת תְּמִימוֹת תִּהְיֶֽינָה, עַד מִמָּחֳרַת הַשַּׁבָּת הַשְּׁבִיעִית תִּסְפְּרוּ חֲמִשִּׁים יוֹם,',
        'כְּדֵי שֶׁיִּטָּהֲרוּ נַפְשׁוֹת עַמְּךָ יִשְׂרָאֵל מִזֻּהֲמָתָם, וּבְכֵן יְהִי רָצוֹן מִלְּפָנֶֽיךָ, יְהֹוָה אֱלהֵֽינוּ וֵאלהֵי אֲבוֹתֵֽינוּ,',
        'שֶׁבִּזְכוּת סְפִירַת הָעֽוֹמֶר שֶׁסָּפַֽרְתִּי הַיּוֹם יְתֻקַּן מַה שֶׁפָּגַֽמְתִּי בִּסְפִירָה',

        'וְאֶטָּהֵר וְאֶתְקַדֵּשׁ בִּקְדֻשָּׁה שֶׁל מַֽעְלָה,',
        'וְעַל יְדֵי זֶה יֻשְׁפַּע שֶֽׁפַע רַב בְּכָל הָעוֹלָמוֹת וּלְתַקֵּן אֶת נַפְשׁוֹתֵֽינוּ וְרוּחוֹתֵֽינוּ וְנִשְׁמוֹתֵֽינוּ מִכָּל סִיג וּפְגַם וּלְטַהֲרֵֽנוּ וּלְקַדְּשֵֽׁנוּ בִּקְדֻשָׁתְךָ הָעֶלְיוֹנָה, אָמֵן סֶֽלָה׃'
    ]
    if prnt:
        ribonoshelolam[2] = ribonoshelolam[2].replace(
            'יְהֹוָה אֱלהֵֽינוּ וֵאלהֵי',
            'ה׳ אֱלקֵֽינוּ וֵאלקֵי'
        )
    return ' '.join(ribonoshelolam[:4] + [sefiros(day)] + ribonoshelolam[4:])
