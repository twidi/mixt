# coding: mixt
from mixt.pyxl import html

def test():
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
