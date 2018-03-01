import time

import core.geo_coll as geo_coll
import core.flavor_coll as flavor_coll
import core.shop_coll as shop_coll
import core.food_coll as food_coll
import core.concept_coll as concept_coll

if __name__ == '__main__':
    start_time = time.time()
    geo_coll.main()
    flavor_coll.main()
    concept_coll.main()
    shop_coll.main()
    food_coll.main()
    end_time = time.time()
    print(end_time - start_time)
