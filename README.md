# gimx-ps4
Code to pass ps4 controller input through to running gimx server for ps4 in python. This is messy code, read at your own risk!.

## Some steps and requirements:
- You need two PS4 controllers plugged into computer (one for gimx PS4 handshake, one for the gamepy input)
- You need GIMX-launcher installed.
- Run GIMX-launcher with settings:
-- Output: GIMX adapter
-- Port: ttylUSB0 (only option for me)
-- Input: Network
-- IP:port: 127.0.0.1:51914
-- Messages: text 
- pygame installation

```
cd path/to/gimx-ps4
pip install pygame
python gimx_ps4_passthrough.py
```
