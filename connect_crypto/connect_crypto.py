"""
Script Name: Connect Cryptomatte
Script Version: 0.5
Flame Version: 2021

Creation date: 07.05.23
Modified date: 02.26.24

Author: Kyle Obley (info@kyleobley.com)

Description:

    Creates and connects a Cryptomatte node to a read file node if it's a cryptomatte.

Change Log:

    v0.5: Completely changed logic to use node.output_sockets which removes the need to try channels, etc.
          This hopefully makes the script bulletproof.

    v0.4: Added support for channels coming out without the filename within the channel itself.

    v0.3: Added support for Houdini's Object ID naming

    v0.2: Added logic for different channel names and support for CryptoMesh

    v0.1: Initial Release

"""

def connect_crypto(selection):
    import flame

    debug = False

    # Define channels
    crypto_channels = ['00','01','02']

    for clip in selection:

        # Get the name of the cryptomatte
        crypto_source = clip
        crypto_source_name = crypto_source.name.get_value()

        # Create the node
        crypto_node = flame.batch.create_node("Cryptomatte")
        crypto_node.pos_x = crypto_source.pos_x + 300
        crypto_node.pos_y = crypto_source.pos_y

        if debug:
            print ("Crypto Source: ", crypto_source_name)
            print ("Sockets:       ", crypto_source.output_sockets)

        primary_channel = crypto_source.output_sockets[0]
        flame.batch.connect_nodes(crypto_source, primary_channel, crypto_node, "Front")

        # Connect all the other channels
        # Loop through the other 3 channels and connect
        for i in crypto_channels:
            material_rgb = primary_channel + i
            material_alpha = primary_channel + i + "_alpha"
            socket_rgb = "uCrypto" + i + "rgb"
            socket_alpha = "uCrypto" + i + "a"

            flame.batch.connect_nodes(crypto_source, material_rgb, crypto_node, socket_rgb)
            flame.batch.connect_nodes(crypto_source, material_alpha, crypto_node, socket_alpha)


# Scope for crypto only
def scope_crypto(selection):
    import flame
    for item in selection:
        if isinstance(item, flame.PyNode):
            if 'crypto' in item.name.get_value():
                return True


def get_batch_custom_ui_actions():
    return [
          {
                "name": "Cryptomatte",
                "actions": [
                     {
                          "name": "Connect Cryptomatte",
                          "isVisible": scope_crypto,
                          "execute": connect_crypto
                     }
                ]
          }
     ]
