
from collections import namedtuple

WidgetInfo = namedtuple('WidgetInfo', 'name label width show_column column_width', defaults=[False, 20])
WidgetInfoAdv = namedtuple('WidgetInfo', 'name label width show_column column_width', defaults=[False, 20])


LocationSample = {'state': WidgetInfo('STATE', 'State', 20, True, 200),
                  'city': WidgetInfo(name='CITY', label='City', width=20, show_column=True, column_width=20),
                  'zipcode': WidgetInfo('ZIP', 'Zip', 20, True, 200),
                  'description': WidgetInfo('DESCRIPTION', 'Description', 20)}

PrimaryDefinition = (WidgetInfo('COLOR', 'Color', 10, True, 200),
                     WidgetInfo('SHAPE', 'Shape', 10, True, 200),
                     WidgetInfo('SIZE', 'Size', 20, True, 200),
                     WidgetInfo('PLACE', 'Place', 20, True, 200),
                     WidgetInfo('NUMBER', 'Number', 10, True, 300),
                     WidgetInfo('OTHER', 'Other Information', 30))


def main(definition):
    for t in definition:
        print(f'The entry widget name is {t.name} and will have a label of {t.label} with a width of {t.width}\nThe column will show: {t.show_column} and its width will be {t.column_width}')

    c = [w for w in definition if w.show_column is True]
    print(c)
    c = [w for w in definition if w.show_column is False]
    print(c)

    

if __name__ == '__main__':
    main(LocationSample.values())