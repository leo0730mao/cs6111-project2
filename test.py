from stanfordnlp.server import CoreNLPClient

annotators_ner = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner']
annotators_kbp = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse', 'coref', 'kbp']
text = "Joe Smith was born in California. It will probably rain on Friday."
with CoreNLPClient(timeout=300000, memory='4G') as pipeline:
    res = pipeline.annotate(text, annotators = annotators_ner)
    for sentence in res.sentence:
        tags = set()
        words = list()
        for token in sentence.token:
            tags.add(token.ner)
            words.append(token.word)
        if 'PERSON' in tags and ('LOCATION' in tags or 'CITY' in tags or 'STATE_OR_PROVINCE' in tags or 'COUNTRY' in tags):
            s = " ".join(words)
            annotated_sentence = pipeline.annotate(s, annotators = annotators_kbp)
            for t in annotated_sentence.sentence[0].kbpTriple:
                print(t.subject + " " + t.relation + " " + t.object)

