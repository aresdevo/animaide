# licence
'''
Copyright (C) 2018 Ares Deveaux


Created by Ares Deveaux

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from . import props, ops, ui
classes = props.classes + ops.classes # + ui.panel_classes + ui.header_classes

# if bpy.context.scene.animaide.key_tweak.panel_pref == 'PANEL':
#     classes = \
#         props.classes + \
#         ops.classes + \
#         ui.panel_classes
# else:
#     classes = \
#         props.classes + \
#         ops.classes + \
#         ui.header_classes

