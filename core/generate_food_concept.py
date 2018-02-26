from core.db_engine import dbsession, FoodConcept


if __name__ == '__main__':
    with open('/home/liuzhf/workspace/projects/ELS/dependence/food_concept', 'r') as f:
        for l in f.readlines():
            l = l.strip()
            key_words = l.split(',')
            concept_name = key_words[0].strip()
            dbsession.add(FoodConcept(
                name=concept_name,
                key_words=l,
            ))
        dbsession.commit()
