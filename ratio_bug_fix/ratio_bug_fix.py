'''
Script Name: Ratio Bug Fix
Script Version: 1.0
Flame Version: 2024.2
Written by: Bryan Bayley
Creation Date: 02.14.24

Description: There is a bug when conforming an AAF/XML with footage at a different resolution than the offline edit. 
Segments with an Action timeline effect will not display the correct size/ratio. To fix this, we add a Source Color 
Management timeline effect, and immediately remove it to get flame to recognize the correct resolution of the source footage.
'''

import flame

def ratio_bug_fix(selection):
    for item in selection:
        item.create_effect('Source Colour Mgmt')
        flame.delete(item.effects[0])

def get_timeline_custom_ui_actions():

    def scope_seq(selection):
        for item in selection:
            if isinstance(item, flame.PySegment):
                return True
        return False

    return [
        {
            'name': 'Segment...',
            'actions': [
                {
                    'name': 'Ratio Bug Fix',
                    'isVisible': scope_seq,
                    'execute': ratio_bug_fix,
                    'minimumVersion': '2020'
                }
            ]
        }
    ]
