from django import template


register = template.Library()

@register.filter
def percentual(value, arg):
    """ Calcula percentual sobre valores """
    return (value / arg) * 100

@register.filter
def multiplicar(value, arg):
    """ Multiplicar valores """
    return value * arg

@register.filter
def subtrair(value, arg):
    """ Subtrair valores """
    return value - arg