# Ratio Bug Fix

**Script Version:** 1.0  
**Flame Version:** 2024.2  
**Written by:** Bryan Bayley  
**Creation Date:** 02.14.24  

## Description

Segments with an Action timeline effect will not display the correct size/ratio. To fix this, we add a Source Color
Management timeline effect, and immediately remove it to get flame to recognize the correct resolution of the source footage.
