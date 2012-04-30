'''
Created on Apr 27, 2012

@author: ruicovelo
'''

import re


class StringScorer(object):
    '''
    Scores a string according to a given pattern and weights

    '''
    # The scores are based on the presence of parts of pattern in the strings
    # being matched (not differences like most string metric algorithms)
    # This is a rudimentary algorithm but at the same time configurable.
    # The scores can be set according to importance (bigger is more important to end result)
 
    
    # The default scores are set like this:
    # If the pattern matches the full string, it is what we are looking for. Big score.
    # Complete words matching is also very importance even if not in the correct place.
    # If the words are in the correct place/order/index, we add to the score.
    # If the word in pattern does not match an entire word but matches the first letter of a word,
    # we score it too but not as much as we would if it would match the entire word.
    # By default repeated occurrences of pattern in string are not scored. 
    # We don't want "dddd" to score more than "d" when pattern is "d". todo: Have to be careful with this
    # "occurrences" might be a problem we want to avoid and will probably be dropped in the future
    
    # default scores:
    __scores = {'full_string':  5,
                'word':         4,
                'word_place':   3,
                'start_word':   2,
                'occurrences':  0
                }
    
    
    __word_separator=None
    
    __line_words=''
    __pattern_words=''
    __pattern=''
    
    # todo: build proper debug code for testing scores
    debug=False


    def __init__(self,pattern,word_separator=None):
        self.set_pattern(pattern)
        self.__word_separator = word_separator
        
    def set_scores(self,full_string_match,word_match,well_placed_word_match,well_placed_startofword_match,occurrences):
        self.__scores['full_string'] = full_string_match
        self.__scores['word'] = word_match
        self.__scores['word_place'] = well_placed_word_match
        self.__scores['start_word'] = well_placed_startofword_match
        self.__scores['occurrences'] = occurrences
            
    def set_pattern(self,pattern):
        self.__pattern = pattern
        self.__pattern_words = self.__split_words(pattern)

    def __split_words(self,line):
        #return line.split(word_separator)
        # todo: to use or not use __word_separator ?
        return re.findall(r'\w+',line)

    def score_lines(self,lines,sort=True,descending=True):
        scored_lines = []
        # score lines
        for line in lines:
            scored_lines[len(scored_lines):]=[(self.score_line(line),line)]
        
        # sort by score
        if sort: scored_lines.sort(reverse=descending)
        if self.debug:
            print "Calculated perfect score: "+str(self.__perfect_score())
        return scored_lines

    def score_line(self,line):
        score = 0
        pattern = self.__pattern
        
        if self.debug: print "line: "+line    
      
        if line == pattern: 
            score += self.__update_score("full_string", score, pattern)
            # TODO: return __perfect_score(self) without comparing the words
            # watch out for occurrences score! 
            
        score += self.__score_words(line)
        
        return score
    
    def __perfect_score(self):
        '''
        This should compute the score of a line that fully matches pattern
        '''
        word_count = len(self.__pattern_words)
        score = self.__scores["full_string"]
        score += self.__scores["word"] * word_count
        score += self.__scores["word_place"] * word_count
        return score
        
         
        
    def certainty(self,scored_lines):
        '''
        Experimental: how certain we are the highest scored line is really the best match 
        Their must be a better mathematical solution for this.
        This is a simple guess. 1-(high_score-perfect_score) / sum ( 1-(high_score-score(n) ) 
        '''
        total_lines=len(scored_lines)
        closenest_to_high_score=0
        if total_lines > 0:
            perfect_score = float(self.__perfect_score())
            scored_lines.sort(reverse=True)
            high_score = float(scored_lines[0][0])
            total_lines_with_high_score=0
            total_scores=0
            for line in scored_lines:
                if line[0] == high_score: total_lines_with_high_score += 1
                total_scores += float(line[0])
                closenest_to_high_score += 1-(high_score/perfect_score - line[0]/perfect_score)
            return (1-(high_score/perfect_score))/closenest_to_high_score
    
                
   
    def __score_words(self,line):
        score=0
        pattern_words = self.__pattern_words
        line_words = self.__split_words(line)
        
        # for each word in line...
        for li in range(0,len(line_words)):
            word = line_words[li]
            
            # compare with each word in pattern
            for pi in range(0,len(pattern_words)):
                pword = pattern_words[pi]
                if word == pword: # word matches: score word presence
                    score = self.__update_score("word",score,pword)
                    
                    if li == pi: # word in the same order/index, add to score
                        score = self.__update_score("word_place", score, pword)
                else: # word does not fully match, will search sub strings of word
                      # todo: review this. The "occurrences" problem.
                    start = 0
                    regexp = re.compile(pword)
                    while True:
                        m = regexp.search(word, start)
                        if m is None:
                            break
                        if m.start() == 0: # word in pattern matches start of word in line
                            score = self.__update_score("start_word",score,pword)
                            if li == pi:
                                score = self.__update_score("word_place",score,pword)    
                        score = self.__update_score("occurrences",score,word[start:len(pword)])
                        start = 1 + m.start()
                    
        return score        
        
    def __update_score(self,name,score,match=''):
        if name in self.__scores:
            score += self.__scores[name]
            if self.debug: print name+": "+str(self.__scores[name])+" -> "+str(score)+ " (" + match + ")"
        else:
            if self.debug: print "Unknown score: "+name
        return score  
            
 
