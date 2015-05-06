#!/usr/bin/python
# -*- coding: UTF-8 -*-

days = [
    u"יוֹם אֶחָד",
    u"שְׁנֵי",
    u"שְׁלשָׁה",
    u"אַרְבָּעָה",
    u"חֲמִשָּׁה",
    u"שִׁשָּׁה",
    u"שִׁבְעָה",
    u"שְׁמוֹנָה",
    u"תִּשְׁעָה",
    u"עֲשָׂרָה",
    u"עָשָׂר",
    u"אַחַד",
    u"שְׁנֵים",
    u"עֶשְׂרִים",
    u"שְׁלשִׁים",
    u"אַרְבָּעִים",
    u"",
    u"אֶחָד",
    u"שְׁנַיִם",
    u"שָׁבוּעַ אֶחָד"
]

vov_hachibur = [ u"", u"וְ", u"וּ", u"וַ" ]

yomim = [ u"", u" יוֹם", u" יָמִים", u" שָׁבוּעוֹת" ]

space = [ u"", u" " ]

indices = [
    (  0, 0, 0, 16, 0 ),
    (  1, 0, 0, 16, 2 ),
    (  2, 0, 0, 16, 2 ),
    (  3, 0, 0, 16, 2 ),
    (  4, 0, 0, 16, 2 ),
    (  5, 0, 0, 16, 2 ),
    (  6, 0, 0, 16, 2 ),
    (  7, 0, 0, 16, 2 ),
    (  8, 0, 0, 16, 2 ),
    (  9, 0, 0, 16, 2 ),
    ( 11, 1, 0, 10, 1 ),
    ( 12, 1, 0, 10, 1 ),
    (  2, 1, 0, 10, 1 ),
    (  3, 1, 0, 10, 1 ),
    (  4, 1, 0, 10, 1 ),
    (  5, 1, 0, 10, 1 ),
    (  6, 1, 0, 10, 1 ),
    (  7, 1, 0, 10, 1 ),
    (  8, 1, 0, 10, 1 ),
    ( 13, 0, 0, 16, 1 ),
    ( 17, 1, 1, 13, 1 ),
    ( 18, 1, 1, 13, 1 ),
    (  2, 1, 1, 13, 1 ),
    (  3, 1, 1, 13, 1 ),
    (  4, 1, 1, 13, 1 ),
    (  5, 1, 1, 13, 1 ),
    (  6, 1, 1, 13, 1 ),
    (  7, 1, 1, 13, 1 ),
    (  8, 1, 1, 13, 1 ),
    ( 14, 0, 0, 16, 1 ),
    ( 17, 1, 2, 14, 1 ),
    ( 18, 1, 2, 14, 1 ),
    (  2, 1, 2, 14, 1 ),
    (  3, 1, 2, 14, 1 ),
    (  4, 1, 2, 14, 1 ),
    (  5, 1, 2, 14, 1 ),
    (  6, 1, 2, 14, 1 ),
    (  7, 1, 2, 14, 1 ),
    (  8, 1, 2, 14, 1 ),
    ( 15, 0, 0, 16, 1 ),
    ( 17, 1, 1, 15, 1 ),
    ( 18, 1, 1, 15, 1 ),
    (  2, 1, 1, 15, 1 ),
    (  3, 1, 1, 15, 1 ),
    (  4, 1, 1, 15, 1 ),
    (  5, 1, 1, 15, 1 ),
    (  6, 1, 1, 15, 1 ),
    (  7, 1, 1, 15, 1 ),
    (  8, 1, 1, 15, 1 ),
]

def makeDaysString(day):
    return u"<span class=bold>%s%s%s%s%s</span> " % ( days         [ indices[ day ][0] ],
                              space        [ indices[ day ][1] ],
                              vov_hachibur [ indices[ day ][2] ],
                              days         [ indices[ day ][3] ],
                              yomim        [ indices[ day ][4] ] )
'''
 0
 1 Shovua Ekhod  ()
 2 Shnei Shovuois (va-) 5         Shnei space Shavuois space va
 3 Shloisho Shovuois (ve-) 1, 4, 6
 4 Arbo'o Shovuois (u-) 2, 3
 5 Khamisho Shovuois
 6 Shishsho Shovuois
 7 Shiv'o Shovuois
'''

week_indices = [
    (  16,  0 ), # 0 (            )
    (  19,  0 ), # 1 (Shovua Echod)
    (   1,  3 ), # 2 (Shnei Shovuois)
    (   2,  3 ), # 3 (Shloisho Shovuois)
    (   3,  3 ), # 3 (Arbo'o Shovuois)
    (   4,  3 ), # 5 (Khamisho Shovuois)
    (   5,  3 ), # 6 (Shishsho Shovuois)
    (   6,  3 ), # 7 (Shiv'o Shovuois)
]

def makeShavuoisString(shavua):
    if not shavua:
        return u''
    return u"שֶׁהֵם <span class=bold>%s%s</span> " % ( days[ week_indices[ shavua ][0] ],
                                                    yomim [ week_indices[ shavua ][1] ]  )

remaining_index = [ 0, 1, 2, 2, 1, 3, 1 ]

def yom(day):
    shavua = (day + 1) // 7
    remaining_days = (day + 1) % 7

    total_days = makeDaysString(day)
    weeks = makeShavuoisString(shavua)
    days = makeDaysString(remaining_days - 1)

    if day < 6:
        return u"הַיּוֹם %sלָעוֹמֶר" % (total_days)
    if not remaining_days:
        return u"הַיּוֹם %s%sלָעוֹמֶר" % (total_days, weeks)
    return u"הַיּוֹם %s%s<span class=bold>%s</span>%sלָעוֹמֶר" % (total_days, weeks, vov_hachibur[remaining_index[remaining_days]], days)

