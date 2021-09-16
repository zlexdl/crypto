import json

# with open("data/uni_whales.json", 'r', encoding='utf-8') as load_f:
with open("data/cake_whales.json", 'r', encoding='utf-8') as load_f:
# with open("data/sushi_whales.json", 'r', encoding='utf-8') as load_f:


    load_dict = json.load(load_f)
    # print(load_dict['messages'])
    count15 = 0
    count17 = 0
    count13 = 0
    count11 = 0
    count10 = 0
    count12 = 0
    counto = 0
    count = 0
    for m in load_dict['messages']:
        counto = counto + 1
        # print(m['date'])
        # print(m['text'].len())
        # print(type(m['text']))
        if isinstance(m['text'], str):
            print('continue0=' + str(m['text']))
            continue
        if len(m['text']) >= 10:
            try:
                if isinstance(m['text'][0], dict):
                    print('continue1=' + str(m['text']))
                    continue
                if m['text'][0].find('Swap') < 0:
                    print('continue2=' + str(m['text']))
                    continue
                from_volume = m['text'][1]['text'].replace(',', '')
                from_asset = m['text'][3]['text'].replace('#', '')
                to_volume = m['text'][5]['text'].replace(',', '')
                to_asset = m['text'][7]['text'].replace('#', '')
                txn_type = ''
                txn_href = ''
                count = count + 1
                for n in range(9, len(m['text']) - 1):
                    other = m['text'][n]
                    if isinstance(other, dict):
                        # count = count + 1
                        if other['text'] == '#shrimp':
                            txn_type = 'shrimp'
                        elif other['text'] == '#fish':
                            txn_type = 'fish'
                        elif other['text'] == '#dolphin':
                            txn_type = 'dolphin'
                        elif other['text'] == '#whale':
                            txn_type = 'whale'
                        elif 'href' in other:
                            if other['href'] != '':
                                txn_href = other['href']
                        elif other['text'] == 'Etherscan':
                            txn_href = n['href']
                        # if txn_type == '':
                        #     print(m['text'])

                # print("{},{},{},{},{},{}".format(from_volume, from_asset, to_volume, to_asset, txn_type, txn_href))

            except Exception as err:
                # print('count=' + str(count))
                print(err)
        # if len(m['text']) == 15:
        #
        #     count15 = count15 + 1
        # elif len(m['text']) == 17:
        #
        #     count17 = count17 + 1
        # elif len(m['text']) == 13:
        #     print(m['text'])
        #     count13 = count13 + 1
        # elif len(m['text']) == 11:
        #     count11 = count11 + 1
        # elif len(m['text']) == 10:
        #
        #     count10 = count10 + 1
        # elif len(m['text']) == 12:
        #
        #     count12 = count12 + 1
        #
        # else:
        #     print(m['text'])
        #     counto = counto + 1

    print('count10=' + str(count10))
    print('count11=' + str(count11))
    print('count12=' + str(count12))
    print('count13=' + str(count13))
    print('count15=' + str(count15))
    print('count17=' + str(count17))
    print('counto=' + str(counto))
    print('count=' + str(count))

if __name__ == '__main__':
    print('test')
