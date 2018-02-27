from core.db_engine import dbsession, FoodConcept

CONCEPT_PATH = '../dependence/food_concept'

if __name__ == '__main__':
    with open(CONCEPT_PATH, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            key_words = l.split(',')
            concept_name = key_words[0].strip()
            dbsession.add(FoodConcept(
                name=concept_name,
                key_words=l,
            ))
        dbsession.commit()
        dbsession.close()
