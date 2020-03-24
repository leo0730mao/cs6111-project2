import os
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
from stanfordnlp.server import CoreNLPClient
from utils import extract_relation, google_search
from datetime import datetime

os.environ["CORENLP_HOME"] = "/Users/maoyue/Desktop/stanford-corenlp-full-2018-10-05/"


if __name__ == '__main__':
    if len(sys.argv) != 7:
        print("main <google api key> <google engine id> <r> <t> <q> <k>")
        exit(1)
    api_key = sys.argv[1]
    engine_id = sys.argv[2]
    r = int(sys.argv[3])
    t = float(sys.argv[4])
    q = sys.argv[5]
    k = int(sys.argv[6])
    now = datetime.now()
    print(now.strftime("%d/%m/%Y %H:%m:%s\n"))

#    api_key = "AIzaSyCRnG7OG9U5R7nobD1VQvhxoc33mYmr08g"
#    engine_id = ""015777630004812292025:fvvd1zkgpmv""
#    r = 1
#    t = 0.5
#    q = "bill Gates microsoft"
#    k = 5
    
    print("run <APIKey> <EngineID> %d %d %s %d" % (r, t, q, k))
    

    x = dict()
    processed_page = set()
    queried_tuple = set()
    
    print()
    print("Parameters:")
    print("Client key = %s" % api_key)
    print("Engine key = %s" % engine_id)
    print("Relation per:schools_attended")
    print("Threshold = %d" % t)
    print("Query = %s" % q)
    print("Number of tuples = %d" % k)

    # Loop until have more than k tuples
    with CoreNLPClient(timeout = 300000, memory = '4G') as pipeline:
        while True:
            # step 2: query for top-10 webpages for current query q
            res = google_search(api_key, engine_id, q)
            for idx, webpage in enumerate(res['items']):
                if webpage['formattedUrl'] not in processed_page:
                    print("URL %d: %s" % (idx + 1, webpage['formattedUrl']))
                    processed_page.add(webpage['formattedUrl'])
                    try:
                        html = urlopen(webpage['formattedUrl']).read()
                    except:
                        html = None
                    if html is not None:
                        soup = BeautifulSoup(html, 'html.parser')
                        for script in soup(['script', "style"]):
                            script.decompose()
                        text = soup.get_text()[:20000]
                        relations = extract_relation(pipeline, text, r, t)
                        for item in relations:
                            if item[0] not in x:
                                x[item[0]] = item[1]
                            elif item[0] in x and item[1] > x[item[0]]:
                                x[item[0]] = item[1]
                print("Complete %s-th webpage, now we have %s tuples" % (idx + 1, len(x)))
            sorted_x = sorted(x.items(), key = lambda item: item[1])
            if len(sorted_x) >= k:
                print([item[0] for item in sorted_x[:k]])
                exit(0)
            else:
                for item in sorted_x:
                    if item[0] not in queried_tuple:
                        q = item[0][0] + " " + item[0][2]
                        queried_tuple.add(item[0])
