# coding: mixt
from mixt import html

def test():
    assert str(<Fragment><if cond="{True}">true</if><else>false</else></Fragment>) == "true"
    assert str(<Fragment><if cond="{False}">true</if><else>false</else></Fragment>) == "false"


def test2():
    assert str(<Fragment>
                   <if cond="{True}">true</if>
                   <else>false</else>
               </Fragment>) == "true"
    assert str(<Fragment>
                   <if cond="{False}">true</if>
                   <else>false</else>
               </Fragment>) == "false"


def test3():
    assert str(<Fragment>
                   <if cond="{True}">
                       <if cond="{True}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{True}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </Fragment>) == "one"

    assert str(<Fragment>
                   <if cond="{True}">
                       <if cond="{False}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{True}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </Fragment>) == "two"

    assert str(<Fragment>
                   <if cond="{False}">
                       <if cond="{False}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{True}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </Fragment>) == "three"

    assert str(<Fragment>
                   <if cond="{False}">
                       <if cond="{False}">
                           one
                       </if>
                       <else>
                           two
                       </else>
                   </if>
                   <else>
                       <if cond="{False}">
                           three
                       </if>
                       <else>
                           four
                       </else>
                   </else>
               </Fragment>) == "four"


def test4():
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
