import json

def getElement(co):
    if len(co) > 0 and isinstance(co[0],list):
        return getElement(co[0])
    else:
        return co
def process_json_tokenize(path):
    data = []
    with open("data/sample.json","r") as file:
        tweets = json.load(file)
        for t in tweets:
            tw = {}
            for k,v in t.items():
                if k == 'Coordinates':
                    tw['Coordinates'] = getElement(v)
                elif k == 'Entities':
                    for ek, vk in v.items():
                        if ek == 'hashtags':
                            hashtags = []
                            for tag in vk:
                                hashtags.append(tag['text'])
                            tw['hashtags'] = hashtags
                        elif ek == 'media' or ek == 'urls':
                            if len(vk) > 0:
                                for key,value in vk[0].items():
                                    if key == "expanded_url":
                                        tw['url'] = value
                else:
                    tw[k] = v
            data.append(tw)
    return data

d = process_json_tokenize("data/sample.json")

for tweet in d:
    for k,v in tweet.items():
        print(k,v)
    
    print()

