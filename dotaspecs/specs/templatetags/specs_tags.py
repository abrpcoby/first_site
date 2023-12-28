from django import template
from django.db.models import Count
from taggit.models import Tag

from specs.models import *

register = template.Library()


@register.simple_tag(name="getcats")
def get_categories():
    # cats_list = Category.objects.annotate(num_times=Count('specs')).order_by('-num_times')
    # categories = list(cats_list.values('name', 'num_times', 'slug'))

    # categories = Category.objects.all().order_by('name')
    categories = Category.objects.annotate(num_times=Count('specs')).order_by('-num_times')
    return categories


@register.inclusion_tag('specs/list_categories.html')
def show_categories(cat_selected=0):
    cats = Category.objects.all()
    return {"cats": cats, "cat_selected": cat_selected}


@register.simple_tag
def all_tags():
    tags = Tag.objects.annotate(num_times=Count('specs')).order_by('-num_times')
    tag_list = list(tags.values('name', 'num_times', 'slug'))
    return tag_list
