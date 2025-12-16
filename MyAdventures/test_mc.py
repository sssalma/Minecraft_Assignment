from mcpi.minecraft import Minecraft
import mcpi.block as block


mc = Minecraft.create()

mc.postToChat("¡Hola! Sistema TAP iniciado correctamente.")

pos = mc.player.getTilePos()
mc.player.setTilePos(pos.x, pos.y + 10, pos.z)
mc.postToChat("¡Te he hecho saltar!")