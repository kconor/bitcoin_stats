"""
Taken from
https://github.com/bitcoin-abe/bitcoin-abe
"""

import struct
from opcodes import opcodes


def script_GetOp(bytes):
  i = 0
  while i < len(bytes):
    vch = None
    opcode = ord(bytes[i])
    i += 1

    if opcode <= opcodes.OP_PUSHDATA4:
      nSize = opcode
      if opcode == opcodes.OP_PUSHDATA1:
        if i + 1 > len(bytes):
          vch = "_INVALID_NULL"
          i = len(bytes)
        else:
          nSize = ord(bytes[i])
          i += 1
      elif opcode == opcodes.OP_PUSHDATA2:
        if i + 2 > len(bytes):
          vch = "_INVALID_NULL"
          i = len(bytes)
        else:
          (nSize,) = struct.unpack_from('<H', bytes, i)
          i += 2
      elif opcode == opcodes.OP_PUSHDATA4:
        if i + 4 > len(bytes):
          vch = "_INVALID_NULL"
          i = len(bytes)
        else:
          (nSize,) = struct.unpack_from('<I', bytes, i)
          i += 4
      if i+nSize > len(bytes):
        vch = "_INVALID_"+bytes[i:]
        i = len(bytes)
      else:
        vch = bytes[i:i+nSize]
        i += nSize

    yield (opcode, vch, i)

def script_GetOpName(opcode):
  try:
    return (opcodes.whatis(opcode)).replace("OP_", "")
  except KeyError:
    return "InvalidOp_"+str(opcode)

def decode_script(bytes):
  result = ''
  for (opcode, vch, i) in script_GetOp(bytes):
    if len(result) > 0: result += " "
    if opcode <= opcodes.OP_PUSHDATA4:
      result += "OP_PUSHDATA"
    else:
      result += script_GetOpName(opcode)
  return result

