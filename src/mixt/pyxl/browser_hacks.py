#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from .base import Base
from .utils import escape

class ConditionalComment(Base):
    class PropTypes:
        cond: str

    def _to_list(self, l):
        # allow '&', escape everything else from cond
        cond = self.__props__.get('cond', '')
        cond = '&'.join(map(escape, cond.split('&')))

        l.extend(('<!--[if ', cond, ']>'))
        self._render_children_to_list(l)
        l.append('<![endif]-->')

class ConditionalNonComment(Base):
    ''' This is a conditional comment where browsers which don't support conditional comments
        will parse the children by default. '''
    class PropTypes:
        cond: str

    def _to_list(self, l):
        # allow '&', escape everything else from cond
        cond = self.__props__.get('cond', '')
        cond = '&'.join(map(escape, cond.split('&')))

        l.extend(('<!--[if ', cond, ']><!-->'))
        self._render_children_to_list(l)
        l.append('<!--<![endif]-->')

