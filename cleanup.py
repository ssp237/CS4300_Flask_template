import json
with open('finaldata.json') as json_file:
    data = json.load(json_file)
bad = ['foundation', 'mascara', 'brow', 'eyeliner', 'pencil',
       'lipstick', 'gloss', 'blush', 'concealer', 'tan', 'bronzer',
       'primer', 'lippie', 'palette', 'highlight', 'eyeshadow', 'powder',
       'eye shadow', 'cheek duo', 'bronzing', 'compact', 'blotting',
       'brush', 'brushes', 'setting', 'corrector', 'tinted', 'strobing'
       'nail' ,'cuticle', 'lip', 'colour']
newdata = {}
for key, dic in data.items() :
    tag = True
    if dic['price'] != 0 and dic['claims'] != '' and dic['ingredients'] != '' :
        tag = False
    for term in bad:
        if term in key.lower():
            tag = True
    if not tag:
        newdata[key] = dic
with open('finaldata.json', 'w') as outfile:
    json.dump(newdata, outfile, indent=7)