class privacyExtension():

    def __init__(self, log, prefix, uri):
        self.log = log
        self.prefix = prefix
        self.uri = uri


    def set_anonymizer(self, operation, level, target):

        layer = self.get_last_layer()

        if(layer is None):
            layer = 1
            self.log.extensions['Privacy'] = {'prefix': self.prefix[:-1], 'uri': self.uri}
            privacyanonymizer = {}
        else:
            layer += 1
            privacyanonymizer = self.log.attributes[self.prefix+'anonymizations']

        anonymizer = {}
        # anonymizer[self.prefix + 'layer'] = layer
        anonymizer[self.prefix + 'operation type'] = operation    #'substitution'
        anonymizer[self.prefix + 'level'] = level   #'event'
        anonymizer[self.prefix + 'target'] = target      #'concept:name'

        if(layer == 1):
            privacyanonymizer[self.prefix+'anonymizer'+str(layer)] = {"value": None, "children": anonymizer}
            self.log.attributes[self.prefix+'anonymizations'] = {"value": None, "children": privacyanonymizer}
        else:
            privacyanonymizer['children'][self.prefix+'anonymizer'+str(layer)]= {"value": None, "children": anonymizer}


    def set_optional_anonymizer(self, layer, **keyparam):
        if (keyparam != {}):
            current_layer = self.get_last_layer()
            if(current_layer == None or current_layer < layer):
                return "The layer does not exist!"
            privacyanonymizer = self.log.attributes[self.prefix + 'anonymizations']
            for key,value in keyparam.items():
                if type(value) is dict:
                    privacyanonymizer['children'][self.prefix+'anonymizer' + str(layer)]['children'][key] = {"value": None, "children": value}
                else:
                    privacyanonymizer['children'][self.prefix + 'anonymizer' + str(layer)]['children'][key] = value
            return "The parameters have been added."
        else:
            return "No parameter has been passed!"

    def get_last_layer(self):
        try:
            layer = len(self.log.attributes[self.prefix+'anonymizations']['children'])
            return layer
        except Exception as e:
            return None

    def get_anonymizer(self,layer):
        return self.log.attributes[self.prefix + 'anonymizations']['children'][self.prefix+'anonymizer' + str(layer)]['children']

    def get_anonymizations(self):
        return self.log.attributes[self.prefix + 'anonymizations']['children']
