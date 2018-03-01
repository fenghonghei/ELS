import json
from core.db_engine import dbsession, Flavor

FLAVOR_FILE_PATH = '../dependence/flavors'


class FlavorItem:
    def __init__(self, id, name, level, parent_id):
        self.id = id
        self.name = name
        self.level = level
        self.parent_id = parent_id


def get_flavors(flavor_category, parent_id):
    flavors = [FlavorItem(flavor_category['id'], flavor_category['name'], flavor_category['level'], parent_id)] if '全部' not in flavor_category['name'] else []
    if 'sub_categories' in flavor_category:
        for fc in flavor_category['sub_categories']:
            flavors.extend(get_flavors(fc, flavor_category['id']))
    return flavors


def main():
    with open(FLAVOR_FILE_PATH, 'r') as f:
        flavors_json = json.loads(f.read())
        flavors = []
        for flavor_category in flavors_json:
            if flavor_category['name'] == '全部商家':
                continue
            else:
                flavors.extend(get_flavors(flavor_category, None))
        flavors = list(sorted(flavors, key=lambda fl: fl.id))
        flavors = [Flavor(
                id=flavor.id,
                name=flavor.name,
                level=flavor.level,
                parent_id=flavor.parent_id
            ) for flavor in flavors]
        dbsession.add_all(flavors)
        dbsession.commit()
