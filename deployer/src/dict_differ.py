class DictDiffer:
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        keys = set()
        changed_attributes = {}
        for config in self.intersect:
            for o in self.current_dict[config]:
                if o not in self.past_dict[config] or self.current_dict[config][o] != self.past_dict[config][o]:
                    keys.add(config)
                    if config not in changed_attributes:
                        changed_attributes[config] = []
                    changed_attributes[config].append(o)

            for o in self.past_dict[config]:
                if o not in self.current_dict[config] and 'docker' not in o:
                    keys.add(config)
                    if config not in changed_attributes:
                        changed_attributes[config] = []
                    changed_attributes[config].append(o)

        return keys, changed_attributes
