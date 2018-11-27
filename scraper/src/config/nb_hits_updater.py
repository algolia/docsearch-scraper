from ..helpers import confirm
import json
import copy


class NbHitsUpdater(object):
    new_nb_hit = None
    previous_nb_hits = None
    config_file = None
    config_content = None

    def __init__(self, config_file, config_content, previous_nb_hits,
                 new_nb_hit):
        self.config_file = config_file
        self.config_content = copy.deepcopy(config_content)
        self.new_nb_hit = new_nb_hit
        self.previous_nb_hits = previous_nb_hits

    def update(self):
        if self._update_needed():
            print("previous nb_hits: " + str(self.previous_nb_hits) + "\n")

            if confirm(
                                    'Do you want to update the nb_hits in ' + self.config_file + ' ?'):
                try:
                    self._update_config()
                    print("\n[OK] " + self.config_file + " has been updated")
                except Exception:
                    print(
                        "\n[KO] " + "Was not able to update " + self.config_file)

    def _update_needed(self):
        return self.previous_nb_hits is None or self.previous_nb_hits != self.new_nb_hit

    def _update_config(self):
        self.config_content['nb_hits'] = self.new_nb_hit
        with open(self.config_file, 'w') as f:
            f.write(json.dumps(self.config_content, indent=2,
                               separators=(',', ': ')))
