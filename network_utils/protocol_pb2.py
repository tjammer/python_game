# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protocol.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='protocol.proto',
  package='mygame_protocol',
  serialized_pb='\n\x0eprotocol.proto\x12\x0fmygame_protocol\"\x84\x02\n\x07Message\x12*\n\x04type\x18\x01 \x02(\x0e\x32\x1c.mygame_protocol.MessageType\x12\'\n\x06player\x18\x02 \x01(\x0b\x32\x17.mygame_protocol.Player\x12%\n\x05input\x18\x03 \x01(\x0b\x32\x16.mygame_protocol.Input\x12/\n\nprojectile\x18\x04 \x01(\x0b\x32\x1b.mygame_protocol.Projectile\x12-\n\tgameState\x18\x07 \x01(\x0e\x32\x1a.mygame_protocol.GameState\x12\x0b\n\x03\x61\x63k\x18\x05 \x01(\x05\x12\x10\n\x08gameTime\x18\x06 \x01(\x02\"\xeb\x01\n\x06Player\x12\n\n\x02id\x18\x06 \x01(\x05\x12\x0c\n\x04posx\x18\x02 \x01(\x02\x12\x0c\n\x04posy\x18\x03 \x01(\x02\x12\x0c\n\x04velx\x18\x04 \x01(\x02\x12\x0c\n\x04vely\x18\x05 \x01(\x02\x12\'\n\x06mState\x18\x07 \x01(\x0b\x32\x17.mygame_protocol.MState\x12\n\n\x02hp\x18\x08 \x01(\x05\x12\r\n\x05\x61rmor\x18\t \x01(\x05\x12\x0c\n\x04time\x18\n \x01(\x04\x12\x0c\n\x04\x63hat\x18\x0b \x01(\t\x12\x0c\n\x04\x61mmo\x18\x0c \x01(\x05\x12/\n\x06weapon\x18\r \x01(\x0e\x32\x1f.mygame_protocol.ProjectileType\"\xbc\x01\n\x05Input\x12\x0c\n\x04time\x18\x01 \x01(\x04\x12\n\n\x02id\x18\x07 \x01(\x05\x12\r\n\x05right\x18\x02 \x01(\x08\x12\x0c\n\x04left\x18\x03 \x01(\x08\x12\n\n\x02up\x18\x04 \x01(\x08\x12\x0c\n\x04name\x18\x06 \x01(\t\x12\n\n\x02mx\x18\x08 \x01(\x02\x12\n\n\x02my\x18\t \x01(\x02\x12\x0b\n\x03\x61tt\x18\n \x01(\x08\x12\x0c\n\x04\x64own\x18\x0b \x01(\x08\x12/\n\x06switch\x18\x0c \x01(\x0e\x32\x1f.mygame_protocol.ProjectileType\"\xbc\x01\n\x06MState\x12\x10\n\x08onGround\x18\x01 \x01(\x08\x12\x11\n\tascending\x18\x02 \x01(\x08\x12\x0f\n\x07landing\x18\x03 \x01(\x08\x12\x0f\n\x07\x63\x61nJump\x18\x04 \x01(\x08\x12\x12\n\ndescending\x18\x05 \x01(\x08\x12\x10\n\x08isFiring\x18\x06 \x01(\x08\x12\x13\n\x0bonRightWall\x18\x07 \x01(\x08\x12\x12\n\nonLeftWall\x18\x08 \x01(\x08\x12\x0e\n\x06isDead\x18\t \x01(\x08\x12\x0c\n\x04hold\x18\n \x01(\x08\"\xb6\x01\n\nProjectile\x12-\n\x04type\x18\x01 \x02(\x0e\x32\x1f.mygame_protocol.ProjectileType\x12\x10\n\x08playerId\x18\x02 \x01(\x05\x12\x0e\n\x06projId\x18\x03 \x01(\x05\x12\x0c\n\x04posx\x18\x04 \x01(\x02\x12\x0c\n\x04posy\x18\x05 \x01(\x02\x12\x0c\n\x04velx\x18\x06 \x01(\x02\x12\x0c\n\x04vely\x18\x07 \x01(\x02\x12\x10\n\x08toDelete\x18\x08 \x01(\x08\x12\r\n\x05\x61ngle\x18\t \x01(\x02*\xb8\x01\n\x0bMessageType\x12\x10\n\x0cplayerUpdate\x10\x00\x12\r\n\tnewPlayer\x10\x01\x12\x0e\n\ndisconnect\x10\x02\x12\x08\n\x04\x63hat\x10\x03\x12\r\n\tmapUpdate\x10\x04\x12\x0e\n\nprojectile\x10\x05\x12\x0f\n\x0bstateUpdate\x10\x06\x12\x0f\n\x0b\x61\x63kResponse\x10\t\x12\t\n\x05input\x10\x07\x12\r\n\tmapChange\x10\x08\x12\x13\n\x0f\x63onnectResponse\x10\n*n\n\x0eProjectileType\x12\r\n\tno_switch\x10\x00\x12\t\n\x05melee\x10\x01\x12\x0b\n\x07\x62laster\x10\x04\x12\x0f\n\x0b\x65xplBlaster\x10\x0b\x12\x06\n\x02lg\x10\x03\x12\x06\n\x02sg\x10\x02\x12\x06\n\x02gl\x10\x05\x12\x0c\n\x08\x65xplNade\x10\x0c*\x94\x01\n\tGameState\x12\n\n\x06warmUp\x10\x00\x12\x0e\n\ninProgress\x10\x01\x12\n\n\x06isDead\x10\x02\x12\n\n\x06spawns\x10\x03\x12\x0b\n\x07isReady\x10\x04\x12\x0c\n\x08goesSpec\x10\x05\x12\r\n\twantsJoin\x10\x06\x12\r\n\tcountDown\x10\x07\x12\x0c\n\x08gameOver\x10\x08\x12\x0c\n\x08overTime\x10\t')

_MESSAGETYPE = _descriptor.EnumDescriptor(
  name='MessageType',
  full_name='mygame_protocol.MessageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='playerUpdate', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='newPlayer', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='disconnect', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='chat', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='mapUpdate', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='projectile', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='stateUpdate', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ackResponse', index=7, number=9,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='input', index=8, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='mapChange', index=9, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='connectResponse', index=10, number=10,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1104,
  serialized_end=1288,
)

MessageType = enum_type_wrapper.EnumTypeWrapper(_MESSAGETYPE)
_PROJECTILETYPE = _descriptor.EnumDescriptor(
  name='ProjectileType',
  full_name='mygame_protocol.ProjectileType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='no_switch', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='melee', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='blaster', index=2, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='explBlaster', index=3, number=11,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='lg', index=4, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='sg', index=5, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='gl', index=6, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='explNade', index=7, number=12,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1290,
  serialized_end=1400,
)

ProjectileType = enum_type_wrapper.EnumTypeWrapper(_PROJECTILETYPE)
_GAMESTATE = _descriptor.EnumDescriptor(
  name='GameState',
  full_name='mygame_protocol.GameState',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='warmUp', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='inProgress', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='isDead', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='spawns', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='isReady', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='goesSpec', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='wantsJoin', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='countDown', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='gameOver', index=8, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='overTime', index=9, number=9,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1403,
  serialized_end=1551,
)

GameState = enum_type_wrapper.EnumTypeWrapper(_GAMESTATE)
playerUpdate = 0
newPlayer = 1
disconnect = 2
chat = 3
mapUpdate = 4
projectile = 5
stateUpdate = 6
ackResponse = 9
input = 7
mapChange = 8
connectResponse = 10
no_switch = 0
melee = 1
blaster = 4
explBlaster = 11
lg = 3
sg = 2
gl = 5
explNade = 12
warmUp = 0
inProgress = 1
isDead = 2
spawns = 3
isReady = 4
goesSpec = 5
wantsJoin = 6
countDown = 7
gameOver = 8
overTime = 9



_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='mygame_protocol.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='mygame_protocol.Message.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='player', full_name='mygame_protocol.Message.player', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='input', full_name='mygame_protocol.Message.input', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='projectile', full_name='mygame_protocol.Message.projectile', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gameState', full_name='mygame_protocol.Message.gameState', index=4,
      number=7, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ack', full_name='mygame_protocol.Message.ack', index=5,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gameTime', full_name='mygame_protocol.Message.gameTime', index=6,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=36,
  serialized_end=296,
)


_PLAYER = _descriptor.Descriptor(
  name='Player',
  full_name='mygame_protocol.Player',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='mygame_protocol.Player.id', index=0,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='posx', full_name='mygame_protocol.Player.posx', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='posy', full_name='mygame_protocol.Player.posy', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='velx', full_name='mygame_protocol.Player.velx', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='vely', full_name='mygame_protocol.Player.vely', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mState', full_name='mygame_protocol.Player.mState', index=5,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='hp', full_name='mygame_protocol.Player.hp', index=6,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='armor', full_name='mygame_protocol.Player.armor', index=7,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='time', full_name='mygame_protocol.Player.time', index=8,
      number=10, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='chat', full_name='mygame_protocol.Player.chat', index=9,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ammo', full_name='mygame_protocol.Player.ammo', index=10,
      number=12, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='weapon', full_name='mygame_protocol.Player.weapon', index=11,
      number=13, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=299,
  serialized_end=534,
)


_INPUT = _descriptor.Descriptor(
  name='Input',
  full_name='mygame_protocol.Input',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='time', full_name='mygame_protocol.Input.time', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='mygame_protocol.Input.id', index=1,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='right', full_name='mygame_protocol.Input.right', index=2,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='left', full_name='mygame_protocol.Input.left', index=3,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='up', full_name='mygame_protocol.Input.up', index=4,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='mygame_protocol.Input.name', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mx', full_name='mygame_protocol.Input.mx', index=6,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='my', full_name='mygame_protocol.Input.my', index=7,
      number=9, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='att', full_name='mygame_protocol.Input.att', index=8,
      number=10, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='down', full_name='mygame_protocol.Input.down', index=9,
      number=11, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='switch', full_name='mygame_protocol.Input.switch', index=10,
      number=12, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=537,
  serialized_end=725,
)


_MSTATE = _descriptor.Descriptor(
  name='MState',
  full_name='mygame_protocol.MState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='onGround', full_name='mygame_protocol.MState.onGround', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ascending', full_name='mygame_protocol.MState.ascending', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='landing', full_name='mygame_protocol.MState.landing', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='canJump', full_name='mygame_protocol.MState.canJump', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='descending', full_name='mygame_protocol.MState.descending', index=4,
      number=5, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isFiring', full_name='mygame_protocol.MState.isFiring', index=5,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='onRightWall', full_name='mygame_protocol.MState.onRightWall', index=6,
      number=7, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='onLeftWall', full_name='mygame_protocol.MState.onLeftWall', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isDead', full_name='mygame_protocol.MState.isDead', index=8,
      number=9, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='hold', full_name='mygame_protocol.MState.hold', index=9,
      number=10, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=728,
  serialized_end=916,
)


_PROJECTILE = _descriptor.Descriptor(
  name='Projectile',
  full_name='mygame_protocol.Projectile',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='mygame_protocol.Projectile.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='playerId', full_name='mygame_protocol.Projectile.playerId', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='projId', full_name='mygame_protocol.Projectile.projId', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='posx', full_name='mygame_protocol.Projectile.posx', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='posy', full_name='mygame_protocol.Projectile.posy', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='velx', full_name='mygame_protocol.Projectile.velx', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='vely', full_name='mygame_protocol.Projectile.vely', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='toDelete', full_name='mygame_protocol.Projectile.toDelete', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='angle', full_name='mygame_protocol.Projectile.angle', index=8,
      number=9, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=919,
  serialized_end=1101,
)

_MESSAGE.fields_by_name['type'].enum_type = _MESSAGETYPE
_MESSAGE.fields_by_name['player'].message_type = _PLAYER
_MESSAGE.fields_by_name['input'].message_type = _INPUT
_MESSAGE.fields_by_name['projectile'].message_type = _PROJECTILE
_MESSAGE.fields_by_name['gameState'].enum_type = _GAMESTATE
_PLAYER.fields_by_name['mState'].message_type = _MSTATE
_PLAYER.fields_by_name['weapon'].enum_type = _PROJECTILETYPE
_INPUT.fields_by_name['switch'].enum_type = _PROJECTILETYPE
_PROJECTILE.fields_by_name['type'].enum_type = _PROJECTILETYPE
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['Player'] = _PLAYER
DESCRIPTOR.message_types_by_name['Input'] = _INPUT
DESCRIPTOR.message_types_by_name['MState'] = _MSTATE
DESCRIPTOR.message_types_by_name['Projectile'] = _PROJECTILE

class Message(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _MESSAGE

  # @@protoc_insertion_point(class_scope:mygame_protocol.Message)

class Player(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PLAYER

  # @@protoc_insertion_point(class_scope:mygame_protocol.Player)

class Input(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _INPUT

  # @@protoc_insertion_point(class_scope:mygame_protocol.Input)

class MState(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _MSTATE

  # @@protoc_insertion_point(class_scope:mygame_protocol.MState)

class Projectile(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _PROJECTILE

  # @@protoc_insertion_point(class_scope:mygame_protocol.Projectile)


# @@protoc_insertion_point(module_scope)
