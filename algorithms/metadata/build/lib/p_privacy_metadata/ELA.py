
class ELA():
    '''
       Process Mining Abstraction Object
    '''
    origin = None
    method = None
    desired_analyses = None
    data = None

    def __init__(self):
        self = self

    def set_values(self, **keyparam):
        attributes = ['origin', 'method', 'desired_analyses', 'data']
        if 'origin' in keyparam.keys():
            self.origin = keyparam['origin']
        if 'method' in keyparam.keys():
            self.method = keyparam['method']
        if 'desired_analyses' in keyparam.keys():
            self.desired_analyses = keyparam['desired_analyses']
        if 'data' in keyparam.keys():
            self.data = keyparam['data']

    def func_xml(self, row, row_name):
        xml = [f'        <item name="{row_name}">']
        for field in row.index:
            xml.append('          <field name="{0}">{1}</field>'.format(field, row[field]))
        xml.append('        </item>')
        return '\n'.join(xml)

    def func_xml_dict(self, dict, wrapper):
        xml = ['        <' + wrapper + '>']
        for key in dict.keys():
            xml.append('          <field name="{0}">{1}</field>'.format(key, dict[key]))
        xml.append('        </' + wrapper + '>')
        return '\n'.join(xml)

    def get_values(self):
        return {'origin': self.origin, 'method':self.method, 'desired_analyses':self.desired_analyses, 'data':self.data}

    def create_xml(self, filename):
        desired_analyses_dict = {i + 1: self.desired_analyses[i] for i in range(0, len(self.desired_analyses))}

        analyses_xml = self.func_xml_dict(desired_analyses_dict, "desired_analyses")

        xml = ['<?xml version="1.0" encoding="UTF-8" ?>']
        xml.append('<ELA>')
        xml.append('    <header>')
        xml.append(f'       <origin>{self.origin}</origin>')
        xml.append(f'       <method>{self.method}</method>')
        xml.append(analyses_xml)
        xml.append('    </header>')
        xml.append('    <data>')
        # xml.append('\n'.join(df.apply(func_xml, axis=1)))
        for index, item in self.data.iterrows():
            xml.append(self.func_xml(item, str(index)))
        xml.append('    </data>')
        xml.append('</ELA>')
        xml_content = '\n'.join(xml)

        f = open(filename, "w")
        f.write(xml_content)
        f.close()

    def read_xml(self, filename):
        ela ={}
        data = []
        import xml.etree.ElementTree as ET
        root = ET.parse(filename).getroot()
        for child in root:
            for subchild in child:
                if(subchild.tag == 'desired_analyses'):
                    analyses = {}
                    for analysis in subchild:
                        analyses[analysis.attrib['name']] = analysis.text
                    ela[subchild.tag] = analyses
                elif (subchild.tag == 'item'):
                    item_dict ={}
                    items = {}
                    for field in subchild:
                        item_dict[field.attrib['name']] = field.text
                    # items[subchild.attrib['name']] = item_dict
                    # data.append(items)
                    data.append(item_dict)
                else:
                    ela[subchild.tag] = subchild.text
        ela['data'] = data
        return ela

#Usage--------------------

# import pandas as pd
# pmo = ELA()
# data = {'Name': ['Tom', 'nick', 'krish', 'jack'], 'Age': [20, 21, 19, 18]}
# df = pd.DataFrame(data)
# pmo.set_values(origin = 'Majid', method = 'test_method', desired_analyses = ['discovery', 'social'].copy(), data = df.copy())
# pmo.create_xml("test.xml")
# print(pmo.get_values()['data'])
#
# ela = pmo.read_xml("test.xml")
# print(ela)
# print("done!")
