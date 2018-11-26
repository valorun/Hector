from chatterbot.logic import BestMatch
from chatterbot.conversation import Statement
import re

ENTITY_PATTERN='{entity}'

class EntityAdapter(BestMatch):

    def __init__(self, **kwargs):
        super(EntityAdapter, self).__init__(**kwargs)

    def can_process(self, statement):
        return True

    def process(self, statement):
        statement_list = self.chatbot.storage.get_response_statements()

        if statement_list:
            for s in statement_list: # for each sentences
                if(ENTITY_PATTERN in s.text): #if the sentence has a 'gap'
                    pattern=self.get_pattern(s.text)
                    if(pattern.match(statement.text)): #and if the input sentence correspond to its pattern
                        entities=re.search(pattern, statement.text).groups()
                        response=super(EntityAdapter, self).process(s)
                        response.entities=entities #add entities to the answer
                        response.confidence=1.0
                        return response
        response=super(EntityAdapter, self).process(statement)
        response.entities=()
        return response

    def get_pattern(self, statement):
        st_list=re.split("("+ENTITY_PATTERN+")", statement)
        pattern="^"
        for s in st_list:
            if(s==ENTITY_PATTERN):
                pattern=pattern+"(.*?)"
            else:
                pattern=pattern+s
        return re.compile(pattern+"$", re.IGNORECASE)

    #def compare(self, input_statement, statement):
    #    static_parts=statement.split()
    #    for p in static_parts:
    #        words=p.split(" ")
    #        statement
    #        for w in words:
    #            confidence = self.compare_statements(input_statement, word)
    #            if(confidence < 0.7):