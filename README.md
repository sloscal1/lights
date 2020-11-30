# Lights
The current light interface consists of an Arduino Server
that accepts light messages in a particular format, and
a Java program that sends the messages and plays music.

This controller is a little different. It's going to be a
manually controlled set of lights.

To get this to work:
1. Need to get a single key to trigger a light
message to the tree.
2. Need to record the timing of the keys.
3. Need to assign the lights to bands.
4. Need to send the stored timing to lights on time.