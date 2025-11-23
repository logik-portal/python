# connect crypto

**Script Version:** 0.5  
**Flame Version:** 2021  
**Written by:** Kyle Obley (info@kyleobley.com)  
**Creation Date:** 07.05.23  
**Update Date:** 02.26.24  

## Description

Creates and connects a Cryptomatte node to a read file node if it's a cryptomatte.

## Updates

v0.5: Completely changed logic to use node.output_sockets which removes the need to try channels, etc.
- This hopefully makes the script bulletproof.
<br>
- v0.4: Added support for channels coming out without the filename within the channel itself.
<br>
- v0.3: Added support for Houdini's Object ID naming
<br>
- v0.2: Added logic for different channel names and support for CryptoMesh
<br>
- v0.1: Initial Release
