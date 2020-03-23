from googleapiclient.discovery import build

annotators_ner = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner']
annotators_kbp = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp']


def judge(tags, r):
    if r == 1 or r == 2 or r == 4:
        return 'ORGANIZATION' in tags and 'PERSON' in tags
    elif r == 3:
        return 'PERSON' in tags and (
                            'LOCATION' in tags or 'CITY' in tags or 'STATE_OR_PROVINCE' in tags or 'COUNTRY' in tags)
    else:
        print("Exit due to unexpected r")
        exit(1)


def extract_relation(pipeline, text, r, t):
    relation = {1: 'per:schools_attended', 2: 'per:employee_or_member_of', 3: 'per:cities_of_residence', 4: 'org:top_members_employees'}
    ner_text = pipeline.annotate(text, annotators = annotators_ner)
    res = set()
    for sentence in ner_text.sentence:
        tags = set()
        words = list()
        for token in sentence.token:
            tags.add(token.ner)
            words.append(token.word)
        if judge(tags, r):
            s = " ".join(words)
            kbp_sentence = pipeline.annotate(s, annotators = annotators_kbp)
            for sen in kbp_sentence.sentence:
                for rel in sen.kbpTriple:
                    if rel.confidence > t and rel.relation == relation[r]:
                        res.add(((rel.subject, rel.relation, rel.object), rel.confidence))
    return res


def google_search(api_key, engine_id, query):
    service = build("customsearch", "v1", developerKey = api_key)
    res = service.cse().list(q = query, cx = engine_id).execute()
    return res
