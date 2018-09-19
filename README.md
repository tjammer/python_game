# python_game
quake 2d platformer prototype

![gaem][screenshot]

## Working
- Client/Server based multiplayer with client side prediction
- Procedural Animation
- Quake style items (Weapons, Armors, Pickups, Teleporters)

## Compiled Objects
Some parts of the game (vectors, quaternions, collision detection) require compiled Cython module. They can be compiled with
```python
python build_libs.py build_ext --inplace
```

[screenshot]: screenshot.png
