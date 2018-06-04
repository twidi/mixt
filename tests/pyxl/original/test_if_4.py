# coding: mixt
from mixt import html

def test():
    count = [0]
    def foo(value):
        count[0] += 1
        return value
    assert str(<Fragment>
                   <if cond="{foo(True)}">a</if>
                   <else>b</else>
                   {count[0]}
               </Fragment>) == "a1"

    count[0] = 0
    assert str(<Fragment>
                   <if cond="{foo(False)}">a</if>
                   <else>b</else>
                   {count[0]}
               </Fragment>) == "b1"
