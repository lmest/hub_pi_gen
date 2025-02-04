#!/bin/bash

# vermelho
pinctrl 18 op pn
pinctrl set 18 dh
sleep 0.2s

# amarelo
pinctrl 24 op pn
pinctrl set 24 dl
sleep 0.2s

# verde
pinctrl 12 op pn
pinctrl set 12 dl
sleep 0.2

    
