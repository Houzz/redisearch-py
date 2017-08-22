import itertools
from .document import Document
from houzz.wise.ner.ner_types import NerRuleEntity

class NERResult(object):
    """
    Represents the result of a search query, and has an array of Document objects
    """

    def __init__(self, res, hascontent, query_text, duration=0, snippets = None, has_payload = False, has_score = False, original_query=None, ner_type=None):
        self.total = res[0]
        self.duration = duration
        self.docs = []
                
        tokens = filter(None, query_text.rstrip("\" ").lstrip(" \"").split(' '))
        step = 1
        if hascontent:
            step += 1
            if has_payload:
                step += 1
        else:
            # we can't have nocontent and payloads in the same response
            has_payload = False

        if has_score:
            step += 1
        
        for i in xrange(1, len(res), step):
            id = res[i]
            fields_offset = 1
            score = None
            payload = None
            entity = NerRuleEntity()

            if has_score:
                score = float(res[i + fields_offset])
                fields_offset += 1

            if has_payload:
                payload = res[i + fields_offset]
                fields_offset += 1
            
            fields = {} 
            if hascontent:
                fields = dict(
                    dict(itertools.izip(res[i + fields_offset][::2], res[i + fields_offset][1::2]))) if hascontent else {}

            entity.set_from_redis_hit(fields, original_query,score, ner_type)
                            
            self.docs.append(entity)
            
            
class Result(object):
    """
    Represents the result of a search query, and has an array of Document objects
    """

    def __init__(self, res, hascontent, query_text, duration=0, snippets = None, has_payload = False, has_score = False):
        """
        - **snippets**: An optional dictionary of the form {field: snippet_size} for snippet formatting
        """

        self.total = res[0]
        self.duration = duration
        self.docs = []

        tokens = filter(None, query_text.rstrip("\" ").lstrip(" \"").split(' '))
        step = 1
        if hascontent:
            step += 1
            if has_payload:
                step += 1
        else:
            # we can't have nocontent and payloads in the same response
            has_payload = False

        if has_score:
            step += 1
        
        for i in xrange(1, len(res), step):
            id = res[i]
            fields_offset = 1
            score = None
            payload = None

            if has_score:
                score = float(res[i + fields_offset])
                fields_offset += 1

            if has_payload:
                payload = res[i + fields_offset]
                fields_offset += 1
            
            fields = {} 
            if hascontent:
                fields = dict(
                    dict(itertools.izip(res[i + fields_offset][::2], res[i + fields_offset][1::2]))) if hascontent else {}
            try:
                del fields['id']
            except KeyError:
                pass

            doc = Document(id, payload=payload, score=score, **fields)
            #print doc
            if hascontent and snippets:
                for k,v in snippets.iteritems():
                    doc.snippetize(k, size=v, bold_tokens = tokens)
                
            self.docs.append(doc)


    def __repr__(self):

        return 'Result{%d total, docs: %s}' % (self.total, self.docs)
