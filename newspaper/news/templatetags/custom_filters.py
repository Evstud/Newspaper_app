from django import template

register = template.Library()

@register.filter(name='Censor')
def Censor(input_text):
    bad_words = ['практически', 'научились']
    if isinstance(input_text, str):
        a = input_text.split()
        for i in a:
            if i in bad_words:
                a.remove(i)
        return ' '.join(a)
    else:
        raise ValueError(f'{input_text} не является строкой или текстом')

@register.filter(name='update_page')
def update_page(full_path:str, page:int):
    try:
        params_list = full_path.split('?')[1].split('&')
        params = dict([tuple(str(param).split('=')) for param in params_list])
        params.update({'page': page})
        link = ''
        for key, value in params.items():
            link += (f"{key}={value}&")
        return link[:-1]
    except:
        return f"page={page}"